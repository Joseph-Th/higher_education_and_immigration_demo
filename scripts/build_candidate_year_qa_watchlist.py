from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path

from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"

LATEST_REVIEW = PROCESSED / "latest_release_institution_review.csv"
CANDIDATE_CHANGES = DATA / "candidate_directory_change_review.csv"
QA_RESOLUTIONS = DATA / "qa_resolution_log.csv"
MEDIUM_QA_RESOLUTIONS = DATA / "medium_qa_resolution_log.csv"

CSV_OUTPUT = DATA / "candidate_year_qa_watchlist.csv"
DOC_OUTPUT = ROOT / "docs" / "CANDIDATE_YEAR_QA_WATCHLIST.md"
HTML_OUTPUT = ROOT / "site" / "candidate-year-watchlist.html"

CURRENT_PRIORITIES = {"high", "medium"}
GROUP_ORDER = {
    "CURRENT_HIGH_PLUS_DIRECTORY_CHANGE": 1,
    "CURRENT_HIGH_PRIORITY": 2,
    "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE": 3,
    "CURRENT_MEDIUM_PRIORITY": 4,
    "CANDIDATE_DIRECTORY_CHANGE_ONLY": 5,
}
GROUP_LABELS = {
    "CURRENT_HIGH_PLUS_DIRECTORY_CHANGE": "Current high priority + candidate directory change",
    "CURRENT_HIGH_PRIORITY": "Current high priority",
    "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE": "Current medium priority + candidate directory change",
    "CURRENT_MEDIUM_PRIORITY": "Current medium priority",
    "CANDIDATE_DIRECTORY_CHANGE_ONLY": "Candidate directory change only",
}
BOUNDARY = (
    f"Carry-forward QA signal only; do not infer {END_YEAR + 1} enrollment movement, institutional opening/closure, "
    f"or continued publication eligibility from this row. Reassess against the full {END_YEAR + 1} Fall Enrollment package."
)

