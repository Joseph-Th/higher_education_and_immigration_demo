"""Build a reviewer-visible release and source-freshness monitoring artifact.

The live NCES request stays outside the offline validation lane. This builder
consumes the last explicitly captured release-monitor snapshot plus maintained
source-review metadata and turns them into a deterministic monitoring register.
"""

from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT_PATH = DATA / "release_monitor_snapshot.json"
DIRECTORY_PREFLIGHT_PATH = DATA / "candidate_directory_preflight.json"
CSV_OUTPUT = DATA / "freshness_monitor.csv"
DOC_OUTPUT = ROOT / "docs" / "FRESHNESS_MONITOR.md"
HTML_OUTPUT = ROOT / "site" / "freshness-monitor.html"

FIELDS = (
    "monitor_id",
    "monitor_area",
    "subject",
    "observed_date",
    "status",
    "evidence",
    "trigger",
    "next_action",
    "authority",
)


@dataclass(frozen=True)
class MonitorRow:
    monitor_id: str
    monitor_area: str
    subject: str
    observed_date: str
    status: str
    evidence: str
    trigger: str
    next_action: str
    authority: str

    def as_row(self) -> dict[str, str]:
        return {field: str(getattr(self, field)) for field in FIELDS}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_snapshot() -> dict[str, object]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    required = {
        "checked_at_utc",
        "current_analysis_end_year",
        "candidate_next_year",
        "fall_enrollment_ready",
        "directory_ready",
        "package_ready",
        "release_decision",
        "files",
    }
    missing = required - snapshot.keys()
    if missing:
        raise RuntimeError(f"Release-monitor snapshot missing fields: {sorted(missing)}")
    checked = datetime.fromisoformat(str(snapshot["checked_at_utc"]).replace("Z", "+00:00"))
    if checked.tzinfo is None:
        raise RuntimeError("Release-monitor checked_at_utc must be timezone-aware")
    files = snapshot["files"]
    if not isinstance(files, list) or len(files) != 4:
        raise RuntimeError("Release-monitor snapshot must contain exactly four candidate files")
    expected_year = int(snapshot["current_analysis_end_year"]) + 1
    if int(snapshot["candidate_next_year"]) != expected_year:
        raise RuntimeError("Release-monitor candidate year must equal current analysis year + 1")
    expected_names = {
        f"EF{expected_year}A.zip",
        f"EF{expected_year}A_Dict.zip",
        f"HD{expected_year}.zip",
        f"HD{expected_year}_Dict.zip",
    }
    names = {str(row.get("file", "")) for row in files}
    if names != expected_names:
        raise RuntimeError(f"Release-monitor file set mismatch: {sorted(names)}")
    derived_package_ready = all(bool(row.get("available")) for row in files)
    if bool(snapshot["package_ready"]) != derived_package_ready:
        raise RuntimeError("Release-monitor package_ready does not match file availability")
    expected_decision = "READY_FOR_SCHEMA_REVIEW" if derived_package_ready else "HOLD_YEAR_ADVANCE"
    if snapshot["release_decision"] != expected_decision:
        raise RuntimeError("Release-monitor decision does not match package readiness")
    return snapshot


def load_directory_preflight(snapshot: dict[str, object]) -> dict[str, object]:
    preflight = json.loads(DIRECTORY_PREFLIGHT_PATH.read_text(encoding="utf-8"))
    if int(preflight.get("current_analysis_end_year", -1)) != int(snapshot["current_analysis_end_year"]):
        raise RuntimeError("Directory preflight current year does not match release snapshot")
    if int(preflight.get("candidate_next_year", -1)) != int(snapshot["candidate_next_year"]):
        raise RuntimeError("Directory preflight candidate year does not match release snapshot")
    if str(preflight.get("release_monitor_checked_at_utc")) != str(snapshot["checked_at_utc"]):
        raise RuntimeError("Directory preflight was not captured against the current release snapshot")
    if preflight.get("release_monitor_decision") != snapshot["release_decision"]:
        raise RuntimeError("Directory preflight release decision is stale")
    if preflight.get("status") != "PASS" or preflight.get("year_advance_authorized") is not False:
        raise RuntimeError("Directory preflight must be PASS and must not authorize year advancement")
    if preflight.get("missing_required_data_fields") != [] or preflight.get("missing_required_dictionary_fields") != []:
        raise RuntimeError("Directory preflight required-field checks are not clean")
    if int(preflight.get("candidate_core_states_dc_count", 0)) != 51:
        raise RuntimeError("Directory preflight must cover all 50 states plus DC")
    if int(preflight.get("candidate_duplicate_unitid_count", -1)) != 0:
        raise RuntimeError("Directory preflight contains duplicate UNITIDs")
    return preflight


