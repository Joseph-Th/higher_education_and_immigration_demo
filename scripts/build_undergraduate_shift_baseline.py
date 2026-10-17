"""Build the current-data baseline for the R01 undergraduate-shift question.

R01 cannot be answered until the next IPEDS Fall Enrollment release is
available. This module makes the current comparison explicit and reproducible
so the next release has a fixed baseline rather than a retrospective one. It
measures the latest undergraduate change by state, institutional control, and
institution continuity; quantifies state and institution concentration; and
places the latest movement in the observed annual history.

The output is descriptive accounting. It does not claim persistence, explain
causes, or use the incomplete candidate-year package.
"""

from __future__ import annotations

import csv
import html
from collections import defaultdict
from pathlib import Path

from build_state_profiles import STATE_NAMES
from project_config import CORE_STATES, END_YEAR, START_YEAR


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CSV_OUTPUT = ROOT / "data" / "undergraduate_shift_baseline.csv"
DOC_OUTPUT = ROOT / "docs" / "UNDERGRADUATE_SHIFT_BASELINE.md"
HTML_OUTPUT = ROOT / "site" / "undergraduate-shift.html"
BASELINE_YEAR = 2024
PRIOR_YEAR = 2023
CONTROLS = ("Public", "Private nonprofit", "Private for-profit")