FIELDS = (
    "review_order",
    "unitid",
    "current_institution",
    "candidate_institution",
    "current_state",
    "candidate_state",
    "current_control",
    "candidate_control",
    "carry_forward_group",
    "current_review_priority",
    "latest_release_change",
    "latest_release_pct_change",
    "latest_review_reasons",
    "flag_2023",
    "flag_2024",
    "candidate_change_class",
    "candidate_change_reasons",
    f"current_{END_YEAR}_nonresident",
    f"current_{END_YEAR}_total_enrollment",
    "high_priority_publication_class",
    "high_priority_disposition",
    "medium_priority_publication_class",
    "medium_priority_disposition",
    "next_release_action",
    "interpretation_boundary",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def integer(value: str) -> int:
    return int(value) if value.strip() else 0


def signed(value: str | int) -> str:
    number = int(value)
    return f"{number:+,}" if number else "0"


def label(value: str) -> str:
    return value.replace("_", " ").capitalize()


def publication_label(value: str) -> str:
    return {
        "safe_with_context": "Safe with context",
        "hold_for_confirmation": "Hold for confirmation",
    }.get(value, label(value))


def build_rows() -> list[dict[str, str]]:
    latest_rows = read_csv(LATEST_REVIEW)
    candidate_rows = read_csv(CANDIDATE_CHANGES)
    qa_rows = read_csv(QA_RESOLUTIONS)
    medium_qa_rows = read_csv(MEDIUM_QA_RESOLUTIONS)

    latest_selected = {
        row["unitid"]: row
        for row in latest_rows
        if row["review_priority"] in CURRENT_PRIORITIES
    }
    candidate_by_unitid = {row["unitid"]: row for row in candidate_rows}
    qa_by_unitid = {row["unitid"]: row for row in qa_rows}
    medium_qa_by_unitid = {row["unitid"]: row for row in medium_qa_rows}

    if len(latest_selected) != 77:
        raise RuntimeError(f"Expected 77 current high/medium review rows, found {len(latest_selected)}")
    if len(candidate_by_unitid) != 154:
        raise RuntimeError(f"Expected 154 candidate directory change rows, found {len(candidate_by_unitid)}")
    if len(qa_by_unitid) != 27:
        raise RuntimeError(f"Expected 27 high-priority QA resolutions, found {len(qa_by_unitid)}")
    if len(medium_qa_by_unitid) != 50:
        raise RuntimeError(f"Expected 50 medium-priority QA resolutions, found {len(medium_qa_by_unitid)}")

    high_unitids = {
        unitid for unitid, row in latest_selected.items() if row["review_priority"] == "high"
    }
    if high_unitids != set(qa_by_unitid):
        missing = sorted(high_unitids - set(qa_by_unitid))
        extra = sorted(set(qa_by_unitid) - high_unitids)
        raise RuntimeError(f"High-priority QA resolution coverage mismatch; missing={missing}, extra={extra}")
    medium_unitids = {
        unitid for unitid, row in latest_selected.items() if row["review_priority"] == "medium"
    }
    if medium_unitids != set(medium_qa_by_unitid):
        missing = sorted(medium_unitids - set(medium_qa_by_unitid))
        extra = sorted(set(medium_qa_by_unitid) - medium_unitids)
        raise RuntimeError(f"Medium-priority QA resolution coverage mismatch; missing={missing}, extra={extra}")

    union_unitids = set(latest_selected) | set(candidate_by_unitid)
    rows: list[dict[str, str]] = []
    for unitid in union_unitids:
        latest = latest_selected.get(unitid)
        candidate = candidate_by_unitid.get(unitid)
        resolution = qa_by_unitid.get(unitid)
        medium_resolution = medium_qa_by_unitid.get(unitid)

        priority = latest["review_priority"] if latest else ""
        if priority == "high" and candidate:
            group = "CURRENT_HIGH_PLUS_DIRECTORY_CHANGE"
        elif priority == "high":
            group = "CURRENT_HIGH_PRIORITY"
        elif priority == "medium" and candidate:
            group = "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"
        elif priority == "medium":
            group = "CURRENT_MEDIUM_PRIORITY"
        else:
            group = "CANDIDATE_DIRECTORY_CHANGE_ONLY"

        current_institution = ""
        current_state = ""
        current_control = ""
        current_nonresident = ""
        current_total = ""
        if candidate:
            current_institution = candidate["current_institution"]
            current_state = candidate["current_state"]
            current_control = candidate["current_control"]
            current_nonresident = candidate["current_nonresident_enrollment"]
            current_total = candidate["current_total_enrollment"]
        if latest:
            current_institution = latest["institution"]
            current_state = latest["state"]
            current_control = latest["control"]
            if current_nonresident and current_nonresident != latest["nonresident_2024"]:
                raise RuntimeError(
                    f"Current nonresident mismatch for UNITID {unitid}: candidate={current_nonresident} latest={latest['nonresident_2024']}"
                )
            current_nonresident = latest["nonresident_2024"]

        if not current_institution and candidate:
            current_institution = candidate["candidate_institution"]
            current_state = candidate["candidate_state"]
            current_control = candidate["candidate_control"]

        if group.startswith("CURRENT_HIGH"):
            next_action = (
                f"Reapply the high-priority rules to the {END_YEAR + 1} Fall Enrollment result and revalidate the existing "
                f"{END_YEAR} publication disposition; do not inherit the prior decision automatically."
            )
        elif group == "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE":
            next_action = (
                f"Reapply the medium-priority rules to the {END_YEAR + 1} Fall Enrollment result, review the enrollment "
                "movement and candidate directory change together, and revalidate the current publication disposition."
            )
        elif group == "CURRENT_MEDIUM_PRIORITY":
            next_action = (
                f"Reapply the review thresholds after the {END_YEAR + 1} build and revalidate the current publication "
                "disposition if the movement remains material; do not inherit the prior decision automatically."
            )
        else:
            next_action = (
                f"Reconcile directory continuity against the full {END_YEAR + 1} Fall Enrollment join before interpreting any enrollment movement."
            )

        rows.append(
            {
                "review_order": "",
                "unitid": unitid,
                "current_institution": current_institution,
                "candidate_institution": candidate["candidate_institution"] if candidate else "",
                "current_state": current_state,
                "candidate_state": candidate["candidate_state"] if candidate else "",
                "current_control": current_control,
                "candidate_control": candidate["candidate_control"] if candidate else "",
                "carry_forward_group": group,
                "current_review_priority": priority,
                "latest_release_change": latest["absolute_change"] if latest else "",
                "latest_release_pct_change": latest["pct_change"] if latest else "",
                "latest_review_reasons": latest["review_reasons"] if latest else "",
                "flag_2023": latest["flag_2023"] if latest else "",
                "flag_2024": latest["flag_2024"] if latest else "",
                "candidate_change_class": candidate["change_class"] if candidate else "",
                "candidate_change_reasons": candidate["change_reasons"] if candidate else "",
                f"current_{END_YEAR}_nonresident": current_nonresident,
                f"current_{END_YEAR}_total_enrollment": current_total,
                "high_priority_publication_class": resolution["publication_class"] if resolution else "",
                "high_priority_disposition": resolution["disposition"] if resolution else "",
                "medium_priority_publication_class": medium_resolution["publication_class"] if medium_resolution else "",
                "medium_priority_disposition": medium_resolution["disposition"] if medium_resolution else "",
                "next_release_action": next_action,
                "interpretation_boundary": BOUNDARY,
            }
        )

    def sort_key(row: dict[str, str]) -> tuple[int, int, int]:
        latest_magnitude = abs(integer(row["latest_release_change"]))
        current_exposure = integer(row[f"current_{END_YEAR}_nonresident"])
        magnitude = latest_magnitude if row["current_review_priority"] else current_exposure
        return (GROUP_ORDER[row["carry_forward_group"]], -magnitude, int(row["unitid"]))

    rows.sort(key=sort_key)
    for order, row in enumerate(rows, start=1):
        row["review_order"] = str(order)
    return rows


def validate_rows(rows: list[dict[str, str]]) -> dict[str, int]:
    if len(rows) != 226:
        raise RuntimeError(f"Expected 226 carry-forward watchlist rows, found {len(rows)}")
    if len({row["unitid"] for row in rows}) != len(rows):
        raise RuntimeError("Candidate-year watchlist contains duplicate UNITIDs")
    if [int(row["review_order"]) for row in rows] != list(range(1, len(rows) + 1)):
        raise RuntimeError("Candidate-year watchlist review_order is not sequential")

    counts = Counter(row["carry_forward_group"] for row in rows)
    expected = {
        "CURRENT_HIGH_PRIORITY": 27,
        "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE": 5,
        "CURRENT_MEDIUM_PRIORITY": 45,
        "CANDIDATE_DIRECTORY_CHANGE_ONLY": 149,
    }
    if counts["CURRENT_HIGH_PLUS_DIRECTORY_CHANGE"] != 0:
        raise RuntimeError("Current capture unexpectedly has high-priority/candidate-directory overlap; review the publication logic")
    for group, expected_count in expected.items():
        if counts[group] != expected_count:
            raise RuntimeError(f"Unexpected {group} count: {counts[group]} (expected {expected_count})")

    high = [row for row in rows if row["current_review_priority"] == "high"]
    medium = [row for row in rows if row["current_review_priority"] == "medium"]
    candidate = [row for row in rows if row["candidate_change_class"]]
    if len(high) != 27 or len(medium) != 50 or len(candidate) != 154:
        raise RuntimeError("Watchlist source counts do not reconcile to 27 high / 50 medium / 154 candidate changes")
    if Counter(row["high_priority_publication_class"] for row in high) != Counter(
        {"hold_for_confirmation": 11, "safe_with_context": 16}
    ):
        raise RuntimeError("High-priority publication classes do not reconcile to the QA resolution log")
    if any(row["high_priority_publication_class"] for row in medium):
        raise RuntimeError("Medium-priority rows must not inherit high-priority publication dispositions")
    if Counter(row["medium_priority_publication_class"] for row in medium) != Counter(
        {"hold_for_confirmation": 33, "safe_with_context": 17}
    ):
        raise RuntimeError("Medium-priority publication classes do not reconcile to the medium QA resolution log")
    if any(row["medium_priority_publication_class"] for row in high):
        raise RuntimeError("High-priority rows must not inherit medium-priority publication dispositions")
    if any(
        row["medium_priority_publication_class"] or row["high_priority_publication_class"]
        for row in rows
        if not row["current_review_priority"]
    ):
        raise RuntimeError("Candidate-directory-only rows must not inherit current publication dispositions")
    if any(row["interpretation_boundary"] != BOUNDARY for row in rows):
        raise RuntimeError("Watchlist interpretation boundary is inconsistent")

    medium_overlap = [row for row in rows if row["carry_forward_group"] == "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"]
    if sum(integer(row[f"current_{END_YEAR}_nonresident"]) for row in medium_overlap) != 2_443:
        raise RuntimeError("Medium/candidate overlap current nonresident exposure changed unexpectedly")
    candidate_only = [row for row in rows if row["carry_forward_group"] == "CANDIDATE_DIRECTORY_CHANGE_ONLY"]
    if sum(integer(row[f"current_{END_YEAR}_nonresident"]) for row in candidate_only) != 9_326:
        raise RuntimeError("Candidate-only current nonresident exposure changed unexpectedly")

    return {
        "row_count": len(rows),
        "high_count": len(high),
        "medium_count": len(medium),
        "candidate_count": len(candidate),
        "high_candidate_overlap": counts["CURRENT_HIGH_PLUS_DIRECTORY_CHANGE"],
        "medium_candidate_overlap": counts["CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"],
        "candidate_only_count": counts["CANDIDATE_DIRECTORY_CHANGE_ONLY"],
        "high_safe": sum(row["high_priority_publication_class"] == "safe_with_context" for row in high),
        "high_held": sum(row["high_priority_publication_class"] == "hold_for_confirmation" for row in high),
        "medium_safe": sum(row["medium_priority_publication_class"] == "safe_with_context" for row in medium),
        "medium_held": sum(row["medium_priority_publication_class"] == "hold_for_confirmation" for row in medium),
        "medium_overlap_exposure": sum(integer(row[f"current_{END_YEAR}_nonresident"]) for row in medium_overlap),
        "candidate_only_exposure": sum(integer(row[f"current_{END_YEAR}_nonresident"]) for row in candidate_only),
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def overlap_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["carry_forward_group"] == "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"]


def high_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["current_review_priority"] == "high"][:10]