def build_rows() -> tuple[list[MonitorRow], dict[str, object]]:
    snapshot = load_snapshot()
    preflight = load_directory_preflight(snapshot)
    checked_date = str(snapshot["checked_at_utc"])[:10]
    candidate = int(snapshot["candidate_next_year"])
    current = int(snapshot["current_analysis_end_year"])
    files = list(snapshot["files"])
    file_rows: list[MonitorRow] = []
    labels = {
        f"EF{candidate}A.zip": "Fall Enrollment data",
        f"EF{candidate}A_Dict.zip": "Fall Enrollment dictionary",
        f"HD{candidate}.zip": "Institutional directory data",
        f"HD{candidate}_Dict.zip": "Institutional directory dictionary",
    }
    for index, item in enumerate(files, start=1):
        available = bool(item["available"])
        status = "AVAILABLE" if available else "NOT AVAILABLE"
        evidence = f"HTTP {item['status']} at the NCES Complete Data Files endpoint"
        if item.get("content_length"):
            evidence += f"; Content-Length {item['content_length']} bytes"
        file_rows.append(
            MonitorRow(
                monitor_id=f"R{index:02d}",
                monitor_area="NCES release package",
                subject=f"{candidate} {labels[str(item['file'])]}",
                observed_date=checked_date,
                status=status,
                evidence=evidence,
                trigger="All four candidate-year assets must be available before the annual package is treated as ready.",
                next_action=(
                    "Preserve the observation and include the file in schema review after the full package is ready."
                    if available
                    else "Continue monitoring; do not substitute a partial next-year package into the analysis."
                ),
                authority=str(item["url"]),
            )
        )

    available_count = sum(row.status == "AVAILABLE" for row in file_rows)
    package_ready = bool(snapshot["package_ready"])
    continuity = preflight["eligible_universe_continuity"]
    directory_preflight = MonitorRow(
        monitor_id="D01",
        monitor_area="Candidate directory preflight",
        subject=f"{candidate} directory structural compatibility",
        observed_date=str(preflight["checked_at_utc"])[:10],
        status="PASS",
        evidence=(
            "6/6 required directory fields preserved in data and dictionary; "
            f"{int(preflight['candidate_directory_eligible_rows']):,} directory-eligible rows; "
            f"{int(continuity['shared_unitids']):,} shared UNITIDs; net eligible change "
            f"{int(continuity['net_change']):+d}."
        ),
        trigger="Both candidate-year directory assets are available before the complete annual package.",
        next_action=(
            "Retain this as directory-side readiness evidence; do not calculate candidate-year enrollment "
            "or advance END_YEAR until Fall Enrollment data/dictionary arrive and full schema review passes."
        ),
        authority="data/candidate_directory_preflight.json",
    )
    gate = MonitorRow(
        monitor_id="G01",
        monitor_area="Annual release gate",
        subject=f"Advance analysis from {current} to {candidate}",
        observed_date=checked_date,
        status="READY FOR SCHEMA REVIEW" if package_ready else "HOLD YEAR ADVANCE",
        evidence=(
            f"{available_count}/4 required candidate-year files available in the captured NCES check; "
            f"candidate directory structural preflight {directory_preflight.status}."
        ),
        trigger="Fall Enrollment data/dictionary and directory data/dictionary are all available.",
        next_action=(
            "Follow the annual update playbook: collect sources, preserve hashes, and run the schema audit before analysis."
            if package_ready
            else f"Keep END_YEAR={current}; rerun the live release check later and advance only after the complete package is available."
        ),
        authority="data/release_monitor_snapshot.json; docs/UPDATE_PLAYBOOK.md",
    )

    library = read_csv(DATA / "research_library.csv")
    crosswalk = read_csv(DATA / "population_crosswalk.csv")
    reports = read_csv(DATA / "recurring_report_register.csv")
    if not library or not crosswalk or len(reports) != 3:
        raise RuntimeError("Freshness monitor requires populated library/crosswalk and exactly three recurring reports")
    library_dates = sorted(row["last_checked"] for row in library)
    crosswalk_dates = sorted(row["last_checked"] for row in crosswalk)
    review_rows = [
        MonitorRow(
            monitor_id="S01",
            monitor_area="Source review",
            subject="Research Library",
            observed_date=library_dates[-1],
            status="REVIEW RECORDED",
            evidence=f"{len(library)} resources; recorded review dates span {library_dates[0]} to {library_dates[-1]}.",
            trigger="Source URL, title, methodology, release pattern, vintage, or project role changes.",
            next_action="Perform a human source review before changing last_checked metadata; URL health alone does not refresh it.",
            authority="data/research_library.csv",
        ),
        MonitorRow(
            monitor_id="S02",
            monitor_area="Source review",
            subject="Population/source crosswalk",
            observed_date=crosswalk_dates[-1],
            status="REVIEW RECORDED",
            evidence=f"{len(crosswalk)} population/source definitions; recorded review dates span {crosswalk_dates[0]} to {crosswalk_dates[-1]}.",
            trigger="Population definition, methodology, source vintage, geography, or comparison rule changes.",
            next_action="Re-review the affected source before using it in a companion comparison or changing public interpretation.",
            authority="data/population_crosswalk.csv",
        ),
    ]
    report_rows: list[MonitorRow] = []
    for index, report in enumerate(reports, start=1):
        report_rows.append(
            MonitorRow(
                monitor_id=f"P{index:02d}",
                monitor_area="Recurring product",
                subject=report["report_title"],
                observed_date=report["last_reviewed"],
                status="MONITOR TRIGGER",
                evidence=(
                    f"Latest public product {report['latest_publication_date']}; current portfolio stage: "
                    f"{report['portfolio_stage']}."
                ),
                trigger=report["monitoring_trigger"],
                next_action=report["next_action"],
                authority=f"data/recurring_report_register.csv#{report['report_id']}",
            )
        )
    return [*file_rows, directory_preflight, gate, *review_rows, *report_rows], snapshot


