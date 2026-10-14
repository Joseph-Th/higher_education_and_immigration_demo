"""Render the captured candidate-year directory preflight for offline review.

The online checker records a dated structural observation of the available HD
package. This builder validates that snapshot without making network requests,
then publishes a human-readable note and static page. The artifact never
authorizes year advancement by itself because Fall Enrollment remains a
separate required package component.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT_PATH = DATA / "candidate_directory_preflight.json"
RELEASE_SNAPSHOT_PATH = DATA / "release_monitor_snapshot.json"
DOC_OUTPUT = ROOT / "docs" / "CANDIDATE_DIRECTORY_PREFLIGHT.md"
HTML_OUTPUT = ROOT / "site" / "candidate-directory-preflight.html"

REQUIRED_FIELDS = ("UNITID", "INSTNM", "STABBR", "CONTROL", "DEGGRANT", "PSET4FLG")
CONTROL_LABELS = ("Public", "Private nonprofit", "Private for-profit")


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def validate_snapshot() -> dict[str, object]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    release = json.loads(RELEASE_SNAPSHOT_PATH.read_text(encoding="utf-8"))

    if int(payload.get("current_analysis_end_year", -1)) != END_YEAR:
        raise RuntimeError("Directory preflight current year does not match END_YEAR")
    if int(payload.get("candidate_next_year", -1)) != END_YEAR + 1:
        raise RuntimeError("Directory preflight candidate year does not match END_YEAR + 1")
    if payload.get("status") != "PASS":
        raise RuntimeError("Candidate directory preflight must be PASS before publication")
    if payload.get("year_advance_authorized") is not False:
        raise RuntimeError("Directory preflight must not authorize year advancement")

    required = payload.get("required_directory_fields")
    if required != list(REQUIRED_FIELDS):
        raise RuntimeError("Candidate directory preflight required-field set changed")
    if payload.get("missing_required_data_fields") != []:
        raise RuntimeError("Candidate directory data is missing required fields")
    if payload.get("missing_required_dictionary_fields") != []:
        raise RuntimeError("Candidate directory dictionary is missing required fields")

    titles = payload.get("required_field_titles")
    if not isinstance(titles, dict) or set(titles) != set(REQUIRED_FIELDS):
        raise RuntimeError("Candidate directory required-field titles are incomplete")
    if any(not str(titles[field]).strip() for field in REQUIRED_FIELDS):
        raise RuntimeError("Candidate directory required-field title is blank")

    candidate_rows = int(payload["candidate_directory_rows"])
    candidate_fields = int(payload["candidate_field_count"])
    candidate_eligible = int(payload["candidate_directory_eligible_rows"])
    if candidate_rows <= 0 or candidate_fields <= 0 or candidate_eligible <= 0:
        raise RuntimeError("Candidate directory structural counts must be positive")
    if int(payload["candidate_core_states_dc_count"]) != 51:
        raise RuntimeError("Candidate directory must cover all 50 states plus DC")
    if int(payload["candidate_duplicate_unitid_count"]) != 0:
        raise RuntimeError("Candidate directory contains duplicate UNITIDs")

    current = payload.get("current_reference")
    if not isinstance(current, dict) or int(current.get("year", -1)) != END_YEAR:
        raise RuntimeError("Candidate preflight current-directory reference is invalid")
    if int(current["core_states_dc_count"]) != 51:
        raise RuntimeError("Current directory reference must cover all 50 states plus DC")
    current_eligible = int(current["directory_eligible_rows"])

    candidate_controls = payload.get("candidate_control_counts")
    current_controls = current.get("control_counts")
    if not isinstance(candidate_controls, dict) or set(candidate_controls) != set(CONTROL_LABELS):
        raise RuntimeError("Candidate directory control counts are incomplete")
    if not isinstance(current_controls, dict) or set(current_controls) != set(CONTROL_LABELS):
        raise RuntimeError("Current directory control counts are incomplete")
    if sum(int(candidate_controls[label]) for label in CONTROL_LABELS) != candidate_eligible:
        raise RuntimeError("Candidate control counts do not reconcile to directory-eligible rows")
    if sum(int(current_controls[label]) for label in CONTROL_LABELS) != current_eligible:
        raise RuntimeError("Current control counts do not reconcile to directory-eligible rows")

    continuity = payload.get("eligible_universe_continuity")
    if not isinstance(continuity, dict):
        raise RuntimeError("Candidate directory continuity block is missing")
    shared = int(continuity["shared_unitids"])
    entering = int(continuity["entering_unitids"])
    leaving = int(continuity["leaving_unitids"])
    net = int(continuity["net_change"])
    if shared + entering != candidate_eligible:
        raise RuntimeError("Candidate directory continuity does not reconcile to candidate eligible rows")
    if shared + leaving != current_eligible:
        raise RuntimeError("Candidate directory continuity does not reconcile to current eligible rows")
    if entering - leaving != net or candidate_eligible - current_eligible != net:
        raise RuntimeError("Candidate directory continuity net change does not reconcile")

    schema = payload.get("schema_delta")
    if not isinstance(schema, dict) or schema.get("required_fields_preserved") is not True:
        raise RuntimeError("Candidate directory required fields are not preserved")
    if int(schema["field_count_change"]) != candidate_fields - int(current["field_count"]):
        raise RuntimeError("Candidate directory field-count delta does not reconcile")
    removed = set(schema.get("removed_fields", []))
    if removed.intersection(REQUIRED_FIELDS):
        raise RuntimeError("A required directory field appears in the removed-field set")

    source = payload.get("candidate_source")
    if not isinstance(source, dict):
        raise RuntimeError("Candidate directory source metadata is missing")
    for key in ("data_sha256", "dictionary_sha256"):
        if len(str(source.get(key, ""))) != 64:
            raise RuntimeError(f"Candidate directory {key} is not a SHA-256 digest")
    if int(source["data_archive_bytes"]) <= 0 or int(source["dictionary_archive_bytes"]) <= 0:
        raise RuntimeError("Candidate directory archive sizes must be positive")

    if int(release.get("current_analysis_end_year", -1)) != END_YEAR:
        raise RuntimeError("Release monitor current year does not match directory preflight")
    if int(release.get("candidate_next_year", -1)) != END_YEAR + 1:
        raise RuntimeError("Release monitor candidate year does not match directory preflight")
    if str(payload.get("release_monitor_checked_at_utc")) != str(release.get("checked_at_utc")):
        raise RuntimeError("Candidate directory preflight was not captured against the current release snapshot")
    if payload.get("release_monitor_decision") != release.get("release_decision"):
        raise RuntimeError("Candidate directory preflight release decision is stale")

    return payload


def write_markdown(payload: dict[str, object]) -> None:
    current = payload["current_reference"]
    continuity = payload["eligible_universe_continuity"]
    schema = payload["schema_delta"]
    source = payload["candidate_source"]
    candidate_controls = payload["candidate_control_counts"]
    current_controls = current["control_counts"]
    current_year = int(payload["current_analysis_end_year"])
    candidate_year = int(payload["candidate_next_year"])
    removed = ", ".join(f"`{field}`" for field in schema["removed_fields"]) or "None"
    added = ", ".join(f"`{field}`" for field in schema["added_fields"]) or "None"

    lines = [
        f"# Candidate {candidate_year} Directory Preflight",
        "",
        "This is a **partial-package structural preflight**, not an analysis-year advance. It uses the available candidate-year IPEDS institutional directory and dictionary to reduce directory-side uncertainty while Fall Enrollment remains unavailable.",
        "",
        f"- **Captured:** {payload['checked_at_utc']}",
        f"- **Preflight status:** {payload['status']}",
        f"- **Current published analysis year:** {current_year}",
        f"- **Candidate year:** {candidate_year}",
        f"- **Year advance authorized:** No",
        f"- **Release-monitor decision:** `{payload['release_monitor_decision']}`",
        "",
        "## What passed",
        "",
        f"The candidate directory contains **{int(payload['candidate_directory_rows']):,} rows**, all **51 states/DC**, zero duplicate UNITIDs, and **6/6 directory variables** required by the current analysis. The same variables are present in the candidate dictionary.",
        "",
        "| Required field | Candidate dictionary title |",
        "| --- | --- |",
    ]
    for field in REQUIRED_FIELDS:
        lines.append(f"| `{field}` | {payload['required_field_titles'][field]} |")
    lines.extend(
        [
            "",
            "## Directory-side continuity",
            "",
            "`Directory-eligible` applies only the current directory-side geography and institution filters: 50 states + DC, `DEGGRANT=1`, and `PSET4FLG` in `{1,3}`. It is not the final analytic universe because the candidate Fall Enrollment file is not yet available for the required UNITID match and enrollment-row checks.",
            "",
            "| Measure | Current directory | Candidate directory | Change |",
            "| --- | ---: | ---: | ---: |",
            f"| Directory rows | {int(current['directory_rows']):,} | {int(payload['candidate_directory_rows']):,} | {signed(int(payload['candidate_directory_rows']) - int(current['directory_rows']))} |",
            f"| Fields | {int(current['field_count']):,} | {int(payload['candidate_field_count']):,} | {signed(int(schema['field_count_change']))} |",
            f"| Directory-eligible rows | {int(current['directory_eligible_rows']):,} | {int(payload['candidate_directory_eligible_rows']):,} | {signed(int(continuity['net_change']))} |",
            f"| Core states/DC represented | {int(current['core_states_dc_count'])} | {int(payload['candidate_core_states_dc_count'])} | 0 |",
            "",
            f"Among directory-eligible UNITIDs, **{int(continuity['shared_unitids']):,}** are shared across {current_year}-{candidate_year}, **{int(continuity['entering_unitids']):,}** enter the directory-side eligible set, and **{int(continuity['leaving_unitids']):,}** leave it, for a net change of **{signed(int(continuity['net_change']))}**. Among shared UNITIDs, {int(continuity['shared_control_changes'])} change control, {int(continuity['shared_state_changes'])} change state, and {int(continuity['shared_name_changes'])} have a changed institution name string.",
            "",
            "### Control composition",
            "",
            "| Control | Current | Candidate | Change |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for label in CONTROL_LABELS:
        before = int(current_controls[label])
        after = int(candidate_controls[label])
        lines.append(f"| {label} | {before:,} | {after:,} | {signed(after - before)} |")
    lines.extend(
        [
            "",
            "## Schema delta",
            "",
            f"The candidate directory has {int(payload['candidate_field_count'])} fields versus {int(current['field_count'])} in the current directory. Removed fields: {removed}. Added fields: {added}. The six fields required by the current analytical join/filter are preserved in both the data file and dictionary, but the nonrequired schema change still belongs in the full annual schema review once the complete package is available.",
            "",
            "## Source integrity",
            "",
            f"- `{source['data_member']}` from {source['data_url']} — {int(source['data_archive_bytes']):,} archive bytes; SHA-256 `{source['data_sha256']}`",
            f"- `{source['dictionary_member']}` from {source['dictionary_url']} — {int(source['dictionary_archive_bytes']):,} archive bytes; SHA-256 `{source['dictionary_sha256']}`",
            "",
            "These hashes describe the candidate preflight capture. They do not enter `data/source_manifest.csv` because the candidate directory is not yet part of the canonical analytical source collection.",
            "",
            "## Decision boundary",
            "",
            f"The directory side is structurally ready for later integration, but **no {candidate_year} enrollment finding can be calculated or published from this preflight**. The project remains on Fall {current_year} until `EF{candidate_year}A.zip` and its dictionary are available, the full source package is preserved, and the cross-year schema/QA workflow passes. R01 persistence therefore remains unresolved.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(payload: dict[str, object]) -> None:
    current = payload["current_reference"]
    continuity = payload["eligible_universe_continuity"]
    schema = payload["schema_delta"]
    source = payload["candidate_source"]
    candidate_controls = payload["candidate_control_counts"]
    current_controls = current["control_counts"]
    current_year = int(payload["current_analysis_end_year"])
    candidate_year = int(payload["candidate_next_year"])
    removed = ", ".join(str(field) for field in schema["removed_fields"]) or "None"
    added = ", ".join(str(field) for field in schema["added_fields"]) or "None"

    required_cards = "".join(
        f"<article><h3><code>{html.escape(field)}</code></h3><p>{html.escape(str(payload['required_field_titles'][field]))}</p></article>"
        for field in REQUIRED_FIELDS
    )
    control_rows = "".join(
        f"<tr><td>{html.escape(label)}</td><td>{int(current_controls[label]):,}</td><td>{int(candidate_controls[label]):,}</td><td>{html.escape(signed(int(candidate_controls[label]) - int(current_controls[label])))}</td></tr>"
        for label in CONTROL_LABELS
    )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Structural preflight of the available candidate-year IPEDS institutional directory before Fall Enrollment is released.">
  <meta name="theme-color" content="#10263c">
  <title>Candidate Directory Preflight | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to candidate directory preflight</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Candidate directory navigation"><a href="index.html">Brief</a><a href="freshness-monitor.html">Freshness</a><a href="release-readiness.html">Release readiness</a><a href="undergraduate-shift.html">R01 baseline</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero">
      <div class="shell">
        <p class="eyebrow">Candidate {candidate_year} partial-package preflight</p>
        <h1>The directory side passes its structural checks. The analysis year still does not advance.</h1>
        <p class="lede">The available candidate-year institutional directory and dictionary preserve every field required by the current join/filter logic and show only a four-institution net change in the directory-side eligible set. Fall Enrollment is still missing, so this is readiness evidence, not a {candidate_year} enrollment result.</p>
        <div class="hero-actions"><a class="button button-primary" href="#continuity">Review continuity</a><a class="button button-secondary" href="downloads/candidate_directory_preflight.json">Download preflight JSON</a></div>
        <p class="release-note"><strong>Decision boundary:</strong> captured {html.escape(str(payload['checked_at_utc']))}. This preflight never substitutes for the missing Fall Enrollment data/dictionary or the full annual schema review. Year advance remains <code>{html.escape(str(payload['release_monitor_decision']))}</code>.</p>
        <div class="handoff-summary">
          <article><strong>{html.escape(str(payload['status']))}</strong><span>directory structural preflight</span></article>
          <article><strong>6/6</strong><span>required directory fields preserved</span></article>
          <article><strong>{int(payload['candidate_directory_eligible_rows']):,}</strong><span>candidate directory-eligible rows</span></article>
          <article><strong>{signed(int(continuity['net_change']))}</strong><span>net eligible-row change vs {current_year}</span></article>
        </div>
      </div>
    </section>

    <section class="section shell">
      <div class="section-heading"><p class="eyebrow">Required variables</p><h2>The current directory join/filter fields survive the candidate schema.</h2><p>Each variable is present in both the candidate CSV and its NCES dictionary. This check is deliberately narrower than full annual schema review.</p></div>
      <div class="method-grid">{required_cards}</div>
    </section>

    <section class="section section-tinted" id="continuity">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Directory-side continuity</p><h2>The eligible institution frame is nearly unchanged in net size.</h2><p>Directory eligibility applies only the current geography and institutional-status filters. Final analytical inclusion still requires the candidate Fall Enrollment match.</p></div>
        <div class="handoff-summary">
          <article><strong>{int(continuity['shared_unitids']):,}</strong><span>shared eligible UNITIDs</span></article>
          <article><strong>{int(continuity['entering_unitids']):,}</strong><span>entering eligible UNITIDs</span></article>
          <article><strong>{int(continuity['leaving_unitids']):,}</strong><span>leaving eligible UNITIDs</span></article>
          <article><strong>{int(continuity['shared_control_changes']):,}</strong><span>shared UNITIDs changing control</span></article>
        </div>
        <div class="method-grid">
          <article><h3>Current {current_year}</h3><p><strong>{int(current['directory_rows']):,}</strong> directory rows<br><strong>{int(current['directory_eligible_rows']):,}</strong> directory-eligible<br><strong>{int(current['field_count'])}</strong> fields</p></article>
          <article><h3>Candidate {candidate_year}</h3><p><strong>{int(payload['candidate_directory_rows']):,}</strong> directory rows<br><strong>{int(payload['candidate_directory_eligible_rows']):,}</strong> directory-eligible<br><strong>{int(payload['candidate_field_count'])}</strong> fields</p></article>
          <article><h3>Shared-record changes</h3><p><strong>{int(continuity['shared_state_changes'])}</strong> state changes<br><strong>{int(continuity['shared_control_changes'])}</strong> control changes<br><strong>{int(continuity['shared_name_changes'])}</strong> name-string changes</p></article>
          <article><h3>Core geography</h3><p><strong>{int(payload['candidate_core_states_dc_count'])}/51</strong> states/DC represented<br><strong>{int(payload['candidate_duplicate_unitid_count'])}</strong> duplicate UNITIDs</p></article>
        </div>
      </div>
    </section>

    <section class="section shell">
      <div class="section-heading compact"><p class="eyebrow">Institutional control</p><h2>Directory-eligible control composition changes only modestly.</h2></div>
      <div class="table-wrap"><table><thead><tr><th>Control</th><th>{current_year}</th><th>{candidate_year}</th><th>Change</th></tr></thead><tbody>{control_rows}</tbody></table></div>
    </section>

    <section class="section section-tinted">
      <div class="shell">
        <div class="section-heading compact"><p class="eyebrow">Schema delta</p><h2>Required fields are preserved even though the full directory schema changed.</h2></div>
        <div class="method-grid">
          <article><h3>Field count</h3><p>{int(current['field_count'])} → {int(payload['candidate_field_count'])} ({signed(int(schema['field_count_change']))})</p></article>
          <article><h3>Removed fields</h3><p>{html.escape(removed)}</p></article>
          <article><h3>Added fields</h3><p>{html.escape(added)}</p></article>
          <article><h3>Annual-review rule</h3><p>Nonrequired changes are still reviewed when the complete package arrives; this partial check does not waive the full schema gate.</p></article>
        </div>
      </div>
    </section>

    <section class="section shell">
      <div class="section-heading compact"><p class="eyebrow">Source integrity</p><h2>The candidate archives are hashed without entering the canonical source manifest.</h2></div>
      <div class="method-grid">
        <article><h3>{html.escape(str(source['data_member']))}</h3><p>{int(source['data_archive_bytes']):,} archive bytes<br><code class="hash-code">{html.escape(str(source['data_sha256']))}</code></p></article>
        <article><h3>{html.escape(str(source['dictionary_member']))}</h3><p>{int(source['dictionary_archive_bytes']):,} archive bytes<br><code class="hash-code">{html.escape(str(source['dictionary_sha256']))}</code></p></article>
      </div>
      <div class="methods-crosswalk-callout"><div><p class="eyebrow">What remains blocked</p><h3>No {candidate_year} enrollment claims yet</h3><p><code>EF{candidate_year}A.zip</code> and its dictionary are still required. Once the full package is available, preserve all source hashes, run the cross-year schema audit, rebuild the analysis, and only then apply the pre-specified R01 persistence rule.</p></div><a class="button button-secondary" href="freshness-monitor.html">Review release monitor</a></div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/candidate_directory_preflight.json">Download JSON</a><a class="button button-secondary" href="downloads/candidate_directory_preflight.md">Download notes</a></div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Candidate Directory Preflight · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = validate_snapshot()
    write_markdown(payload)
    write_html(payload)
    continuity = payload["eligible_universe_continuity"]
    print(
        f"Candidate directory preflight: {payload['status']}; "
        f"eligible={int(payload['candidate_directory_eligible_rows']):,}; "
        f"shared={int(continuity['shared_unitids']):,}; net={signed(int(continuity['net_change']))}"
    )
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
