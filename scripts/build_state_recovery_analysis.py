"""Build a state recovery decomposition for the 2019-2024 period.

The existing state summary identifies which states are above or below their 2019
U.S. nonresident enrollment. This layer explains those outcomes with two exact
accounting views: undergraduate versus graduate change, and institution-level
continuity versus entries/exits from the analytic universe.
"""

from __future__ import annotations

import csv
import html
from collections import Counter, defaultdict
from pathlib import Path

from build_state_profiles import STATE_NAMES
from project_config import CORE_STATES, END_YEAR


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CSV_OUTPUT = ROOT / "data" / "state_recovery_analysis.csv"
DOC_OUTPUT = ROOT / "docs" / "STATE_RECOVERY_ANALYSIS.md"
HTML_OUTPUT = ROOT / "site" / "state-recovery.html"
BASELINE_YEAR = 2019

FIELDS = (
    "state",
    "state_name",
    "recovery_status",
    "nonresident_2019",
    "nonresident_2024",
    "change_2019_2024",
    "undergraduate_change",
    "graduate_change",
    "level_driver",
    "public_change",
    "private_nonprofit_change",
    "private_forprofit_change",
    "control_driver",
    "continuing_change",
    "entered_enrollment",
    "exited_enrollment",
    "institution_accounting_net",
    "directional_movement",
    "offsetting_movement",
    "top3_directional_contribution",
    "top3_directional_share_pct",
    "top1_institution",
    "top1_contribution",
    "top3_institutions",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def classify_level_driver(net: int, undergraduate: int, graduate: int) -> str:
    if net == 0:
        return "Balanced / offsetting"
    aligned = []
    if undergraduate * net > 0:
        aligned.append((abs(undergraduate), "Undergraduate-led"))
    if graduate * net > 0:
        aligned.append((abs(graduate), "Graduate-led"))
    if not aligned:
        raise RuntimeError(
            f"No student-level component aligns with nonzero net change: {net}, {undergraduate}, {graduate}"
        )
    return max(aligned)[1]


def classify_control_driver(net: int, changes: dict[str, int]) -> str:
    if net == 0:
        return "Balanced / offsetting"
    labels = {
        "Public": "Public-led",
        "Private nonprofit": "Private nonprofit-led",
        "Private for-profit": "Private for-profit-led",
    }
    aligned = [
        (abs(change), labels[control])
        for control, change in changes.items()
        if change * net > 0
    ]
    if not aligned:
        raise RuntimeError(f"No institutional-control component aligns with nonzero net change: {net}, {changes}")
    return max(aligned)[1]


def build_rows() -> list[dict[str, object]]:
    state_year = read_rows(PROCESSED / "state_year.csv")
    summaries = {
        row["state"]: row for row in read_rows(PROCESSED / "state_change_summary.csv")
    }
    institution_year = read_rows(PROCESSED / "institution_year.csv")

    state_lookup = {
        (row["state"], int(row["year"])): row
        for row in state_year
        if int(row["year"]) in {BASELINE_YEAR, END_YEAR}
    }
    institution_lookup: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in institution_year:
        year = int(row["year"])
        if year in {BASELINE_YEAR, END_YEAR}:
            institution_lookup[(row["state"], year)][row["unitid"]] = row

    if set(summaries) != CORE_STATES:
        raise RuntimeError("State recovery summary must cover exactly the 50 states plus DC")

    output: list[dict[str, object]] = []
    for state in sorted(CORE_STATES, key=lambda code: STATE_NAMES[code]):
        baseline = state_lookup[(state, BASELINE_YEAR)]
        latest = state_lookup[(state, END_YEAR)]
        summary = summaries[state]
        baseline_total = int(baseline["nonresident_enrollment"])
        latest_total = int(latest["nonresident_enrollment"])
        net = latest_total - baseline_total
        undergraduate_change = (
            int(latest["undergraduate_nonresident"])
            - int(baseline["undergraduate_nonresident"])
        )
        graduate_change = (
            int(latest["graduate_nonresident"])
            - int(baseline["graduate_nonresident"])
        )
        if undergraduate_change + graduate_change != net:
            raise RuntimeError(f"Student-level decomposition does not reconcile for {state}")
        if int(summary[f"change_{BASELINE_YEAR}_{END_YEAR}"]) != net:
            raise RuntimeError(f"State summary does not reconcile for {state}")

        before = institution_lookup[(state, BASELINE_YEAR)]
        after = institution_lookup[(state, END_YEAR)]
        controls = ("Public", "Private nonprofit", "Private for-profit")
        before_control = {
            control: sum(
                int(row["nonresident_enrollment"])
                for row in before.values()
                if row["control"] == control
            )
            for control in controls
        }
        after_control = {
            control: sum(
                int(row["nonresident_enrollment"])
                for row in after.values()
                if row["control"] == control
            )
            for control in controls
        }
        if sum(before_control.values()) != baseline_total or sum(after_control.values()) != latest_total:
            raise RuntimeError(f"Institutional-control totals do not reconcile for {state}")
        control_changes = {
            control: after_control[control] - before_control[control]
            for control in controls
        }
        if sum(control_changes.values()) != net:
            raise RuntimeError(f"Institutional-control change does not reconcile for {state}")

        contributions: list[tuple[int, str]] = []
        continuing_change = 0
        entered_enrollment = 0
        exited_enrollment = 0
        for unitid in set(before) | set(after):
            old_value = int(before[unitid]["nonresident_enrollment"]) if unitid in before else 0
            new_value = int(after[unitid]["nonresident_enrollment"]) if unitid in after else 0
            change = new_value - old_value
            institution = (after.get(unitid) or before[unitid])["institution"]
            contributions.append((change, institution))
            if unitid in before and unitid in after:
                continuing_change += change
            elif unitid in after:
                entered_enrollment += new_value
            else:
                exited_enrollment += old_value

        accounting_net = continuing_change + entered_enrollment - exited_enrollment
        if accounting_net != net:
            raise RuntimeError(
                f"Institution accounting does not reconcile for {state}: {accounting_net} != {net}"
            )

        if net > 0:
            directional = [item for item in contributions if item[0] > 0]
            offsetting = [item for item in contributions if item[0] < 0]
        elif net < 0:
            directional = [item for item in contributions if item[0] < 0]
            offsetting = [item for item in contributions if item[0] > 0]
        else:
            directional = [item for item in contributions if item[0] != 0]
            offsetting = []
        directional.sort(key=lambda item: (abs(item[0]), item[1]), reverse=True)
        directional_movement = sum(abs(item[0]) for item in directional)
        offsetting_movement = sum(abs(item[0]) for item in offsetting)
        if net != 0 and directional_movement - offsetting_movement != abs(net):
            raise RuntimeError(f"Directional movement does not reconcile for {state}")
        top_three = directional[:3]
        top_three_total = sum(abs(item[0]) for item in top_three)
        top_three_share = (
            top_three_total / directional_movement * 100 if directional_movement else 0.0
        )
        top_one = top_three[0] if top_three else (0, "No directional institution movement")

        output.append(
            {
                "state": state,
                "state_name": STATE_NAMES[state],
                "recovery_status": summary["recovery_status"],
                "nonresident_2019": baseline_total,
                "nonresident_2024": latest_total,
                "change_2019_2024": net,
                "undergraduate_change": undergraduate_change,
                "graduate_change": graduate_change,
                "level_driver": classify_level_driver(
                    net, undergraduate_change, graduate_change
                ),
                "public_change": control_changes["Public"],
                "private_nonprofit_change": control_changes["Private nonprofit"],
                "private_forprofit_change": control_changes["Private for-profit"],
                "control_driver": classify_control_driver(net, control_changes),
                "continuing_change": continuing_change,
                "entered_enrollment": entered_enrollment,
                "exited_enrollment": exited_enrollment,
                "institution_accounting_net": accounting_net,
                "directional_movement": directional_movement,
                "offsetting_movement": offsetting_movement,
                "top3_directional_contribution": top_three_total,
                "top3_directional_share_pct": round(top_three_share, 1),
                "top1_institution": top_one[1],
                "top1_contribution": top_one[0],
                "top3_institutions": "; ".join(
                    f"{institution} ({signed(change)})"
                    for change, institution in top_three
                ),
            }
        )
    return output


def write_csv(analysis: list[dict[str, object]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(analysis)


def summarize(analysis: list[dict[str, object]]) -> dict[str, object]:
    recovered = [row for row in analysis if row["recovery_status"] == "At or above 2019"]
    below = [row for row in analysis if row["recovery_status"] == "Below 2019"]
    if len(recovered) != 33 or len(below) != 18:
        raise RuntimeError("Recovery-status counts no longer match the validated state summary")
    driver_counts = Counter(str(row["level_driver"]) for row in recovered)
    control_driver_counts = Counter(str(row["control_driver"]) for row in recovered)
    gains = sorted(analysis, key=lambda row: int(row["change_2019_2024"]), reverse=True)
    shortfalls = sorted(analysis, key=lambda row: int(row["change_2019_2024"]))
    return {
        "recovered": recovered,
        "below": below,
        "driver_counts": driver_counts,
        "control_driver_counts": control_driver_counts,
        "gains": gains,
        "shortfalls": shortfalls,
        "national_change": sum(int(row["change_2019_2024"]) for row in analysis),
    }


def write_markdown(analysis: list[dict[str, object]]) -> None:
    summary = summarize(analysis)
    gains = summary["gains"][:8]
    shortfalls = summary["shortfalls"][:8]
    drivers = summary["driver_counts"]
    control_drivers = summary["control_driver_counts"]
    lines = [
        "# State Recovery Decomposition, 2019-2024",
        "",
        "This analysis explains the project's existing state-recovery finding rather than introducing a new population definition. It decomposes each state's 2019-2024 U.S. nonresident enrollment change by student level, institutional control, and institution continuity, then measures how concentrated the directional institution movement is among the three largest contributors.",
        "",
        "## National pattern",
        "",
        f"- **{len(summary['recovered'])} states/DC** were at or above their 2019 level in 2024; **{len(summary['below'])}** remained below.",
        f"- Across the recovered group, **{drivers['Undergraduate-led']}** states/DC were undergraduate-led and **{drivers['Graduate-led']}** were graduate-led.",
        f"- By institutional control, recovered states/DC were led by private nonprofits in **{control_drivers['Private nonprofit-led']}** cases, public institutions in **{control_drivers['Public-led']}**, and private for-profits in **{control_drivers['Private for-profit-led']}**.",
        f"- Summing all state changes reconciles to a national 2019-2024 change of **{signed(int(summary['national_change']))}** students.",
        "",
        "`level_driver` identifies the student-level component aligned with the state's net direction. Institution concentration is measured against gross movement in the state's net direction, so offsets from institutions moving the other way remain visible rather than being hidden inside the net value.",
        "",
        "## Largest gains",
        "",
        "| State | Net change | Undergraduate | Graduate | Control driver | Institution accounting | Top-three directional share | Leading institution |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for row in gains:
        lines.append(
            f"| {row['state_name']} ({row['state']}) | {signed(int(row['change_2019_2024']))} | "
            f"{signed(int(row['undergraduate_change']))} | {signed(int(row['graduate_change']))} | "
            f"{row['control_driver']} | "
            f"{signed(int(row['institution_accounting_net']))} | {float(row['top3_directional_share_pct']):.1f}% | "
            f"{row['top1_institution']} ({signed(int(row['top1_contribution']))}) |"
        )
    lines.extend(
        [
            "",
            "## Largest remaining shortfalls",
            "",
            "| State | Net change | Undergraduate | Graduate | Control driver | Institution accounting | Top-three directional share | Leading institution |",
            "| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |",
        ]
    )
    for row in shortfalls:
        lines.append(
            f"| {row['state_name']} ({row['state']}) | {signed(int(row['change_2019_2024']))} | "
            f"{signed(int(row['undergraduate_change']))} | {signed(int(row['graduate_change']))} | "
            f"{row['control_driver']} | "
            f"{signed(int(row['institution_accounting_net']))} | {float(row['top3_directional_share_pct']):.1f}% | "
            f"{row['top1_institution']} ({signed(int(row['top1_contribution']))}) |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A state's net change can be concentrated even when its overall recovery status looks broad at first glance. The institution accounting therefore keeps continuing-institution change, newly present institutions, and institutions no longer in the state analytic universe separate. A UNITID entering or leaving a state's analytic universe can reflect reporting, eligibility, merger/reorganization, or location/classification change and should not automatically be interpreted as a campus opening or closure.",
            "",
            "The student-level and institutional-control decompositions are arithmetic, not causal. They identify which components contribute most to the observed direction; they do not establish why those components changed. Control is measured at each endpoint, so changes can also reflect an institution changing control category between 2019 and 2024.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python scripts/build_state_recovery_analysis.py",
            "```",
            "",
            "Canonical authorities are `data/processed/state_year.csv`, `data/processed/state_change_summary.csv`, and `data/processed/institution_year.csv`. The generated CSV is a downstream comparative analysis.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def table_rows(rows: list[dict[str, object]]) -> str:
    return "".join(
        f"<tr><td>{html.escape(str(row['state_name']))} ({row['state']})</td>"
        f"<td>{signed(int(row['change_2019_2024']))}</td>"
        f"<td>{html.escape(str(row['level_driver']))}</td>"
        f"<td>{html.escape(str(row['control_driver']))}</td>"
        f"<td>{signed(int(row['undergraduate_change']))} / {signed(int(row['graduate_change']))}</td>"
        f"<td>{float(row['top3_directional_share_pct']):.1f}%</td>"
        f"<td>{html.escape(str(row['top1_institution']))} ({signed(int(row['top1_contribution']))})</td></tr>"
        for row in rows
    )


def write_html(analysis: list[dict[str, object]]) -> None:
    summary = summarize(analysis)
    drivers = summary["driver_counts"]
    gains = summary["gains"][:8]
    shortfalls = summary["shortfalls"][:8]
    national_change = int(summary["national_change"])
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="State-level decomposition of U.S. nonresident enrollment recovery since 2019 by student level, institutional control, and institution continuity.">
  <meta name="theme-color" content="#10263c">
  <title>State Recovery Analysis | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to state recovery analysis</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="State recovery navigation"><a href="index.html">Brief</a><a href="state.html?state=CA">State profile</a><a href="ad-hoc-analysis.html">Ad hoc</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">State recovery decomposition</p><h1>Recovery status is the result. The decomposition shows what produced it.</h1><p class="lede">Every state's 2019-2024 change is reconciled three ways: undergraduate versus graduate enrollment, institutional control, and continuing institutions versus entries/exits from the state analytic universe.</p><div class="hero-actions"><a class="button button-primary" href="#largest-movements">Review state drivers</a><a class="button button-secondary" href="downloads/state_recovery_analysis.csv">Download all 51 rows</a></div><p class="release-note"><strong>Interpretation boundary:</strong> this is accounting, not causal attribution. Institution entry/exit can reflect reporting or universe changes and is not automatically a campus opening or closure.</p><div class="handoff-summary"><article><strong>{len(summary['recovered'])}</strong><span>states/DC at or above 2019</span></article><article><strong>{len(summary['below'])}</strong><span>states/DC still below 2019</span></article><article><strong>{drivers['Graduate-led']}</strong><span>recovered states/DC graduate-led</span></article><article><strong>{signed(national_change)}</strong><span>national change, 2019-2024</span></article></div></div></section>
    <section class="section shell" id="largest-movements"><div class="section-heading"><p class="eyebrow">Largest movements</p><h2>Student level and institutional control identify directional components; institution concentration shows whether movement is broad or narrow.</h2><p>The top-three share uses gross institution movement in the state's net direction as the denominator, preserving offsetting movements rather than netting them away.</p></div><h3>Largest gains</h3><div class="table-wrap"><table><thead><tr><th>State</th><th>Net</th><th>Level driver</th><th>Control driver</th><th>UG / Grad change</th><th>Top-3 share</th><th>Leading institution</th></tr></thead><tbody>{table_rows(gains)}</tbody></table></div><h3>Largest remaining shortfalls</h3><div class="table-wrap"><table><thead><tr><th>State</th><th>Net</th><th>Level driver</th><th>Control driver</th><th>UG / Grad change</th><th>Top-3 share</th><th>Leading institution</th></tr></thead><tbody>{table_rows(shortfalls)}</tbody></table></div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Accounting controls</p><h2>Three independent decompositions must return the same state total.</h2></div><div class="method-grid"><article><h3>Student level</h3><p>Undergraduate change + graduate change = state 2019-2024 net change.</p></article><article><h3>Institutional control</h3><p>Public + private nonprofit + private for-profit changes = the same state net change.</p></article><article><h3>Institution continuity</h3><p>Continuing change + entered enrollment - exited enrollment = the same state net change.</p></article><article><h3>Concentration</h3><p>Top-three directional contribution is divided by all gross institution movement aligned with the state's net direction.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/state_recovery_analysis.csv">Download decomposition CSV</a><a class="button button-secondary" href="downloads/state_recovery_analysis.md">Download analysis notes</a></div><p class="fine-print">Canonical inputs: <code>state_year.csv</code>, <code>state_change_summary.csv</code>, and <code>institution_year.csv</code>. Institutional control is measured at each endpoint and is descriptive rather than causal.</p></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>State Recovery Analysis · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    analysis = build_rows()
    write_csv(analysis)
    write_markdown(analysis)
    write_html(analysis)
    summary = summarize(analysis)
    print(
        "State recovery analysis: "
        f"{len(summary['recovered'])} recovered; {len(summary['below'])} below; "
        f"national change={signed(int(summary['national_change']))}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