def candidate_only_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["carry_forward_group"] == "CANDIDATE_DIRECTORY_CHANGE_ONLY"][:10]


def write_markdown(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    lines = [
        "# Candidate-Year QA Carry-Forward Watchlist",
        "",
        f"This pre-release watchlist combines the current {END_YEAR - 1}-{END_YEAR} high/medium institution QA queue with the already-available {END_YEAR + 1} candidate directory structural review. It contains **{summary['row_count']:,} unique UNITIDs** and is intended to make the next full-package QA pass faster without inventing candidate-year enrollment values.",
        "",
        "## Reconciliation",
        "",
        f"- **Current high-priority QA rows:** {summary['high_count']:,}",
        f"- **Current medium-priority QA rows:** {summary['medium_count']:,}",
        f"- **Candidate directory structural-change rows:** {summary['candidate_count']:,}",
        f"- **Current high + candidate directory overlaps:** {summary['high_candidate_overlap']:,}",
        f"- **Current medium + candidate directory overlaps:** {summary['medium_candidate_overlap']:,}",
        f"- **Unique union:** {summary['high_count']} + {summary['medium_count']} + {summary['candidate_count']} - {summary['medium_candidate_overlap']} = **{summary['row_count']:,}**",
        "",
        f"The existing high-priority evidence review remains **{summary['high_safe']} safe with context / {summary['high_held']} held for confirmation**, and the medium-priority evidence review remains **{summary['medium_safe']} safe with context / {summary['medium_held']} held**, for the current {END_YEAR} publication. Those decisions are carried as context only and must be revalidated after the next complete Fall Enrollment build; they are not automatically inherited by {END_YEAR + 1}.",
        "",
        "## Medium-priority rows that also changed in the candidate directory",
        "",
        f"Five current medium-priority rows also have a candidate directory structural signal. Together they represent **{summary['medium_overlap_exposure']:,} current-year U.S. nonresident students**. This overlap changes review order, not publication status.",
        "",
        "| Institution | State | 2023-2024 change | Current publication class | Candidate directory signal | 2024 nonresident |",
        "| --- | --- | ---: | --- | --- | ---: |",
    ]
    for row in overlap_rows(rows):
        reasons = row["candidate_change_reasons"].replace(";", "; ")
        lines.append(
            f"| {row['current_institution']} | {row['current_state']} | {signed(row['latest_release_change'])} | {publication_label(row['medium_priority_publication_class'])} | {label(row['candidate_change_class'])}: {reasons} | {integer(row[f'current_{END_YEAR}_nonresident']):,} |"
        )

    lines.extend(
        [
            "",
            "## Current high-priority carry-forwards",
            "",
            "The first ten rows below are ordered by absolute current latest-release change. Current publication classes are shown because they already have evidence-backed review, but the next-release action is still to revalidate rather than inherit the decision.",
            "",
            "| Institution | State | 2023-2024 change | Current publication class |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for row in high_rows(rows):
        lines.append(
            f"| {row['current_institution']} | {row['current_state']} | {signed(row['latest_release_change'])} | {publication_label(row['high_priority_publication_class'])} |"
        )

    lines.extend(
        [
            "",
            "## Candidate-directory-only rows with the largest current exposure",
            "",
            f"There are **{summary['candidate_only_count']:,}** candidate structural-change rows that are not in the current high/medium queue. Their current-year U.S. nonresident exposure sums to **{summary['candidate_only_exposure']:,}**. Exposure only determines display order here; it is not a risk score or a forecast.",
            "",
            "| Institution | Current state | Candidate signal | 2024 nonresident | Candidate identity/state/control |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in candidate_only_rows(rows):
        candidate_identity = row["candidate_institution"] or "Not present"
        candidate_state = row["candidate_state"] or "—"
        candidate_control = row["candidate_control"] or "—"
        lines.append(
            f"| {row['current_institution']} | {row['current_state']} | {label(row['candidate_change_class'])}: {row['candidate_change_reasons'].replace(';', '; ')} | {integer(row[f'current_{END_YEAR}_nonresident']):,} | {candidate_identity}; {candidate_state}; {candidate_control} |"
        )

    lines.extend(
        [
            "",
            "## Review order and boundary",
            "",
            "The CSV uses the existing review signals rather than inventing a new risk score. Current high-priority rows come first, then current medium rows that also have a candidate directory change, then the remaining current medium rows, then candidate-directory-only rows ordered by current-year U.S. nonresident exposure. UNITID breaks ties.",
            "",
            f"**Boundary:** {BOUNDARY}",
            "",
            "When the complete candidate-year package arrives, every watchlist row should be reconciled against the full Fall Enrollment join before any institution-specific next-release narrative is published. A current `safe_with_context` decision is not a standing approval for a future release.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    overlap_html = []
    for row in overlap_rows(rows):
        overlap_html.append(
            "<tr>"
            f"<td>{html.escape(row['current_institution'])}</td>"
            f"<td>{html.escape(row['current_state'])}</td>"
            f"<td>{signed(row['latest_release_change'])}</td>"
            f"<td>{html.escape(publication_label(row['medium_priority_publication_class']))}</td>"
            f"<td>{html.escape(label(row['candidate_change_class']))}<br><small>{html.escape(row['candidate_change_reasons'].replace(';', '; '))}</small></td>"
            f"<td>{integer(row[f'current_{END_YEAR}_nonresident']):,}</td>"
            "</tr>"
        )

    high_html = []
    for row in high_rows(rows):
        high_html.append(
            "<tr>"
            f"<td>{html.escape(row['current_institution'])}</td>"
            f"<td>{html.escape(row['current_state'])}</td>"
            f"<td>{signed(row['latest_release_change'])}</td>"
            f"<td>{html.escape(publication_label(row['high_priority_publication_class']))}</td>"
            "</tr>"
        )

    candidate_html = []
    for row in candidate_only_rows(rows):
        candidate_identity = row["candidate_institution"] or "Not present in candidate directory"
        candidate_html.append(
            "<tr>"
            f"<td>{html.escape(row['current_institution'])}</td>"
            f"<td>{html.escape(row['current_state'])}</td>"
            f"<td>{html.escape(label(row['candidate_change_class']))}<br><small>{html.escape(row['candidate_change_reasons'].replace(';', '; '))}</small></td>"
            f"<td>{integer(row[f'current_{END_YEAR}_nonresident']):,}</td>"
            f"<td>{html.escape(candidate_identity)}<br><small>{html.escape(row['candidate_state'] or '—')} · {html.escape(row['candidate_control'] or '—')}</small></td>"
            "</tr>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Candidate-year institution QA carry-forward watchlist combining current high/medium review signals with candidate directory structural changes.">
  <meta name="theme-color" content="#10263c">
  <title>Candidate-Year QA Watchlist | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to candidate-year QA watchlist</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Candidate-year QA navigation"><a href="index.html">Brief</a><a href="qa-review.html">Current QA</a><a href="candidate-directory-changes.html">Directory changes</a><a href="release-readiness.html">Release readiness</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell">
      <p class="eyebrow">Candidate-year QA carry-forward</p>
      <h1>The next full-package QA pass already has a {summary['row_count']:,}-institution watchlist.</h1>
      <p class="lede">The list unions the current high/medium institution review queue with every candidate-directory structural change. Existing priorities and evidence-backed publication dispositions are preserved as current-release context; no candidate-year enrollment values are invented.</p>
      <div class="hero-actions"><a class="button button-primary" href="#overlap">Review cross-signal overlaps</a><a class="button button-secondary" href="downloads/candidate_year_qa_watchlist.csv">Download full watchlist</a></div>
      <p class="release-note"><strong>Boundary:</strong> {html.escape(BOUNDARY)}</p>
      <div class="handoff-summary">
        <article><strong>{summary['row_count']:,}</strong><span>unique UNITIDs carried forward</span></article>
        <article><strong>{summary['high_count']}</strong><span>current high-priority QA rows</span></article>
        <article><strong>{summary['medium_candidate_overlap']}</strong><span>current medium rows with candidate directory change</span></article>
        <article><strong>{summary['candidate_count']}</strong><span>candidate directory structural-change rows</span></article>
      </div>
    </div></section>

    <section class="section shell">
      <div class="section-heading"><p class="eyebrow">Exact union</p><h2>226 is a reconciled union, not a second independent flagging system.</h2><p>{summary['high_count']} current high-priority rows + {summary['medium_count']} current medium-priority rows + {summary['candidate_count']} candidate directory changes - {summary['medium_candidate_overlap']} overlaps = {summary['row_count']} unique UNITIDs. No current high-priority record overlaps the captured candidate directory changes.</p></div>
      <div class="method-grid">
        <article><h3>Current high-priority layer</h3><p><strong>{summary['high_safe']} safe with context / {summary['high_held']} held</strong><br>The current evidence-backed disposition is retained only as context for the next review.</p></article>
        <article><h3>Current medium-priority layer</h3><p><strong>{summary['medium_safe']} safe with context / {summary['medium_held']} held</strong><br>The current evidence-backed disposition is retained only as context for the next review.</p></article>
        <article><h3>Candidate directory layer</h3><p><strong>{summary['candidate_count']} rows</strong><br>Structural entry, exit, name, state, and control changes are carried forward before Fall Enrollment arrives.</p></article>
        <article><h3>No new risk score</h3><p>The watchlist preserves existing high/medium priority, surfaces cross-signal overlap, then orders candidate-only rows by current-year exposure.</p></article>
      </div>
    </section>

    <section class="section section-tinted" id="overlap"><div class="shell">
      <div class="section-heading"><p class="eyebrow">Cross-signal overlap</p><h2>Five current medium-priority rows also changed in the candidate directory.</h2><p>These five rows represent {summary['medium_overlap_exposure']:,} current-year U.S. nonresident students. The overlap means the enrollment movement and directory continuity should be reviewed together when the full package arrives; it does not upgrade the row to a high-priority finding.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>2023-2024 change</th><th>Current publication class</th><th>Candidate directory signal</th><th>2024 nonresident</th></tr></thead><tbody>{''.join(overlap_html)}</tbody></table></div>
    </div></section>

    <section class="section shell" id="current-high">
      <div class="section-heading"><p class="eyebrow">Current high-priority carry-forward</p><h2>Existing publication decisions are context, not standing approval.</h2><p>The ten largest current high-priority changes are shown below. All 27 appear in the downloadable watchlist. A current <em>Safe with context</em> disposition must be revalidated after the candidate-year build rather than inherited automatically.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>2023-2024 change</th><th>Current publication class</th></tr></thead><tbody>{''.join(high_html)}</tbody></table></div>
    </section>

    <section class="section section-tinted" id="candidate-only"><div class="shell">
      <div class="section-heading"><p class="eyebrow">Candidate-directory-only queue</p><h2>149 structural changes sit outside the current high/medium queue.</h2><p>These rows total {summary['candidate_only_exposure']:,} current-year U.S. nonresident students. The table shows the ten largest current exposures only. Exposure determines display order, not risk, and a directory signal is not a candidate-year enrollment finding.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Current institution</th><th>State</th><th>Candidate signal</th><th>2024 nonresident</th><th>Candidate identity/state/control</th></tr></thead><tbody>{''.join(candidate_html)}</tbody></table></div>
    </div></section>

    <section class="section shell">
      <div class="section-heading compact"><p class="eyebrow">Next-release operating rule</p><h2>Carry forward the question, not the answer.</h2></div>
      <div class="method-grid">
        <article><h3>High priority</h3><p>Reapply the thresholds and revalidate the evidence-backed publication disposition against the new release.</p></article>
        <article><h3>Medium + directory change</h3><p>Review the enrollment movement and structural directory change together, then revalidate the current evidence-backed disposition.</p></article>
        <article><h3>Remaining medium</h3><p>Reapply the latest-release rules and revalidate the current evidence-backed disposition if the next change remains material.</p></article>
        <article><h3>Directory only</h3><p>Reconcile the candidate directory record to the full Fall Enrollment join before interpreting enrollment movement.</p></article>
      </div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/candidate_year_qa_watchlist.csv">Download watchlist CSV</a><a class="button button-secondary" href="downloads/candidate_year_qa_watchlist.md">Download watchlist note</a><a class="button button-secondary" href="candidate-directory-changes.html">Directory change review</a><a class="button button-secondary" href="qa-review.html">Current high-priority review</a><a class="button button-secondary" href="medium-qa-review.html">Medium QA evidence review</a></div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Candidate-Year QA Watchlist · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows = build_rows()
    summary = validate_rows(rows)
    write_csv(rows)
    write_markdown(rows, summary)
    write_html(rows, summary)
    print(
        "Candidate-year QA watchlist: "
        f"rows={summary['row_count']}; high={summary['high_count']}; medium={summary['medium_count']}; "
        f"candidate={summary['candidate_count']}; medium+candidate={summary['medium_candidate_overlap']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