FIELDS = (
    "state",
    "state_name",
    "undergraduate_2023",
    "undergraduate_2024",
    "undergraduate_change",
    "graduate_change",
    "total_change",
    "undergraduate_direction",
    "public_undergraduate_change",
    "private_nonprofit_undergraduate_change",
    "private_forprofit_undergraduate_change",
    "continuing_undergraduate_change",
    "entered_undergraduate_enrollment",
    "exited_undergraduate_enrollment",
    "undergraduate_accounting_net",
    "directional_institution_movement",
    "offsetting_institution_movement",
    "top3_directional_contribution",
    "top3_directional_share_pct",
    "positive_state_rank",
    "share_of_gross_positive_state_pct",
    "cumulative_positive_state_share_pct",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_int(row: dict[str, str] | None, field: str) -> int:
    if row is None:
        return 0
    value = row.get(field, "")
    return int(value) if value else 0


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def endpoint_maps(
    rows: list[dict[str, str]], key: str
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    old = {row[key]: row for row in rows if int(row["year"]) == PRIOR_YEAR}
    new = {row[key]: row for row in rows if int(row["year"]) == BASELINE_YEAR}
    return old, new


def institution_state_rows(
    institution_year: list[dict[str, str]], state: str
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    old = {
        row["unitid"]: row
        for row in institution_year
        if int(row["year"]) == PRIOR_YEAR and row["state"] == state
    }
    new = {
        row["unitid"]: row
        for row in institution_year
        if int(row["year"]) == BASELINE_YEAR and row["state"] == state
    }
    return old, new


def control_change(
    old: dict[str, dict[str, str]], new: dict[str, dict[str, str]], control: str
) -> int:
    old_total = sum(
        to_int(row, "undergraduate_nonresident")
        for row in old.values()
        if row["control"] == control
    )
    new_total = sum(
        to_int(row, "undergraduate_nonresident")
        for row in new.values()
        if row["control"] == control
    )
    return new_total - old_total


def institution_accounting(
    old: dict[str, dict[str, str]], new: dict[str, dict[str, str]]
) -> dict[str, object]:
    continuing = set(old) & set(new)
    entered = set(new) - set(old)
    exited = set(old) - set(new)
    continuing_change = sum(
        to_int(new[unitid], "undergraduate_nonresident")
        - to_int(old[unitid], "undergraduate_nonresident")
        for unitid in continuing
    )
    entered_enrollment = sum(
        to_int(new[unitid], "undergraduate_nonresident") for unitid in entered
    )
    exited_enrollment = sum(
        to_int(old[unitid], "undergraduate_nonresident") for unitid in exited
    )
    net = continuing_change + entered_enrollment - exited_enrollment

    contributions: list[int] = []
    for unitid in set(old) | set(new):
        contributions.append(
            to_int(new.get(unitid), "undergraduate_nonresident")
            - to_int(old.get(unitid), "undergraduate_nonresident")
        )
    if net > 0:
        directional_values = sorted((value for value in contributions if value > 0), reverse=True)
        directional = sum(directional_values)
        offsetting = -sum(value for value in contributions if value < 0)
    elif net < 0:
        directional_values = sorted((-value for value in contributions if value < 0), reverse=True)
        directional = sum(directional_values)
        offsetting = sum(value for value in contributions if value > 0)
    else:
        directional_values = []
        directional = 0
        offsetting = 0
    top3 = sum(directional_values[:3])
    top3_share = top3 / directional * 100 if directional else 0.0
    return {
        "continuing_change": continuing_change,
        "entered_enrollment": entered_enrollment,
        "exited_enrollment": exited_enrollment,
        "net": net,
        "directional": directional,
        "offsetting": offsetting,
        "top3": top3,
        "top3_share": top3_share,
        "contributions": contributions,
    }


def build_rows() -> list[dict[str, object]]:
    state_year = read_rows(PROCESSED / "state_year.csv")
    institution_year = read_rows(PROCESSED / "institution_year.csv")
    state_old, state_new = endpoint_maps(state_year, "state")
    if set(state_old) != CORE_STATES or set(state_new) != CORE_STATES:
        raise RuntimeError("Undergraduate-shift baseline requires exactly the 50 states plus DC")

    output: list[dict[str, object]] = []
    for state in sorted(CORE_STATES, key=lambda code: STATE_NAMES[code]):
        old_state = state_old[state]
        new_state = state_new[state]
        undergraduate_2023 = to_int(old_state, "undergraduate_nonresident")
        undergraduate_2024 = to_int(new_state, "undergraduate_nonresident")
        undergraduate_change = undergraduate_2024 - undergraduate_2023
        graduate_change = (
            to_int(new_state, "graduate_nonresident")
            - to_int(old_state, "graduate_nonresident")
        )
        total_change = (
            to_int(new_state, "nonresident_enrollment")
            - to_int(old_state, "nonresident_enrollment")
        )
        if undergraduate_change + graduate_change != total_change:
            raise RuntimeError(f"Student-level latest-year change does not reconcile for {state}")

        old_inst, new_inst = institution_state_rows(institution_year, state)
        controls = {control: control_change(old_inst, new_inst, control) for control in CONTROLS}
        if sum(controls.values()) != undergraduate_change:
            raise RuntimeError(f"Institutional-control undergraduate change does not reconcile for {state}")
        accounting = institution_accounting(old_inst, new_inst)
        if int(accounting["net"]) != undergraduate_change:
            raise RuntimeError(f"Institution-continuity undergraduate change does not reconcile for {state}")
        if undergraduate_change and int(accounting["directional"]) - int(accounting["offsetting"]) != abs(
            undergraduate_change
        ):
            raise RuntimeError(f"Directional institution movement does not reconcile for {state}")

        output.append(
            {
                "state": state,
                "state_name": STATE_NAMES[state],
                "undergraduate_2023": undergraduate_2023,
                "undergraduate_2024": undergraduate_2024,
                "undergraduate_change": undergraduate_change,
                "graduate_change": graduate_change,
                "total_change": total_change,
                "undergraduate_direction": (
                    "Increase" if undergraduate_change > 0 else "Decline" if undergraduate_change < 0 else "Flat"
                ),
                "public_undergraduate_change": controls["Public"],
                "private_nonprofit_undergraduate_change": controls["Private nonprofit"],
                "private_forprofit_undergraduate_change": controls["Private for-profit"],
                "continuing_undergraduate_change": accounting["continuing_change"],
                "entered_undergraduate_enrollment": accounting["entered_enrollment"],
                "exited_undergraduate_enrollment": accounting["exited_enrollment"],
                "undergraduate_accounting_net": accounting["net"],
                "directional_institution_movement": accounting["directional"],
                "offsetting_institution_movement": accounting["offsetting"],
                "top3_directional_contribution": accounting["top3"],
                "top3_directional_share_pct": round(float(accounting["top3_share"]), 1),
                "positive_state_rank": "",
                "share_of_gross_positive_state_pct": "",
                "cumulative_positive_state_share_pct": "",
            }
        )

    positive = sorted(
        (row for row in output if int(row["undergraduate_change"]) > 0),
        key=lambda row: (-int(row["undergraduate_change"]), str(row["state"])),
    )
    gross_positive = sum(int(row["undergraduate_change"]) for row in positive)
    cumulative = 0
    for rank, row in enumerate(positive, start=1):
        change = int(row["undergraduate_change"])
        cumulative += change
        row["positive_state_rank"] = rank
        row["share_of_gross_positive_state_pct"] = round(change / gross_positive * 100, 2)
        row["cumulative_positive_state_share_pct"] = round(cumulative / gross_positive * 100, 2)
    return output


def annual_history() -> list[dict[str, object]]:
    national = sorted(
        (
            row
            for row in read_rows(PROCESSED / "national_year.csv")
            if START_YEAR <= int(row["year"]) <= BASELINE_YEAR
        ),
        key=lambda row: int(row["year"]),
    )
    states = read_rows(PROCESSED / "state_year.csv")
    states_by_year: dict[int, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in states:
        states_by_year[int(row["year"])][row["state"]] = row

    history: list[dict[str, object]] = []
    for old, new in zip(national, national[1:]):
        old_year = int(old["year"])
        new_year = int(new["year"])
        undergraduate_change = to_int(new, "undergraduate_nonresident") - to_int(
            old, "undergraduate_nonresident"
        )
        graduate_change = to_int(new, "graduate_nonresident") - to_int(old, "graduate_nonresident")
        total_change = to_int(new, "nonresident_enrollment") - to_int(old, "nonresident_enrollment")
        if undergraduate_change + graduate_change != total_change:
            raise RuntimeError(f"National student-level history does not reconcile for {new_year}")
        old_states = states_by_year[old_year]
        new_states = states_by_year[new_year]
        if set(old_states) != CORE_STATES or set(new_states) != CORE_STATES:
            raise RuntimeError(f"State breadth history is incomplete for {old_year}-{new_year}")
        positive_states = sum(
            to_int(new_states[state], "undergraduate_nonresident")
            - to_int(old_states[state], "undergraduate_nonresident")
            > 0
            for state in CORE_STATES
        )
        history.append(
            {
                "period": f"{old_year}-{new_year}",
                "end_year": new_year,
                "undergraduate_change": undergraduate_change,
                "graduate_change": graduate_change,
                "total_change": total_change,
                "states_with_undergraduate_growth": positive_states,
            }
        )
    return history


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    national = {
        int(row["year"]): row for row in read_rows(PROCESSED / "national_year.csv")
    }
    controls = read_rows(PROCESSED / "control_year.csv")
    institution_year = read_rows(PROCESSED / "institution_year.csv")
    history = annual_history()
    latest_history = history[-1]

    expected_ug = (
        to_int(national[BASELINE_YEAR], "undergraduate_nonresident")
        - to_int(national[PRIOR_YEAR], "undergraduate_nonresident")
    )
    expected_grad = (
        to_int(national[BASELINE_YEAR], "graduate_nonresident")
        - to_int(national[PRIOR_YEAR], "graduate_nonresident")
    )
    expected_total = (
        to_int(national[BASELINE_YEAR], "nonresident_enrollment")
        - to_int(national[PRIOR_YEAR], "nonresident_enrollment")
    )
    if sum(int(row["undergraduate_change"]) for row in rows) != expected_ug:
        raise RuntimeError("State undergraduate changes do not reconcile to national change")
    if sum(int(row["graduate_change"]) for row in rows) != expected_grad:
        raise RuntimeError("State graduate changes do not reconcile to national change")
    if sum(int(row["total_change"]) for row in rows) != expected_total:
        raise RuntimeError("State total changes do not reconcile to national change")

    positive_states = sorted(
        (row for row in rows if int(row["undergraduate_change"]) > 0),
        key=lambda row: int(row["positive_state_rank"]),
    )
    negative_states = sorted(
        (row for row in rows if int(row["undergraduate_change"]) < 0),
        key=lambda row: int(row["undergraduate_change"]),
    )
    gross_positive_state = sum(int(row["undergraduate_change"]) for row in positive_states)
    gross_negative_state = -sum(int(row["undergraduate_change"]) for row in negative_states)
    if gross_positive_state - gross_negative_state != expected_ug:
        raise RuntimeError("State gross undergraduate movement does not reconcile")
    top5_state = sum(int(row["undergraduate_change"]) for row in positive_states[:5])

    control_changes: dict[str, int] = {}
    for control in CONTROLS:
        old = next(
            row
            for row in controls
            if int(row["year"]) == PRIOR_YEAR and row["control"] == control
        )
        new = next(
            row
            for row in controls
            if int(row["year"]) == BASELINE_YEAR and row["control"] == control
        )
        control_changes[control] = to_int(new, "undergraduate_nonresident") - to_int(
            old, "undergraduate_nonresident"
        )
    if sum(control_changes.values()) != expected_ug:
        raise RuntimeError("National control undergraduate movement does not reconcile")

    old_inst, new_inst = endpoint_maps(institution_year, "unitid")
    accounting = institution_accounting(old_inst, new_inst)
    if int(accounting["net"]) != expected_ug:
        raise RuntimeError("National institution-continuity undergraduate movement does not reconcile")
    contributions = [int(value) for value in accounting["contributions"]]
    positive_institutions = sorted((value for value in contributions if value > 0), reverse=True)
    negative_institutions = [value for value in contributions if value < 0]
    gross_positive_institution = sum(positive_institutions)
    gross_negative_institution = -sum(negative_institutions)
    if gross_positive_institution - gross_negative_institution != expected_ug:
        raise RuntimeError("Institution gross undergraduate movement does not reconcile")
    top10_institution_share = (
        sum(positive_institutions[:10]) / gross_positive_institution * 100
        if gross_positive_institution
        else 0.0
    )

    consecutive_positive = 0
    for item in reversed(history):
        if int(item["undergraduate_change"]) > 0:
            consecutive_positive += 1
        else:
            break
    latest_is_largest_positive = int(latest_history["undergraduate_change"]) == max(
        int(item["undergraduate_change"]) for item in history
    )
    latest_has_widest_state_breadth = int(latest_history["states_with_undergraduate_growth"]) == max(
        int(item["states_with_undergraduate_growth"]) for item in history
    )

    return {
        "undergraduate_change": expected_ug,
        "graduate_change": expected_grad,
        "total_change": expected_total,
        "positive_states": positive_states,
        "negative_states": negative_states,
        "gross_positive_state": gross_positive_state,
        "gross_negative_state": gross_negative_state,
        "top5_state_share_pct": top5_state / gross_positive_state * 100,
        "control_changes": control_changes,
        "continuing_change": accounting["continuing_change"],
        "entered_enrollment": accounting["entered_enrollment"],
        "exited_enrollment": accounting["exited_enrollment"],
        "gross_positive_institution": gross_positive_institution,
        "gross_negative_institution": gross_negative_institution,
        "top10_institution_share_pct": top10_institution_share,
        "history": history,
        "consecutive_positive_undergraduate_years": consecutive_positive,
        "latest_is_largest_positive_undergraduate_change": latest_is_largest_positive,
        "latest_has_widest_state_breadth": latest_has_widest_state_breadth,
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, object]]) -> None:
    summary = summarize(rows)
    controls = summary["control_changes"]
    positive = summary["positive_states"]
    negative = summary["negative_states"]
    history = summary["history"]
    lines = [
        "# R01 Undergraduate Shift Baseline",
        "",
        f"This note establishes the fixed {PRIOR_YEAR}-{BASELINE_YEAR} baseline for R01 before the next IPEDS Fall Enrollment release arrives. It does **not** answer whether the shift persists; that requires a complete next-year package, schema review, and the same decomposition on the new release.",
        "",
        "## Baseline finding",
        "",
        f"- Undergraduate U.S. nonresident enrollment changed **{signed(int(summary['undergraduate_change']))}** from {PRIOR_YEAR} to {BASELINE_YEAR}; graduate enrollment changed **{signed(int(summary['graduate_change']))}**, for a national net change of **{signed(int(summary['total_change']))}**.",
        f"- Undergraduate enrollment increased in **{len(positive)} of 51 states/DC** and declined in **{len(negative)}**. This is the widest state breadth of undergraduate growth in the {START_YEAR}-{END_YEAR} annual series.",
        f"- The {PRIOR_YEAR}-{BASELINE_YEAR} undergraduate increase is the **largest positive annual undergraduate change** in the series and the **third consecutive annual undergraduate increase**.",
        f"- By institutional control, undergraduate change was **Public {signed(int(controls['Public']))}**, **Private nonprofit {signed(int(controls['Private nonprofit']))}**, and **Private for-profit {signed(int(controls['Private for-profit']))}**.",
        f"- Continuing institutions contributed **{signed(int(summary['continuing_change']))}**; institutions entering the analytic universe contributed **+{int(summary['entered_enrollment']):,}** and exiting institutions had **{int(summary['exited_enrollment']):,}** undergraduate U.S. nonresident students in {PRIOR_YEAR}. The entry/exit net is **{signed(int(summary['entered_enrollment']) - int(summary['exited_enrollment']))}**.",
        f"- State gross positive undergraduate movement was **{int(summary['gross_positive_state']):,}** against **{int(summary['gross_negative_state']):,}** of offsetting state declines; the top five positive states contributed **{float(summary['top5_state_share_pct']):.1f}%** of gross positive state movement.",
        f"- At the institution level, gross positive undergraduate movement was **{int(summary['gross_positive_institution']):,}** against **{int(summary['gross_negative_institution']):,}** of offsetting declines; the ten largest positive institution contributions accounted for **{float(summary['top10_institution_share_pct']):.1f}%** of gross positive institution movement.",
        "",
        "The breadth result and the institution-concentration result answer different questions. Forty-five states had undergraduate growth, while the top ten institutions accounted for only about one-fifth of gross positive institution movement. The state-level top-five share is higher because large states contain many institutions.",
        "",
        "## Annual context",
        "",
        "| Period | Undergraduate change | Graduate change | Net change | States/DC with undergraduate growth |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in history:
        lines.append(
            f"| {item['period']} | {signed(int(item['undergraduate_change']))} | "
            f"{signed(int(item['graduate_change']))} | {signed(int(item['total_change']))} | "
            f"{int(item['states_with_undergraduate_growth'])}/51 |"
        )
    lines.extend(
        [
            "",
            "## Largest current-state undergraduate increases",
            "",
            "| State | Undergraduate change | Graduate change | Net change | Public | Private nonprofit | Private for-profit | Top-three institution share |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in positive[:10]:
        lines.append(
            f"| {row['state_name']} ({row['state']}) | {signed(int(row['undergraduate_change']))} | "
            f"{signed(int(row['graduate_change']))} | {signed(int(row['total_change']))} | "
            f"{signed(int(row['public_undergraduate_change']))} | "
            f"{signed(int(row['private_nonprofit_undergraduate_change']))} | "
            f"{signed(int(row['private_forprofit_undergraduate_change']))} | "
            f"{float(row['top3_directional_share_pct']):.1f}% |"
        )
    lines.extend(
        [
            "",
            "## States with undergraduate declines",
            "",
            "| State | Undergraduate change | Graduate change | Net change | Top-three institution share |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in negative:
        lines.append(
            f"| {row['state_name']} ({row['state']}) | {signed(int(row['undergraduate_change']))} | "
            f"{signed(int(row['graduate_change']))} | {signed(int(row['total_change']))} | "
            f"{float(row['top3_directional_share_pct']):.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            f"This analysis establishes the {BASELINE_YEAR} comparison point for the next-release persistence test. It does not call the current shift durable. R01 remains open until the next complete Fall Enrollment and directory package passes schema review and the national/state decomposition is repeated.",
            "",
            "The control and institution-continuity decompositions are descriptive accounting rather than causal attribution. State identifies institution location, not student residence. Entry/exit can reflect eligibility, reporting, merger/reorganization, identifier, or location changes and should not automatically be interpreted as campus openings or closures.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python scripts/build_undergraduate_shift_baseline.py",
            "```",
            "",
            "Canonical authorities are `data/processed/national_year.csv`, `data/processed/state_year.csv`, `data/processed/control_year.csv`, and `data/processed/institution_year.csv`.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def state_table(rows: list[dict[str, object]]) -> str:
    return "".join(
        f"<tr><td>{html.escape(str(row['state_name']))} ({row['state']})</td>"
        f"<td>{signed(int(row['undergraduate_change']))}</td>"
        f"<td>{signed(int(row['graduate_change']))}</td>"
        f"<td>{signed(int(row['total_change']))}</td>"
        f"<td>{signed(int(row['public_undergraduate_change']))}</td>"
        f"<td>{signed(int(row['private_nonprofit_undergraduate_change']))}</td>"
        f"<td>{float(row['top3_directional_share_pct']):.1f}%</td></tr>"
        for row in rows
    )


def history_table(history: list[dict[str, object]]) -> str:
    return "".join(
        f"<tr><td>{item['period']}</td><td>{signed(int(item['undergraduate_change']))}</td>"
        f"<td>{signed(int(item['graduate_change']))}</td><td>{signed(int(item['total_change']))}</td>"
        f"<td>{int(item['states_with_undergraduate_growth'])}/51</td></tr>"
        for item in history
    )


def history_visual(history: list[dict[str, object]]) -> str:
    max_abs = max(abs(int(item["undergraduate_change"])) for item in history)
    rows = []
    for item in history:
        value = int(item["undergraduate_change"])
        breadth = int(item["states_with_undergraduate_growth"])
        bar_width = 50 * abs(value) / max_abs if max_abs else 0
        breadth_width = breadth / 51 * 100
        direction = "positive" if value >= 0 else "negative"
        latest = " latest" if int(item["end_year"]) == BASELINE_YEAR else ""
        rows.append(
            f"""<div class="shift-history-row{latest}">
              <span class="shift-history-period">{html.escape(str(item['period']))}</span>
              <div class="shift-change-cell"><div class="shift-diverging-track"><i class="shift-diverging-bar {direction}" style="width:{bar_width:.2f}%"></i></div><strong>{signed(value)}</strong></div>
              <div class="shift-breadth-cell"><div class="shift-breadth-track"><i style="width:{breadth_width:.2f}%"></i></div><strong>{breadth}/51</strong></div>
            </div>"""
        )
    return (
        '<div class="shift-history-visual" aria-label="Annual undergraduate enrollment change and state breadth from 2015-2016 through 2023-2024">'
        '<div class="shift-history-head"><span>Period</span><span>Undergraduate change</span><span>States/DC with growth</span></div>'
        + "".join(rows)
        + "</div>"
    )


def state_bar_panel(title: str, rows: list[dict[str, object]], max_abs: int, *, positive: bool) -> str:
    direction = "positive" if positive else "negative"
    body = "".join(
        f"""<div class="shift-state-bar-row">
          <strong>{html.escape(str(row['state']))}</strong>
          <div class="shift-state-bar-track"><i class="{direction}" style="width:{(abs(int(row['undergraduate_change'])) / max_abs * 100 if max_abs else 0):.2f}%"></i></div>
          <span>{signed(int(row['undergraduate_change']))}</span>
        </div>"""
        for row in rows
    )
    return f'<article class="shift-state-panel"><h3>{html.escape(title)}</h3>{body}</article>'


def write_html(rows: list[dict[str, object]]) -> None:
    summary = summarize(rows)
    controls = summary["control_changes"]
    positive = summary["positive_states"]
    negative = summary["negative_states"]
    state_visual_positive = positive[:6]
    state_visual_negative = negative
    state_visual_max = max(
        abs(int(row["undergraduate_change"]))
        for row in [*state_visual_positive, *state_visual_negative]
    )
    breadth_positive_pct = len(positive) / 51 * 100
    breadth_negative_pct = len(negative) / 51 * 100
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Current-data baseline for testing whether the 2024 undergraduate-led U.S. nonresident enrollment shift persists in the next IPEDS Fall Enrollment release.">
  <meta name="theme-color" content="#10263c">
  <title>Undergraduate Shift Baseline | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to undergraduate shift baseline</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Undergraduate shift navigation"><a href="index.html">Brief</a><a href="freshness-monitor.html">Freshness</a><a href="state-recovery.html">State recovery</a><a href="release-readiness.html">Release readiness</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">R01 current-data baseline</p><h1>The next release will test persistence. This fixes the baseline before it arrives.</h1><p class="lede">The {PRIOR_YEAR}-{BASELINE_YEAR} undergraduate increase is decomposed by geography, institutional control, and institution continuity, then placed in the fixed {START_YEAR}-{BASELINE_YEAR} annual history.</p><div class="hero-actions"><a class="button button-primary" href="#annual-context">Review annual context</a><a class="button button-secondary" href="downloads/undergraduate_shift_baseline.csv">Download 51-state baseline</a></div><p class="release-note"><strong>Interpretation boundary:</strong> this analysis does not establish persistence or causation. R01 remains open until the next complete Fall Enrollment package passes schema review and the comparison is repeated.</p><div class="handoff-summary"><article><strong>{signed(int(summary['undergraduate_change']))}</strong><span>undergraduate change, {PRIOR_YEAR}-{BASELINE_YEAR}</span></article><article><strong>{len(positive)}/51</strong><span>states/DC with undergraduate growth</span></article><article><strong>{int(summary['consecutive_positive_undergraduate_years'])}</strong><span>consecutive annual undergraduate gains</span></article><article><strong>{float(summary['top10_institution_share_pct']):.1f}%</strong><span>top-10 institution share of gross positive movement</span></article></div></div></section>
    <section class="section shell"><div class="section-heading"><p class="eyebrow">What changed</p><h2>The latest undergraduate increase is unusually large and geographically broad.</h2><p>Undergraduate enrollment rose in {len(positive)} states/DC, the widest breadth in the observed annual series. The national undergraduate increase is also the largest positive annual undergraduate movement since {START_YEAR}. Those facts strengthen the baseline for monitoring, but they do not substitute for a second post-{BASELINE_YEAR} observation.</p></div><div class="method-grid"><article><h3>Student level</h3><p><strong>{signed(int(summary['undergraduate_change']))}</strong> undergraduate plus <strong>{signed(int(summary['graduate_change']))}</strong> graduate = <strong>{signed(int(summary['total_change']))}</strong> total.</p></article><article><h3>Institutional control</h3><p>Public <strong>{signed(int(controls['Public']))}</strong>; private nonprofit <strong>{signed(int(controls['Private nonprofit']))}</strong>; private for-profit <strong>{signed(int(controls['Private for-profit']))}</strong>.</p></article><article><h3>Institution continuity</h3><p>Continuing institutions <strong>{signed(int(summary['continuing_change']))}</strong>; entry/exit nets to <strong>{signed(int(summary['entered_enrollment']) - int(summary['exited_enrollment']))}</strong>.</p></article><article><h3>Institution concentration</h3><p>Gross positive movement is {int(summary['gross_positive_institution']):,}; gross negative movement is {int(summary['gross_negative_institution']):,}. The ten largest gains account for {float(summary['top10_institution_share_pct']):.1f}% of gross positive movement.</p></article></div></section>
    <section class="section section-tinted" id="annual-context"><div class="shell"><div class="section-heading"><p class="eyebrow">Annual context</p><h2>Positive undergraduate direction predates 2024; the scale and breadth are new.</h2><p>The latest year is the third consecutive undergraduate increase. Its +31,592 change is the largest positive undergraduate movement in this annual series, and 45 of 51 states/DC moved up.</p></div>{history_visual(summary['history'])}<details class="evidence-details shift-audit-details"><summary>Inspect all nine annual intervals and student-level components</summary><div class="table-wrap"><table><thead><tr><th>Period</th><th>Undergraduate</th><th>Graduate</th><th>Net</th><th>States/DC with UG growth</th></tr></thead><tbody>{history_table(summary['history'])}</tbody></table></div></details></div></section>
    <section class="section shell" id="state-breadth"><div class="section-heading"><p class="eyebrow">State breadth</p><h2>Forty-five states/DC increased; only six declined.</h2><p>Gross positive state movement is {int(summary['gross_positive_state']):,}, offset by {int(summary['gross_negative_state']):,} of declines. Florida and Texas lead the gains, while California is the largest undergraduate decline.</p></div><div class="shift-breadth-summary" aria-label="45 states and DC increased undergraduate U.S. nonresident enrollment while 6 declined"><div class="shift-breadth-balance"><i class="positive" style="width:{breadth_positive_pct:.2f}%"></i><i class="negative" style="width:{breadth_negative_pct:.2f}%"></i></div><div class="shift-breadth-labels"><span><strong>{len(positive)}</strong> increased</span><span><strong>{len(negative)}</strong> declined</span></div></div><div class="shift-state-visual" aria-label="Largest state undergraduate gains and all state undergraduate declines">{state_bar_panel('Largest undergraduate gains', state_visual_positive, state_visual_max, positive=True)}{state_bar_panel('All undergraduate declines', state_visual_negative, state_visual_max, positive=False)}</div><p class="shift-visual-note">Bars use the same scale across both panels. The five largest positive states account for {float(summary['top5_state_share_pct']):.1f}% of gross positive state movement.</p><details class="evidence-details shift-audit-details"><summary>Inspect full state accounting tables</summary><h3>Ten largest undergraduate increases</h3><div class="table-wrap"><table><thead><tr><th>State</th><th>UG change</th><th>Graduate</th><th>Net</th><th>Public UG</th><th>Private nonprofit UG</th><th>Top-3 institution share</th></tr></thead><tbody>{state_table(positive[:10])}</tbody></table></div><h3>States with undergraduate declines</h3><div class="table-wrap"><table><thead><tr><th>State</th><th>UG change</th><th>Graduate</th><th>Net</th><th>Public UG</th><th>Private nonprofit UG</th><th>Top-3 institution share</th></tr></thead><tbody>{state_table(negative)}</tbody></table></div></details></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Next-release rule</p><h2>The baseline is fixed; the persistence judgment is still pending.</h2></div><div class="method-grid"><article><h3>Do not overwrite the baseline</h3><p>The incomplete candidate-year directory package is not used here. This baseline remains fixed at {PRIOR_YEAR}-{BASELINE_YEAR} even after the project later advances to a new data year.</p></article><article><h3>Repeat the same measures</h3><p>The next update should recompute national undergraduate/graduate change, state breadth, control decomposition, and institution continuity before comparing with this baseline.</p></article><article><h3>Preserve schema review</h3><p>A new release enters variable/code and universe review before any year-over-year persistence conclusion is published.</p></article><article><h3>Keep interpretation bounded</h3><p>A repeated enrollment pattern would establish persistence in the observed series, not a cause or immigration-policy effect.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/undergraduate_shift_baseline.csv">Download baseline CSV</a><a class="button button-secondary" href="downloads/undergraduate_shift_baseline.md">Download baseline note</a><a class="button button-secondary" href="freshness-monitor.html">Candidate-year freshness</a></div></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Undergraduate Shift Baseline · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    if END_YEAR < BASELINE_YEAR:
        raise RuntimeError(
            f"Project END_YEAR={END_YEAR} does not yet include the fixed {BASELINE_YEAR} R01 baseline"
        )
    rows = build_rows()
    write_csv(rows)
    write_markdown(rows)
    write_html(rows)
    summary = summarize(rows)
    print(
        "Undergraduate shift baseline: "
        f"UG={signed(int(summary['undergraduate_change']))}; "
        f"positive_states={len(summary['positive_states'])}/51; "
        f"consecutive_positive_years={summary['consecutive_positive_undergraduate_years']}; "
        f"top10_institution_share={float(summary['top10_institution_share_pct']):.1f}%"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