def write_csv(rows: list[MonitorRow]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(row.as_row() for row in rows)


def write_markdown(rows: list[MonitorRow], snapshot: dict[str, object]) -> None:
    candidate = int(snapshot["candidate_next_year"])
    current = int(snapshot["current_analysis_end_year"])
    available = sum(row.status == "AVAILABLE" for row in rows if row.monitor_area == "NCES release package")
    gate = next(row for row in rows if row.monitor_id == "G01")
    directory_preflight = next(row for row in rows if row.monitor_id == "D01")
    lines = [
        "# Release and Freshness Monitor",
        "",
        "This is a **dated portfolio monitoring snapshot**, not a continuously live dashboard. The NCES availability observation is captured by the separate online release checker; the offline build preserves and validates that observation without making network access a reproducibility dependency.",
        "",
        f"- **Captured check:** {str(snapshot['checked_at_utc'])}",
        f"- **Current analysis end year:** {current}",
        f"- **Candidate next year:** {candidate}",
        f"- **Candidate package:** {available}/4 required files available",
        f"- **Decision:** {gate.status}",
        "",
        "## Monitoring register",
        "",
        "| ID | Area | Subject | Observed | Status | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.monitor_id} | {row.monitor_area} | {row.subject} | {row.observed_date} | {row.status} | {row.next_action} |"
        )
    lines.extend([
        "",
        "## Candidate directory preflight",
        "",
        f"The available candidate-year directory has already passed a bounded structural preflight: {directory_preflight.evidence} This reduces directory-side uncertainty but does not convert a partial package into an enrollment release. See `docs/CANDIDATE_DIRECTORY_PREFLIGHT.md` for the field, continuity, archive-hash, and schema-delta detail.",
        "",
        "## Operational rule",
        "",
        f"The current snapshot does not authorize advancing beyond Fall {current} unless the complete {candidate} package is available. A newly posted file is a review trigger, not automatic permission to publish. Recurring-product dates are not inferred from prior public release dates; kickoff and partner milestones remain confirmation-dependent.",
        "",
        "## Refresh the live observation",
        "",
        "```bash",
        "python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json",
        "python scripts/check_candidate_directory.py --write-snapshot data/candidate_directory_preflight.json",
        "python scripts/build_candidate_directory_preflight.py",
        "python scripts/build_freshness_monitor.py",
        "```",
        "",
    ])
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[MonitorRow], snapshot: dict[str, object]) -> None:
    candidate = int(snapshot["candidate_next_year"])
    current = int(snapshot["current_analysis_end_year"])
    preflight = load_directory_preflight(snapshot)
    continuity = preflight["eligible_universe_continuity"]
    schema_delta = preflight["schema_delta"]
    release_rows = [row for row in rows if row.monitor_area == "NCES release package"]
    gate = next(row for row in rows if row.monitor_id == "G01")
    available = sum(row.status == "AVAILABLE" for row in release_rows)
    library = next(row for row in rows if row.monitor_id == "S01")
    report_rows = [row for row in rows if row.monitor_area == "Recurring product"]
    package_ready = bool(snapshot["package_ready"])
    if package_ready:
        release_heading = "The complete package is available for schema review."
        release_copy = (
            f"All four required {candidate} assets are available. Availability starts the review process; "
            "it does not by itself authorize new public findings. Preserve the source package and run the "
            "schema and methodology gates before advancing publication."
        )
    else:
        release_heading = "Incomplete availability does not advance the project year."
        release_copy = (
            f"{available}/4 required {candidate} assets are available. The analysis therefore remains pinned "
            f"to Fall {current}; continue monitoring until the complete package is available for schema review."
        )

    release_cards = []
    for row in release_rows:
        css = "handoff-status-ready" if row.status == "AVAILABLE" else "handoff-status-hold"
        release_cards.append(f"""
          <article class="handoff-card" data-monitor-id="{row.monitor_id}">
            <div class="handoff-card-head"><span>{row.monitor_id}</span><span class="handoff-status {css}">{html.escape(row.status)}</span></div>
            <p class="case-kicker">NCES candidate-year asset</p>
            <h2>{html.escape(row.subject)}</h2>
            <dl class="handoff-meta">
              <div><dt>Evidence</dt><dd>{html.escape(row.evidence)}</dd></div>
              <div><dt>Next action</dt><dd>{html.escape(row.next_action)}</dd></div>
            </dl>
          </article>""")

    report_cards = []
    for row in report_rows:
        report_cards.append(f"""
          <article class="handoff-card" data-product-monitor="{row.monitor_id}">
            <div class="handoff-card-head"><span>{row.monitor_id}</span><span class="handoff-status handoff-status-ready">MONITOR</span></div>
            <p class="case-kicker">Recurring product trigger</p>
            <h2>{html.escape(row.subject)}</h2>
            <dl class="handoff-meta">
              <div><dt>Current evidence</dt><dd>{html.escape(row.evidence)}</dd></div>
              <div><dt>Trigger</dt><dd>{html.escape(row.trigger)}</dd></div>
              <div><dt>Next action</dt><dd>{html.escape(row.next_action)}</dd></div>
            </dl>
          </article>""")

    HTML_OUTPUT.write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Dated release-readiness and source-freshness monitoring for the higher-education research portfolio.">
  <meta name="theme-color" content="#10263c">
  <title>Freshness Monitor | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to freshness monitor</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Freshness monitor navigation"><a href="index.html">Brief</a><a href="research-library.html">Library</a><a href="research-operations.html">Operations</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero">
      <div class="shell">
        <p class="eyebrow">Release and source freshness</p>
        <h1>Know what changed before advancing the analysis year.</h1>
        <p class="lede">A dated monitoring snapshot separates source availability from publication permission: detect a release, preserve the observation, then run schema and methodology review before using it.</p>
        <div class="hero-actions"><a class="button button-primary" href="#release-readiness">Review release gate</a><a class="button button-secondary" href="downloads/freshness_monitor.csv">Download monitoring register</a></div>
        <p class="release-note"><strong>Snapshot boundary:</strong> checked {html.escape(str(snapshot['checked_at_utc']))}. This page is not continuously live, and recurring-product deadlines are not inferred from prior publication dates.</p>
        <div class="handoff-summary">
          <article><strong>{available}/4</strong><span>{candidate} package assets available</span></article>
          <article><strong>{html.escape(gate.status)}</strong><span>analysis-year decision</span></article>
          <article><strong>{html.escape(str(preflight['status']))}</strong><span>candidate directory preflight</span></article>
          <article><strong>{len(report_rows)}</strong><span>recurring products with explicit triggers</span></article>
        </div>
      </div>
    </section>
    <section class="section shell" id="release-readiness">
      <div class="section-heading"><p class="eyebrow">Candidate {candidate} package</p><h2>{html.escape(release_heading)}</h2><p>{html.escape(release_copy)}</p></div>
      <div class="handoff-grid">{''.join(release_cards)}</div>
      <div class="methods-crosswalk-callout"><div><p class="eyebrow">Decision gate</p><h3>{html.escape(gate.status)}</h3><p>{html.escape(gate.evidence)} {html.escape(gate.next_action)}</p></div><a class="button button-secondary" href="downloads/release_monitor_snapshot.json">Download captured NCES check</a></div>
    </section>
    <section class="section section-tinted" id="directory-preflight">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Candidate directory preflight</p><h2>The available directory side has already cleared a bounded structural check.</h2><p>All six fields required by the current directory join/filter are present in both the candidate CSV and dictionary. That reduces one update risk while preserving the full-package gate.</p></div>
        <div class="handoff-summary">
          <article><strong>6/6</strong><span>required directory fields preserved</span></article>
          <article><strong>{int(preflight['candidate_directory_eligible_rows']):,}</strong><span>candidate directory-eligible rows</span></article>
          <article><strong>{int(continuity['shared_unitids']):,}</strong><span>shared eligible UNITIDs</span></article>
          <article><strong>{int(continuity['net_change']):+d}</strong><span>net eligible-row change vs {current}</span></article>
        </div>
        <div class="methods-crosswalk-callout"><div><p class="eyebrow">Schema delta</p><h3>{int(preflight['current_reference']['field_count'])} → {int(preflight['candidate_field_count'])} fields</h3><p>Removed nonrequired fields: {html.escape(', '.join(schema_delta['removed_fields']) or 'None')}. Required fields are preserved, but the full annual schema audit still runs when Fall Enrollment arrives.</p></div><a class="button button-secondary" href="candidate-directory-preflight.html">Open full preflight</a></div>
      </div>
    </section>
    <section class="section section-tinted">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Source review</p><h2>Availability is only one kind of freshness.</h2><p>The Research Library and population crosswalk retain human review dates because a working URL does not prove that definitions, vintages, or comparison rules are still appropriate.</p></div>
        <div class="method-grid">
          <article><h3>Research Library</h3><p><strong>{html.escape(library.observed_date)}</strong><br>{html.escape(library.evidence)}</p></article>
          <article><h3>Population crosswalk</h3><p><strong>{html.escape(next(row for row in rows if row.monitor_id == 'S02').observed_date)}</strong><br>{html.escape(next(row for row in rows if row.monitor_id == 'S02').evidence)}</p></article>
        </div>
      </div>
    </section>
    <section class="section shell">
      <div class="section-heading"><p class="eyebrow">Recurring products</p><h2>Monitor triggers, not guessed deadlines.</h2><p>Each product carries an explicit event that begins the next review cycle. Internal milestones remain confirmation-dependent.</p></div>
      <div class="handoff-grid">{''.join(report_cards)}</div>
    </section>
    <section class="section section-tinted">
      <div class="shell"><div class="section-heading compact"><p class="eyebrow">Working pattern</p><h2>Detect → preserve → review → advance</h2></div>
        <div class="method-grid">
          <article><h3>1. Detect</h3><p>Run the online release checker separately from the reproducible research build.</p></article>
          <article><h3>2. Preserve</h3><p>Write the dated availability snapshot instead of relying on an ephemeral console message.</p></article>
          <article><h3>3. Review</h3><p>When the package is complete, preserve hashes and run schema/methodology checks before interpreting values.</p></article>
          <article><h3>4. Advance</h3><p>Change the project year only after required files and review gates support the update.</p></article>
        </div>
        <div class="memo-actions"><a class="button button-primary" href="downloads/freshness_monitor.csv">Download monitor CSV</a><a class="button button-secondary" href="downloads/freshness_monitor.md">Download monitor notes</a><a class="button button-secondary" href="candidate-directory-preflight.html">Candidate directory preflight</a></div>
      </div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Freshness Monitor · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""", encoding="utf-8")


def main() -> int:
    rows, snapshot = build_rows()
    write_csv(rows)
    write_markdown(rows, snapshot)
    write_html(rows, snapshot)
    available = sum(row.status == "AVAILABLE" for row in rows if row.monitor_area == "NCES release package")
    gate = next(row for row in rows if row.monitor_id == "G01")
    print(f"Freshness monitor: {available}/4 candidate files available; decision={gate.status}; {len(rows)} monitoring rows")
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
