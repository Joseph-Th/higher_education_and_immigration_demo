"""Validate and render the captured candidate-directory change review.

The online candidate-directory checker captures institution-level directory
changes while the next Fall Enrollment package is still incomplete. This
offline builder verifies that the captured CSV is exactly the file hashed by
the preflight snapshot, reconciles every summary measure to the current 2024
analysis, and renders a bounded review surface without treating directory
change as enrollment change.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

from check_candidate_directory import (
    CHANGE_CLASS_ORDER,
    CHANGE_REVIEW_FIELDS,
    CONTROL_LABELS,
    INTERPRETATION_BOUNDARY,
)
from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT_PATH = DATA / "candidate_directory_preflight.json"
CSV_PATH = DATA / "candidate_directory_change_review.csv"
CURRENT_INSTITUTIONS = DATA / "processed" / f"institutions_{END_YEAR}.csv"
DOC_OUTPUT = ROOT / "docs" / "CANDIDATE_DIRECTORY_CHANGE_REVIEW.md"
HTML_OUTPUT = ROOT / "site" / "candidate-directory-changes.html"

ALLOWED_CLASSES = frozenset(CHANGE_CLASS_ORDER)
ALLOWED_YES_NO = {"Yes", "No"}
ENTRY_REASONS = {
    "new_directory_record",
    "state_entered_core_geography",
    "degree_granting_status_gained",
    "title_iv_first_look_status_gained",
}
EXIT_REASONS = {
    "directory_record_absent",
    "state_left_core_geography",
    "degree_granting_status_lost",
    "title_iv_first_look_status_lost",
}
SHARED_REASONS = {
    "institution_name_changed",
    "state_changed_within_core",
    "control_changed",
    "title_iv_indicator_changed_within_eligible_values",
}
REASON_LABELS = {
    "new_directory_record": "New directory record",
    "state_entered_core_geography": "State entered the 50-state/DC geography",
    "degree_granting_status_gained": "Degree-granting status became eligible",
    "title_iv_first_look_status_gained": "Title IV / First Look status became eligible",
    "directory_record_absent": "Directory record absent in candidate file",
    "state_left_core_geography": "State left the 50-state/DC geography",
    "degree_granting_status_lost": "Degree-granting status became ineligible",
    "title_iv_first_look_status_lost": "Title IV / First Look status became ineligible",
    "institution_name_changed": "Institution name changed",
    "state_changed_within_core": "State changed within the core geography",
    "control_changed": "Institutional control changed",
    "title_iv_indicator_changed_within_eligible_values": "Title IV indicator changed within eligible values",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        return list(reader), fields


def current_analysis_index() -> dict[str, dict[str, str]]:
    rows, fields = read_csv(CURRENT_INSTITUTIONS)
    required = {
        "unitid",
        "institution",
        "state",
        "control",
        "total_enrollment",
        "nonresident_enrollment",
    }
    missing = required - set(fields)
    if missing:
        raise RuntimeError(f"Current institution analysis is missing fields: {sorted(missing)}")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        unitid = row["unitid"]
        if unitid in result:
            raise RuntimeError(f"Duplicate current-analysis UNITID {unitid}")
        result[unitid] = row
    return result


def int_or_zero(value: str) -> int:
    return int(value) if value else 0


def changed(before: str, after: str) -> bool:
    return bool(before and after and before != after)


def validate_row(row: dict[str, str], current_analysis: dict[str, dict[str, str]]) -> None:
    unitid = row["unitid"]
    if not unitid.isdigit():
        raise RuntimeError(f"Directory change review UNITID is not numeric: {unitid!r}")
    change_class = row["change_class"]
    if change_class not in ALLOWED_CLASSES:
        raise RuntimeError(f"Unsupported directory change class for {unitid}: {change_class}")
    for field in (
        "current_directory_present",
        "candidate_directory_present",
        "current_directory_eligible",
        "candidate_directory_eligible",
        "name_changed",
        "state_changed",
        "control_changed",
        "current_analysis_present",
    ):
        if row[field] not in ALLOWED_YES_NO:
            raise RuntimeError(f"Unsupported Yes/No value for {unitid} {field}: {row[field]!r}")
    if row["interpretation_boundary"] != INTERPRETATION_BOUNDARY:
        raise RuntimeError(f"Directory change review boundary changed for {unitid}")

    reasons = set(filter(None, row["change_reasons"].split(";")))
    if not reasons:
        raise RuntimeError(f"Directory change review reasons are blank for {unitid}")
    if change_class == "ENTERED_DIRECTORY_ELIGIBLE":
        if not reasons.issubset(ENTRY_REASONS):
            raise RuntimeError(f"Unexpected entry reason for {unitid}: {sorted(reasons)}")
        if row["current_directory_eligible"] != "No" or row["candidate_directory_eligible"] != "Yes":
            raise RuntimeError(f"Entry eligibility flags do not reconcile for {unitid}")
    elif change_class == "LEFT_DIRECTORY_ELIGIBLE":
        if not reasons.issubset(EXIT_REASONS):
            raise RuntimeError(f"Unexpected exit reason for {unitid}: {sorted(reasons)}")
        if row["current_directory_eligible"] != "Yes" or row["candidate_directory_eligible"] != "No":
            raise RuntimeError(f"Exit eligibility flags do not reconcile for {unitid}")
    else:
        if not reasons.issubset(SHARED_REASONS):
            raise RuntimeError(f"Unexpected shared-attribute reason for {unitid}: {sorted(reasons)}")
        if row["current_directory_eligible"] != "Yes" or row["candidate_directory_eligible"] != "Yes":
            raise RuntimeError(f"Shared-attribute eligibility flags do not reconcile for {unitid}")

    current_present = row["current_directory_present"] == "Yes"
    candidate_present = row["candidate_directory_present"] == "Yes"
    if current_present != bool(row["current_institution"]):
        raise RuntimeError(f"Current directory presence/name mismatch for {unitid}")
    if candidate_present != bool(row["candidate_institution"]):
        raise RuntimeError(f"Candidate directory presence/name mismatch for {unitid}")
    if "new_directory_record" in reasons and current_present:
        raise RuntimeError(f"New-directory reason conflicts with current presence for {unitid}")
    if "directory_record_absent" in reasons and candidate_present:
        raise RuntimeError(f"Directory-absent reason conflicts with candidate presence for {unitid}")

    expected_name_changed = changed(row["current_institution"], row["candidate_institution"])
    expected_state_changed = changed(row["current_state"], row["candidate_state"])
    expected_control_changed = changed(row["current_control_code"], row["candidate_control_code"])
    if (row["name_changed"] == "Yes") != expected_name_changed:
        raise RuntimeError(f"Name-change flag does not reconcile for {unitid}")
    if (row["state_changed"] == "Yes") != expected_state_changed:
        raise RuntimeError(f"State-change flag does not reconcile for {unitid}")
    if (row["control_changed"] == "Yes") != expected_control_changed:
        raise RuntimeError(f"Control-change flag does not reconcile for {unitid}")

    for code_field, label_field in (
        ("current_control_code", "current_control"),
        ("candidate_control_code", "candidate_control"),
    ):
        code = row[code_field]
        expected_label = CONTROL_LABELS.get(code, "")
        if row[label_field] != expected_label:
            raise RuntimeError(f"Control code/label mismatch for {unitid} {code_field}")

    if change_class == "SHARED_ATTRIBUTE_CHANGE":
        expected_reasons = set()
        if expected_name_changed:
            expected_reasons.add("institution_name_changed")
        if expected_state_changed:
            expected_reasons.add("state_changed_within_core")
        if expected_control_changed:
            expected_reasons.add("control_changed")
        if changed(row["current_pset4flg"], row["candidate_pset4flg"]):
            expected_reasons.add("title_iv_indicator_changed_within_eligible_values")
        if reasons != expected_reasons:
            raise RuntimeError(
                f"Shared-attribute reasons do not reconcile for {unitid}: {sorted(reasons)} != {sorted(expected_reasons)}"
            )

    analysis_row = current_analysis.get(unitid)
    analysis_present = row["current_analysis_present"] == "Yes"
    if analysis_present != (analysis_row is not None):
        raise RuntimeError(f"Current analysis presence does not reconcile for {unitid}")
    if analysis_row:
        if row["current_nonresident_enrollment"] != analysis_row["nonresident_enrollment"]:
            raise RuntimeError(f"Current nonresident exposure does not reconcile for {unitid}")
        if row["current_total_enrollment"] != analysis_row["total_enrollment"]:
            raise RuntimeError(f"Current total-enrollment exposure does not reconcile for {unitid}")
        if row["current_institution"] != analysis_row["institution"]:
            raise RuntimeError(f"Current institution name does not reconcile for {unitid}")
        if row["current_state"] != analysis_row["state"]:
            raise RuntimeError(f"Current state does not reconcile for {unitid}")
        if row["current_control"] != analysis_row["control"]:
            raise RuntimeError(f"Current control does not reconcile for {unitid}")
    elif row["current_nonresident_enrollment"] or row["current_total_enrollment"]:
        raise RuntimeError(f"Current exposure values exist without a current analysis row for {unitid}")


def reason_counts(rows: list[dict[str, str]], change_class: str) -> Counter[str]:
    return Counter(
        reason
        for row in rows
        if row["change_class"] == change_class
        for reason in row["change_reasons"].split(";")
        if reason
    )


def build_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    class_counts = Counter(row["change_class"] for row in rows)
    leavers = [row for row in rows if row["change_class"] == "LEFT_DIRECTORY_ELIGIBLE"]
    shared = [row for row in rows if row["change_class"] == "SHARED_ATTRIBUTE_CHANGE"]
    control_changes = [row for row in shared if row["control_changed"] == "Yes"]
    state_changes = [row for row in shared if row["state_changed"] == "Yes"]
    name_changes = [row for row in shared if row["name_changed"] == "Yes"]

    def exposure(records: list[dict[str, str]], field: str = "current_nonresident_enrollment") -> int:
        return sum(int_or_zero(row[field]) for row in records)

    return {
        "row_count": len(rows),
        "entered": class_counts["ENTERED_DIRECTORY_ELIGIBLE"],
        "left": class_counts["LEFT_DIRECTORY_ELIGIBLE"],
        "shared_attribute": class_counts["SHARED_ATTRIBUTE_CHANGE"],
        "entry_reasons": reason_counts(rows, "ENTERED_DIRECTORY_ELIGIBLE"),
        "exit_reasons": reason_counts(rows, "LEFT_DIRECTORY_ELIGIBLE"),
        "leaver_analysis_present": sum(row["current_analysis_present"] == "Yes" for row in leavers),
        "leaver_nonresident_exposure": exposure(leavers),
        "leaver_total_exposure": exposure(leavers, "current_total_enrollment"),
        "control_changes": len(control_changes),
        "control_nonresident_exposure": exposure(control_changes),
        "state_changes": len(state_changes),
        "state_nonresident_exposure": exposure(state_changes),
        "name_changes": len(name_changes),
        "name_nonresident_exposure": exposure(name_changes),
    }


def validate_capture() -> tuple[list[dict[str, str]], dict[str, object], dict[str, object]]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if int(snapshot.get("current_analysis_end_year", -1)) != END_YEAR:
        raise RuntimeError("Candidate directory snapshot current year does not match END_YEAR")
    if int(snapshot.get("candidate_next_year", -1)) != END_YEAR + 1:
        raise RuntimeError("Candidate directory snapshot candidate year does not match END_YEAR + 1")
    if snapshot.get("status") != "PASS" or snapshot.get("year_advance_authorized") is not False:
        raise RuntimeError("Candidate directory snapshot is not a non-authorizing PASS")
    review_meta = snapshot.get("change_review")
    if not isinstance(review_meta, dict):
        raise RuntimeError("Candidate directory snapshot is missing change-review metadata")
    if review_meta.get("csv_path") != "data/candidate_directory_change_review.csv":
        raise RuntimeError("Candidate directory change-review path is unexpected")

    payload = CSV_PATH.read_bytes()
    if sha256_bytes(payload) != review_meta.get("csv_sha256"):
        raise RuntimeError("Candidate directory change review does not match the snapshot SHA-256")
    rows, fields = read_csv(CSV_PATH)
    if fields != CHANGE_REVIEW_FIELDS:
        raise RuntimeError(f"Candidate directory change-review schema mismatch: {fields}")
    if len(rows) != int(review_meta["row_count"]):
        raise RuntimeError("Candidate directory change-review row count does not match snapshot")
    unitids = [row["unitid"] for row in rows]
    if len(unitids) != len(set(unitids)):
        raise RuntimeError("Candidate directory change review contains duplicate UNITIDs")
    expected_order = sorted(
        rows,
        key=lambda row: (CHANGE_CLASS_ORDER[row["change_class"]], int(row["unitid"])),
    )
    if rows != expected_order:
        raise RuntimeError("Candidate directory change review is not in deterministic class/UNITID order")

    current_analysis = current_analysis_index()
    for row in rows:
        validate_row(row, current_analysis)

    summary = build_summary(rows)
    continuity = snapshot["eligible_universe_continuity"]
    checks = {
        "entered": int(continuity["entering_unitids"]),
        "left": int(continuity["leaving_unitids"]),
        "control_changes": int(continuity["shared_control_changes"]),
        "state_changes": int(continuity["shared_state_changes"]),
        "name_changes": int(continuity["shared_name_changes"]),
    }
    for key, expected in checks.items():
        if int(summary[key]) != expected:
            raise RuntimeError(f"Candidate directory change-review {key} does not reconcile to preflight")
    if int(summary["shared_attribute"]) != int(review_meta["shared_attribute_change_rows"]):
        raise RuntimeError("Shared attribute-change row count does not match snapshot")
    if int(summary["entered"]) != int(review_meta["entered_directory_eligible"]):
        raise RuntimeError("Entry count does not match snapshot change-review metadata")
    if int(summary["left"]) != int(review_meta["left_directory_eligible"]):
        raise RuntimeError("Exit count does not match snapshot change-review metadata")

    if dict(summary["entry_reasons"]) != review_meta["entry_reason_counts"]:
        raise RuntimeError("Entry reason counts do not match snapshot")
    if dict(summary["exit_reasons"]) != review_meta["exit_reason_counts"]:
        raise RuntimeError("Exit reason counts do not match snapshot")
    metric_pairs = {
        "leaver_analysis_present": "current_analysis_present_leavers",
        "leaver_nonresident_exposure": "current_nonresident_exposure_leavers",
        "leaver_total_exposure": "current_total_enrollment_exposure_leavers",
        "control_nonresident_exposure": "current_nonresident_exposure_control_changes",
        "state_nonresident_exposure": "current_nonresident_exposure_state_changes",
        "name_nonresident_exposure": "current_nonresident_exposure_name_changes",
    }
    for summary_key, snapshot_key in metric_pairs.items():
        if int(summary[summary_key]) != int(review_meta[snapshot_key]):
            raise RuntimeError(f"Candidate directory exposure metric mismatch: {summary_key}")
    return rows, snapshot, summary


def institution_label(row: dict[str, str]) -> str:
    return row["candidate_institution"] or row["current_institution"] or f"UNITID {row['unitid']}"


def sort_exposure(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda row: (-int_or_zero(row["current_nonresident_enrollment"]), institution_label(row), int(row["unitid"])),
    )


def reason_table_lines(counter: Counter[str]) -> list[str]:
    return [
        f"| {REASON_LABELS[reason]} | {count:,} |"
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def write_markdown(rows: list[dict[str, str]], snapshot: dict[str, object], summary: dict[str, object]) -> None:
    candidate = int(snapshot["candidate_next_year"])
    current = int(snapshot["current_analysis_end_year"])
    leavers = sort_exposure([row for row in rows if row["change_class"] == "LEFT_DIRECTORY_ELIGIBLE"])
    shared = [row for row in rows if row["change_class"] == "SHARED_ATTRIBUTE_CHANGE"]
    control_changes = sort_exposure([row for row in shared if row["control_changed"] == "Yes"])
    state_changes = sort_exposure([row for row in shared if row["state_changed"] == "Yes"])
    name_changes = sort_exposure([row for row in shared if row["name_changed"] == "Yes"])

    lines = [
        f"# Candidate {candidate} Directory Change Review",
        "",
        "This review expands the candidate-directory preflight from aggregate counts to the affected public institution records. It remains **directory-side readiness evidence only**. A change in directory eligibility, institutional control, state, or name is not evidence of a campus opening/closure or a candidate-year enrollment change.",
        "",
        f"- **Captured preflight:** `{snapshot['checked_at_utc']}`",
        f"- **Current analysis year:** {current}",
        f"- **Candidate year:** {candidate}",
        f"- **Affected UNITIDs:** {int(summary['row_count']):,}",
        f"- **Directory-eligible entry / exit:** {int(summary['entered']):,} / {int(summary['left']):,}",
        f"- **Shared eligible records with changed attributes:** {int(summary['shared_attribute']):,}",
        f"- **Year advance:** not authorized; snapshot decision remains `{snapshot['release_monitor_decision']}`",
        "",
        "## Frame turnover",
        "",
        f"The candidate directory has {int(summary['entered']):,} UNITIDs entering the directory-side eligible set and {int(summary['left']):,} leaving it, a net change of {int(summary['entered']) - int(summary['left']):+d}. Reason counts can overlap when one record changes more than one eligibility field.",
        "",
        "### Entry reasons",
        "",
        "| Structural reason | UNITIDs |",
        "| --- | ---: |",
        *reason_table_lines(summary["entry_reasons"]),
        "",
        "### Exit reasons",
        "",
        "| Structural reason | UNITIDs |",
        "| --- | ---: |",
        *reason_table_lines(summary["exit_reasons"]),
        "",
        "## Current-year exposure among candidate-frame leavers",
        "",
        f"Of the {int(summary['left']):,} directory-side leavers, {int(summary['leaver_analysis_present']):,} appear in the current {current} canonical institution analysis. Together those rows contain **{int(summary['leaver_nonresident_exposure']):,} U.S. nonresident students** and **{int(summary['leaver_total_exposure']):,} total students** in {current}. These are current-year exposure measures only; they are not projected {candidate} losses and do not imply that absent directory records represent institutional closures.",
        "",
        "| UNITID | Institution | State | Exit reason | Current nonresident | Current total |",
        "| ---: | --- | --- | --- | ---: | ---: |",
    ]
    for row in leavers[:10]:
        reasons = "; ".join(REASON_LABELS[reason] for reason in row["change_reasons"].split(";"))
        lines.append(
            f"| {row['unitid']} | {institution_label(row)} | {row['current_state']} | {reasons} | "
            f"{int_or_zero(row['current_nonresident_enrollment']):,} | {int_or_zero(row['current_total_enrollment']):,} |"
        )

    lines.extend(
        [
            "",
            "## Control changes",
            "",
            f"Six shared directory-eligible UNITIDs change institutional control. Their current {current} U.S. nonresident enrollment totals **{int(summary['control_nonresident_exposure']):,}**. This is a control-comparability flag for the next release, not a national enrollment change.",
            "",
            "| UNITID | Institution | State | Current control | Candidate control | Current nonresident |",
            "| ---: | --- | --- | --- | --- | ---: |",
        ]
    )
    for row in control_changes:
        lines.append(
            f"| {row['unitid']} | {institution_label(row)} | {row['current_state']} | {row['current_control']} | "
            f"{row['candidate_control']} | {int_or_zero(row['current_nonresident_enrollment']):,} |"
        )

    lines.extend(
        [
            "",
            "## State changes",
            "",
            f"Three shared directory-eligible UNITIDs change state codes and carry **{int(summary['state_nonresident_exposure']):,}** current-year U.S. nonresident students. Recheck state attribution after the complete candidate-year package is available; do not treat the directory move by itself as student migration.",
            "",
            "| UNITID | Institution | Current state | Candidate state | Current nonresident |",
            "| ---: | --- | --- | --- | ---: |",
        ]
    )
    for row in state_changes:
        lines.append(
            f"| {row['unitid']} | {institution_label(row)} | {row['current_state']} | {row['candidate_state']} | "
            f"{int_or_zero(row['current_nonresident_enrollment']):,} |"
        )

    lines.extend(
        [
            "",
            "## Name continuity",
            "",
            f"Forty-one shared eligible UNITIDs change institution-name strings. Those records represent **{int(summary['name_nonresident_exposure']):,}** current-year U.S. nonresident students. UNITID, not the displayed name string, remains the continuity key. The table shows the ten largest current-year exposures; the governed CSV contains all affected records.",
            "",
            "| UNITID | Current name | Candidate name | Current nonresident |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for row in name_changes[:10]:
        lines.append(
            f"| {row['unitid']} | {row['current_institution']} | {row['candidate_institution']} | "
            f"{int_or_zero(row['current_nonresident_enrollment']):,} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation and next-release rule",
            "",
            "The change review is a pre-analysis QA queue. When Fall Enrollment arrives, rebuild the full analytic join and determine which directory-side entries/exits actually enter the candidate enrollment universe. Reconcile state and control changes before interpreting subgroup movement, retain UNITID continuity across name changes, and investigate material discontinuities before institution-specific narrative. The directory review must never substitute current-year exposure for an unobserved candidate-year value.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], snapshot: dict[str, object], summary: dict[str, object]) -> None:
    candidate = int(snapshot["candidate_next_year"])
    current = int(snapshot["current_analysis_end_year"])
    leavers = sort_exposure([row for row in rows if row["change_class"] == "LEFT_DIRECTORY_ELIGIBLE"])
    shared = [row for row in rows if row["change_class"] == "SHARED_ATTRIBUTE_CHANGE"]
    control_changes = sort_exposure([row for row in shared if row["control_changed"] == "Yes"])
    state_changes = sort_exposure([row for row in shared if row["state_changed"] == "Yes"])
    name_changes = sort_exposure([row for row in shared if row["name_changed"] == "Yes"])

    def table_rows(records: list[dict[str, str]], render) -> str:
        return "".join(f"<tr>{render(row)}</tr>" for row in records)

    entry_reason_rows = "".join(
        f"<tr><td>{html.escape(REASON_LABELS[reason])}</td><td>{count:,}</td></tr>"
        for reason, count in sorted(summary["entry_reasons"].items(), key=lambda item: (-item[1], item[0]))
    )
    exit_reason_rows = "".join(
        f"<tr><td>{html.escape(REASON_LABELS[reason])}</td><td>{count:,}</td></tr>"
        for reason, count in sorted(summary["exit_reasons"].items(), key=lambda item: (-item[1], item[0]))
    )
    leaver_rows = table_rows(
        leavers[:10],
        lambda row: (
            f"<td>{row['unitid']}</td><td>{html.escape(institution_label(row))}</td><td>{html.escape(row['current_state'])}</td>"
            f"<td>{html.escape('; '.join(REASON_LABELS[reason] for reason in row['change_reasons'].split(';')))}</td>"
            f"<td>{int_or_zero(row['current_nonresident_enrollment']):,}</td><td>{int_or_zero(row['current_total_enrollment']):,}</td>"
        ),
    )
    control_rows = table_rows(
        control_changes,
        lambda row: (
            f"<td>{row['unitid']}</td><td>{html.escape(institution_label(row))}</td><td>{html.escape(row['current_state'])}</td>"
            f"<td>{html.escape(row['current_control'])}</td><td>{html.escape(row['candidate_control'])}</td>"
            f"<td>{int_or_zero(row['current_nonresident_enrollment']):,}</td>"
        ),
    )
    state_rows = table_rows(
        state_changes,
        lambda row: (
            f"<td>{row['unitid']}</td><td>{html.escape(institution_label(row))}</td><td>{html.escape(row['current_state'])}</td>"
            f"<td>{html.escape(row['candidate_state'])}</td><td>{int_or_zero(row['current_nonresident_enrollment']):,}</td>"
        ),
    )
    name_rows = table_rows(
        name_changes[:10],
        lambda row: (
            f"<td>{row['unitid']}</td><td>{html.escape(row['current_institution'])}</td>"
            f"<td>{html.escape(row['candidate_institution'])}</td><td>{int_or_zero(row['current_nonresident_enrollment']):,}</td>"
        ),
    )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Institution-level structural review of candidate-year IPEDS directory entries, exits, control changes, state changes, and name changes before Fall Enrollment is available.">
  <meta name="theme-color" content="#10263c">
  <title>Candidate Directory Changes | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to candidate directory changes</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Candidate directory change navigation"><a href="index.html">Brief</a><a href="candidate-directory-preflight.html">Preflight</a><a href="freshness-monitor.html">Freshness</a><a href="release-readiness.html">Release readiness</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero">
      <div class="shell">
        <p class="eyebrow">Candidate {candidate} directory change review</p>
        <h1>Directory changes are review signals, not enrollment findings.</h1>
        <p class="lede">The candidate directory has {int(summary['entered']):,} eligible-frame entries, {int(summary['left']):,} exits, and {int(summary['shared_attribute']):,} shared UNITIDs with changed names, states, or institutional control. This review identifies where the next full update needs extra reconciliation before any {candidate} enrollment interpretation.</p>
        <div class="hero-actions"><a class="button button-primary" href="#frame-turnover">Review frame turnover</a><a class="button button-secondary" href="downloads/candidate_directory_change_review.csv">Download full change review</a></div>
        <p class="release-note"><strong>Boundary:</strong> {html.escape(INTERPRETATION_BOUNDARY)} Fall Enrollment is still missing, so year advancement remains <code>{html.escape(str(snapshot['release_monitor_decision']))}</code>.</p>
        <div class="handoff-summary">
          <article><strong>{int(summary['row_count']):,}</strong><span>affected UNITIDs in the captured review</span></article>
          <article><strong>{int(summary['entered']):,} / {int(summary['left']):,}</strong><span>directory-eligible entries / exits</span></article>
          <article><strong>{int(summary['leaver_nonresident_exposure']):,}</strong><span>{current} nonresident students at frame leavers</span></article>
          <article><strong>{int(summary['control_nonresident_exposure']):,}</strong><span>{current} nonresident students at control-change UNITIDs</span></article>
        </div>
      </div>
    </section>

    <section class="section shell" id="frame-turnover">
      <div class="section-heading"><p class="eyebrow">Eligible-frame turnover</p><h2>Entry and exit reasons are structural and auditable.</h2><p>Reason counts can overlap when a UNITID changes more than one eligibility field. A record entering or leaving the directory-side eligible frame does not establish an opening, closure, or enrollment change.</p></div>
      <div class="method-grid">
        <article><h3>Entry reasons</h3><div class="table-wrap compact-table"><table><thead><tr><th>Reason</th><th>UNITIDs</th></tr></thead><tbody>{entry_reason_rows}</tbody></table></div></article>
        <article><h3>Exit reasons</h3><div class="table-wrap compact-table"><table><thead><tr><th>Reason</th><th>UNITIDs</th></tr></thead><tbody>{exit_reason_rows}</tbody></table></div></article>
      </div>
    </section>

    <section class="section section-tinted" id="leaver-exposure">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Current-year exposure</p><h2>Only current {current} counts are used to prioritize the next review.</h2><p>{int(summary['leaver_analysis_present']):,} of {int(summary['left']):,} frame leavers appear in the current canonical institution analysis. Together they contain {int(summary['leaver_nonresident_exposure']):,} U.S. nonresident students and {int(summary['leaver_total_exposure']):,} total students in {current}. Those counts are not projected {candidate} losses.</p></div>
        <div class="table-wrap"><table><thead><tr><th>UNITID</th><th>Institution</th><th>State</th><th>Structural reason</th><th>Current nonresident</th><th>Current total</th></tr></thead><tbody>{leaver_rows}</tbody></table></div>
      </div>
    </section>

    <section class="section shell" id="control-changes">
      <div class="section-heading"><p class="eyebrow">Control comparability</p><h2>Six shared UNITIDs change institutional control.</h2><p>These rows carry {int(summary['control_nonresident_exposure']):,} current-year U.S. nonresident students. Reconcile them before interpreting candidate-year public/nonprofit/for-profit movement.</p></div>
      <div class="table-wrap"><table><thead><tr><th>UNITID</th><th>Institution</th><th>State</th><th>Current control</th><th>Candidate control</th><th>Current nonresident</th></tr></thead><tbody>{control_rows}</tbody></table></div>
    </section>

    <section class="section section-tinted" id="state-changes">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">State comparability</p><h2>Three shared UNITIDs change state codes.</h2><p>They carry {int(summary['state_nonresident_exposure']):,} current-year U.S. nonresident students. A directory state change is an attribution review flag, not evidence that students moved.</p></div>
        <div class="table-wrap"><table><thead><tr><th>UNITID</th><th>Institution</th><th>Current state</th><th>Candidate state</th><th>Current nonresident</th></tr></thead><tbody>{state_rows}</tbody></table></div>
      </div>
    </section>

    <section class="section shell" id="name-continuity">
      <div class="section-heading"><p class="eyebrow">Label continuity</p><h2>UNITID continuity prevents name changes from becoming false institution entries.</h2><p>{int(summary['name_changes']):,} shared eligible UNITIDs change institution-name strings, representing {int(summary['name_nonresident_exposure']):,} current-year U.S. nonresident students. The ten largest current exposures are shown below; the full governed CSV contains every affected record.</p></div>
      <div class="table-wrap"><table><thead><tr><th>UNITID</th><th>Current name</th><th>Candidate name</th><th>Current nonresident</th></tr></thead><tbody>{name_rows}</tbody></table></div>
    </section>

    <section class="section section-tinted">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Next-release controls</p><h2>The review queue is ready before the enrollment file arrives.</h2></div>
        <div class="method-grid">
          <article><h3>Rebuild the full join</h3><p>When Fall Enrollment arrives, determine which directory-side entries and exits actually enter the candidate analytic universe.</p></article>
          <article><h3>Reconcile category moves</h3><p>Apply control and state changes before interpreting subgroup movement so reclassification is not mistaken for enrollment change.</p></article>
          <article><h3>Keep UNITID continuity</h3><p>Carry institution identity across name changes instead of treating renamed records as new institutions.</p></article>
          <article><h3>Re-capture revisions</h3><p>If NCES replaces either candidate directory archive, rerun the live capture and require the CSV hash and preflight snapshot to move together.</p></article>
        </div>
        <div class="memo-actions"><a class="button button-primary" href="downloads/candidate_directory_change_review.csv">Download change review CSV</a><a class="button button-secondary" href="downloads/candidate_directory_change_review.md">Download review note</a><a class="button button-secondary" href="candidate-year-watchlist.html">Carry-forward QA watchlist</a><a class="button button-secondary" href="candidate-directory-preflight.html">Directory preflight</a></div>
      </div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Candidate Directory Changes · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows, snapshot, summary = validate_capture()
    write_markdown(rows, snapshot, summary)
    write_html(rows, snapshot, summary)
    print(
        "Candidate directory change review: "
        f"rows={int(summary['row_count']):,}; enter={int(summary['entered']):,}; "
        f"leave={int(summary['left']):,}; current-NR-exposure={int(summary['leaver_nonresident_exposure']):,}"
    )
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
