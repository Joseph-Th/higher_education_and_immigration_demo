"""Analyze whether private-nonprofit U.S. nonresident growth is broadly distributed.

The sector-level finding is already validated in ``control_year.csv``. This
downstream layer attributes the 2015-2024 private-nonprofit change to endpoint
institution contributions, decomposes it by student level, and measures how much
gross positive movement is captured by the largest contributors.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path

from project_config import END_YEAR, START_YEAR


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CSV_OUTPUT = ROOT / "data" / "private_nonprofit_growth.csv"
DOC_OUTPUT = ROOT / "docs" / "PRIVATE_NONPROFIT_GROWTH.md"
HTML_OUTPUT = ROOT / "site" / "private-nonprofit-growth.html"
SECTOR = "Private nonprofit"

FIELDS = (
    "unitid",
    "institution",
    "state_2015",
    "state_2024",
    "endpoint_status",
    "nonresident_2015",
    "nonresident_2024",
    "change_2015_2024",
    "undergraduate_change",
    "graduate_change",
    "latest_release_review_priority",
    "latest_release_publication_class",
    "narrative_gate",
    "positive_rank",
    "share_of_gross_positive_pct",
    "cumulative_positive_share_pct",
    "concentration_group",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def gate_label(value: object) -> str:
    labels = {
        "safe_with_context": "Safe with context",
        "hold_for_confirmation": "Hold for confirmation",
        "high-priority review unresolved": "High-priority review unresolved",
        "not high-priority in latest release queue": "Not high-priority in latest release queue",
    }
    return labels.get(str(value), str(value).replace("_", " ").capitalize())


def endpoint_label(value: object) -> str:
    labels = {
        "Private nonprofit in both endpoints": "Private nonprofit in both endpoints",
        "Entered private-nonprofit endpoint universe": "Entered endpoint sector universe",
        "Left private-nonprofit endpoint universe": "Left endpoint sector universe",
    }
    return labels.get(str(value), str(value))


def to_int(row: dict[str, str] | None, field: str) -> int:
    if row is None:
        return 0
    value = row[field]
    return int(value) if value else 0


def sector_control_totals() -> dict[int, dict[str, str]]:
    rows = read_rows(PROCESSED / "control_year.csv")
    selected = {
        int(row["year"]): row
        for row in rows
        if row["control"] == SECTOR and int(row["year"]) in {START_YEAR, END_YEAR}
    }
    if set(selected) != {START_YEAR, END_YEAR}:
        raise RuntimeError("Private-nonprofit control totals are missing an endpoint year")
    return selected


def build_rows() -> list[dict[str, object]]:
    institution_year = read_rows(PROCESSED / "institution_year.csv")
    latest_review = {
        row["unitid"]: row
        for row in read_rows(PROCESSED / "latest_release_institution_review.csv")
    }
    resolution = {
        row["unitid"]: row for row in read_rows(ROOT / "data" / "qa_resolution_log.csv")
    }
    endpoint_rows = [
        row
        for row in institution_year
        if row["control"] == SECTOR and int(row["year"]) in {START_YEAR, END_YEAR}
    ]
    before = {
        row["unitid"]: row for row in endpoint_rows if int(row["year"]) == START_YEAR
    }
    after = {
        row["unitid"]: row for row in endpoint_rows if int(row["year"]) == END_YEAR
    }
    if not before or not after:
        raise RuntimeError("Private-nonprofit endpoint institution sets are empty")

    output: list[dict[str, object]] = []
    for unitid in sorted(set(before) | set(after), key=int):
        old = before.get(unitid)
        new = after.get(unitid)
        old_total = to_int(old, "nonresident_enrollment")
        new_total = to_int(new, "nonresident_enrollment")
        change = new_total - old_total
        undergraduate_change = to_int(new, "undergraduate_nonresident") - to_int(
            old, "undergraduate_nonresident"
        )
        graduate_change = to_int(new, "graduate_nonresident") - to_int(
            old, "graduate_nonresident"
        )
        if undergraduate_change + graduate_change != change:
            raise RuntimeError(f"Student-level contribution does not reconcile for UNITID {unitid}")

        if old and new:
            status = "Private nonprofit in both endpoints"
        elif new:
            status = "Entered private-nonprofit endpoint universe"
        else:
            status = "Left private-nonprofit endpoint universe"

        review_row = latest_review.get(unitid)
        review_priority = review_row["review_priority"] if review_row else "not_in_latest_endpoint"
        resolution_row = resolution.get(unitid)
        publication_class = resolution_row["publication_class"] if resolution_row else ""
        if review_priority == "high":
            narrative_gate = publication_class or "high-priority review unresolved"
        else:
            narrative_gate = "not high-priority in latest release queue"

        output.append(
            {
                "unitid": unitid,
                "institution": (new or old)["institution"],
                "state_2015": old["state"] if old else "",
                "state_2024": new["state"] if new else "",
                "endpoint_status": status,
                "nonresident_2015": old_total,
                "nonresident_2024": new_total,
                "change_2015_2024": change,
                "undergraduate_change": undergraduate_change,
                "graduate_change": graduate_change,
                "latest_release_review_priority": review_priority,
                "latest_release_publication_class": publication_class,
                "narrative_gate": narrative_gate,
                "positive_rank": "",
                "share_of_gross_positive_pct": "",
                "cumulative_positive_share_pct": "",
                "concentration_group": "Nonpositive contribution",
            }
        )

    positive = sorted(
        (row for row in output if int(row["change_2015_2024"]) > 0),
        key=lambda row: (
            -int(row["change_2015_2024"]),
            str(row["institution"]),
            int(row["unitid"]),
        ),
    )
    gross_positive = sum(int(row["change_2015_2024"]) for row in positive)
    if not gross_positive:
        raise RuntimeError("Private-nonprofit gross positive movement is zero")
    cumulative = 0
    for rank, row in enumerate(positive, start=1):
        contribution = int(row["change_2015_2024"])
        cumulative += contribution
        row["positive_rank"] = rank
        row["share_of_gross_positive_pct"] = round(contribution / gross_positive * 100, 2)
        row["cumulative_positive_share_pct"] = round(cumulative / gross_positive * 100, 2)
        if rank <= 10:
            row["concentration_group"] = "Top 10 positive contributors"
        elif rank <= 25:
            row["concentration_group"] = "Positive contributors 11-25"
        else:
            row["concentration_group"] = "Other positive contributors"

    controls = sector_control_totals()
    expected_2015 = int(controls[START_YEAR]["nonresident_enrollment"])
    expected_2024 = int(controls[END_YEAR]["nonresident_enrollment"])
    if sum(int(row["nonresident_2015"]) for row in output) != expected_2015:
        raise RuntimeError("Private-nonprofit 2015 institution total does not match control-year authority")
    if sum(int(row["nonresident_2024"]) for row in output) != expected_2024:
        raise RuntimeError("Private-nonprofit 2024 institution total does not match control-year authority")
    if sum(int(row["change_2015_2024"]) for row in output) != expected_2024 - expected_2015:
        raise RuntimeError("Private-nonprofit institution contributions do not reconcile to sector change")
    return output


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    controls = sector_control_totals()
    total_2015 = int(controls[START_YEAR]["nonresident_enrollment"])
    total_2024 = int(controls[END_YEAR]["nonresident_enrollment"])
    net = total_2024 - total_2015
    undergraduate_change = int(controls[END_YEAR]["undergraduate_nonresident"]) - int(
        controls[START_YEAR]["undergraduate_nonresident"]
    )
    graduate_change = int(controls[END_YEAR]["graduate_nonresident"]) - int(
        controls[START_YEAR]["graduate_nonresident"]
    )
    if undergraduate_change + graduate_change != net:
        raise RuntimeError("Private-nonprofit student-level sector change does not reconcile")

    positive = sorted(
        (row for row in rows if int(row["change_2015_2024"]) > 0),
        key=lambda row: int(row["positive_rank"]),
    )
    negative = [row for row in rows if int(row["change_2015_2024"]) < 0]
    zero = [row for row in rows if int(row["change_2015_2024"]) == 0]
    gross_positive = sum(int(row["change_2015_2024"]) for row in positive)
    gross_negative = -sum(int(row["change_2015_2024"]) for row in negative)
    if gross_positive - gross_negative != net:
        raise RuntimeError("Private-nonprofit gross movement does not reconcile to sector net change")

    top1 = sum(int(row["change_2015_2024"]) for row in positive[:1])
    top5 = sum(int(row["change_2015_2024"]) for row in positive[:5])
    top10 = sum(int(row["change_2015_2024"]) for row in positive[:10])
    top25 = sum(int(row["change_2015_2024"]) for row in positive[:25])
    top10_share = top10 / gross_positive * 100
    decision = (
        "Concentrated in the top 10"
        if top10_share >= 50
        else "Broadly distributed beyond the top 10"
    )

    continuing = [row for row in rows if row["endpoint_status"] == "Private nonprofit in both endpoints"]
    entered = [
        row
        for row in rows
        if row["endpoint_status"] == "Entered private-nonprofit endpoint universe"
    ]
    exited = [
        row
        for row in rows
        if row["endpoint_status"] == "Left private-nonprofit endpoint universe"
    ]
    continuing_change = sum(int(row["change_2015_2024"]) for row in continuing)
    entered_enrollment = sum(int(row["nonresident_2024"]) for row in entered)
    exited_enrollment = sum(int(row["nonresident_2015"]) for row in exited)
    if continuing_change + entered_enrollment - exited_enrollment != net:
        raise RuntimeError("Private-nonprofit endpoint accounting does not reconcile")

    hhi = sum(
        (int(row["change_2015_2024"]) / gross_positive) ** 2 for row in positive
    ) * 10000
    effective_contributors = 10000 / hhi if hhi else 0.0
    return {
        "total_2015": total_2015,
        "total_2024": total_2024,
        "net": net,
        "undergraduate_change": undergraduate_change,
        "graduate_change": graduate_change,
        "gross_positive": gross_positive,
        "gross_negative": gross_negative,
        "positive_count": len(positive),
        "negative_count": len(negative),
        "zero_count": len(zero),
        "top1": top1,
        "top5": top5,
        "top10": top10,
        "top25": top25,
        "top1_share_pct": top1 / gross_positive * 100,
        "top5_share_pct": top5 / gross_positive * 100,
        "top10_share_pct": top10_share,
        "top25_share_pct": top25 / gross_positive * 100,
        "outside_top10_share_pct": (gross_positive - top10) / gross_positive * 100,
        "decision": decision,
        "hhi": hhi,
        "effective_contributors": effective_contributors,
        "continuing_change": continuing_change,
        "entered_enrollment": entered_enrollment,
        "exited_enrollment": exited_enrollment,
        "continuing_count": len(continuing),
        "entered_count": len(entered),
        "exited_count": len(exited),
        "positive": positive,
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def top_table_markdown(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| Rank | Institution | State | Change | Undergraduate | Graduate | Gross-positive share | Cumulative share | Endpoint status | Latest-release QA gate |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows[:10]:
        state = str(row["state_2024"] or row["state_2015"])
        lines.append(
            f"| {row['positive_rank']} | {row['institution']} | {state} | "
            f"{signed(int(row['change_2015_2024']))} | {signed(int(row['undergraduate_change']))} | "
            f"{signed(int(row['graduate_change']))} | {float(row['share_of_gross_positive_pct']):.2f}% | "
            f"{float(row['cumulative_positive_share_pct']):.2f}% | {endpoint_label(row['endpoint_status'])} | "
            f"{gate_label(row['narrative_gate'])} |"
        )
    return lines


def write_markdown(rows: list[dict[str, object]]) -> None:
    summary = summarize(rows)
    lines = [
        "# Private Nonprofit Growth Concentration, 2015-2024",
        "",
        "This analysis follows research-agenda item R03 and tests whether the private-nonprofit increase in U.S. nonresident enrollment is dominated by a small set of institutions or distributed more broadly across the sector.",
        "",
        "## Result",
        "",
        f"Private nonprofit institutions increased from **{summary['total_2015']:,}** U.S. nonresident students in 2015 to **{summary['total_2024']:,}** in 2024, a net change of **{signed(int(summary['net']))}**.",
        "",
        f"Graduate enrollment contributed **{signed(int(summary['graduate_change']))}** while undergraduate enrollment contributed **{signed(int(summary['undergraduate_change']))}**. The top 10 positive institution contributors account for **{summary['top10_share_pct']:.1f}%** of gross positive movement, leaving **{summary['outside_top10_share_pct']:.1f}%** outside the top 10 across **{summary['positive_count']}** positive contributors.",
        "",
        f"**Decision rule:** call the sector shift concentrated only if the top 10 institutions contribute at least half of gross positive movement. **Result: {summary['decision']}.**",
        "",
        "Gross positive movement is the denominator for concentration. Using the net sector change instead would overstate leading-institution shares whenever declining institutions offset some growth.",
        "",
        "## Concentration checks",
        "",
        f"- Gross positive movement: **{summary['gross_positive']:,}** across **{summary['positive_count']}** institutions.",
        f"- Gross negative movement: **{summary['gross_negative']:,}** across **{summary['negative_count']}** institutions.",
        f"- Top 1 / top 5 / top 10 / top 25 shares of gross positive movement: **{summary['top1_share_pct']:.1f}% / {summary['top5_share_pct']:.1f}% / {summary['top10_share_pct']:.1f}% / {summary['top25_share_pct']:.1f}%**.",
        f"- Positive-contribution HHI: **{summary['hhi']:.0f}**, equivalent to about **{summary['effective_contributors']:.1f}** equally sized positive contributors.",
        f"- Endpoint accounting: continuing private nonprofits **{signed(int(summary['continuing_change']))}** + entering endpoint enrollment **{summary['entered_enrollment']:,}** - exiting endpoint enrollment **{summary['exited_enrollment']:,}** = **{signed(int(summary['net']))}**.",
        "",
        "## Ten largest positive contributors",
        "",
        *top_table_markdown(summary["positive"]),
        "",
        "## Interpretation",
        "",
        "The decomposition is descriptive, not causal. An institution appearing only in one private-nonprofit endpoint can reflect entry to or exit from the analytic universe, a control-category change, reporting change, merger/reorganization, or another classification change. The endpoint-status field therefore should not be read automatically as a campus opening or closure.",
        "",
        "The concentration calculation retains all official IPEDS endpoint values. The institution table shows whether a contributor was private nonprofit in both endpoints or entered the endpoint sector universe, and separately carries the current latest-release QA priority and analyst publication class. Sector entry can reflect control-category or universe change rather than institution-level enrollment growth. A high-priority institution that is unresolved or held may remain in aggregate accounting while its institution-specific interpretation remains withheld.",
        "",
        "The top-10 majority rule is an explicit portfolio decision rule for the R03 question, not a general statistical standard. The underlying shares, gross movements, contributor counts, and institution rows are published so a reviewer can apply a different concentration threshold if desired.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/build_private_nonprofit_analysis.py",
        "```",
        "",
        "Canonical inputs are `data/processed/control_year.csv` and `data/processed/institution_year.csv`. The generated institution-contribution table is downstream analysis rather than a new analytical authority.",
        "",
    ]
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def top_table_html(rows: list[dict[str, object]]) -> str:
    rendered = []
    for row in rows[:10]:
        state = str(row["state_2024"] or row["state_2015"])
        rendered.append(
            f"<tr><td>{row['positive_rank']}</td><td>{html.escape(str(row['institution']))}</td>"
            f"<td>{html.escape(state)}</td><td>{signed(int(row['change_2015_2024']))}</td>"
            f"<td>{signed(int(row['undergraduate_change']))} / {signed(int(row['graduate_change']))}</td>"
            f"<td>{float(row['share_of_gross_positive_pct']):.1f}%</td>"
            f"<td>{float(row['cumulative_positive_share_pct']):.1f}%</td>"
            f"<td>{html.escape(endpoint_label(row['endpoint_status']))}</td>"
            f"<td>{html.escape(gate_label(row['narrative_gate']))}</td></tr>"
        )
    return "".join(rendered)


def write_html(rows: list[dict[str, object]]) -> None:
    summary = summarize(rows)
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Concentration analysis of private-nonprofit U.S. nonresident enrollment growth from 2015 to 2024.">
  <meta name="theme-color" content="#10263c">
  <title>Private Nonprofit Growth | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to private nonprofit growth analysis</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Private nonprofit analysis navigation"><a href="index.html">Brief</a><a href="state-recovery.html">State recovery</a><a href="ad-hoc-analysis.html">Ad hoc</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Institutional-control research note</p><h1>Private nonprofit increase extends beyond the largest institutions.</h1><p class="lede">The sector added {summary['net']:,} U.S. nonresident students from 2015 to 2024. Concentration is measured against gross positive institution movement so declines elsewhere do not inflate the leading contributors' shares.</p><div class="hero-actions"><a class="button button-primary" href="#concentration">Review concentration</a><a class="button button-secondary" href="downloads/private_nonprofit_growth.csv">Download institution table</a></div><p class="release-note"><strong>Decision rule:</strong> classify the shift as concentrated only if the top 10 institutions account for at least 50% of gross positive movement. Current result: <strong>{html.escape(str(summary['decision']))}</strong>.</p><div class="handoff-summary"><article><strong>{signed(int(summary['net']))}</strong><span>private nonprofit net change</span></article><article><strong>{signed(int(summary['graduate_change']))}</strong><span>graduate contribution</span></article><article><strong>{summary['positive_count']}</strong><span>positive institution contributors</span></article><article><strong>{summary['top10_share_pct']:.1f}%</strong><span>top-10 share of gross positive movement</span></article></div></div></section>
    <section class="section shell" id="concentration"><div class="section-heading"><p class="eyebrow">Concentration test</p><h2>{html.escape(str(summary['decision']))}.</h2><p>The top 10 account for {summary['top10_share_pct']:.1f}% of gross positive movement; {summary['outside_top10_share_pct']:.1f}% occurs outside them. The sector also contains {summary['negative_count']} institutions with negative endpoint contributions, totaling {summary['gross_negative']:,} students of offsetting movement.</p></div><div class="method-grid"><article><h3>Top 1 / top 5</h3><p><strong>{summary['top1_share_pct']:.1f}% / {summary['top5_share_pct']:.1f}%</strong><br>Share of gross positive institution movement.</p></article><article><h3>Top 10 / top 25</h3><p><strong>{summary['top10_share_pct']:.1f}% / {summary['top25_share_pct']:.1f}%</strong><br>Share of gross positive institution movement.</p></article><article><h3>Gross movement</h3><p><strong>{summary['gross_positive']:,} positive</strong><br>{summary['gross_negative']:,} negative; difference = {signed(int(summary['net']))} net.</p></article><article><h3>Effective contributors</h3><p><strong>{summary['effective_contributors']:.1f}</strong><br>Inverse-HHI equivalent count from positive institution contributions.</p></article></div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading"><p class="eyebrow">Largest positive contributors</p><h2>The leading institutions matter, but they do not necessarily define the sector result.</h2><p>Shares below use gross positive movement as the denominator. Endpoint status identifies contributors that entered the private-nonprofit sector universe, which can reflect control or universe change rather than institution-level enrollment growth. The QA gate is inherited from the current latest-release review so a held institution can remain in aggregate accounting without being treated as a cleared institution-specific narrative claim.</p></div><div class="table-wrap"><table><thead><tr><th>Rank</th><th>Institution</th><th>State</th><th>Change</th><th>UG / Grad change</th><th>Share</th><th>Cumulative</th><th>Endpoint status</th><th>Latest-release QA gate</th></tr></thead><tbody>{top_table_html(summary['positive'])}</tbody></table></div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Accounting and interpretation</p><h2>The sector total is reconciled before concentration is interpreted.</h2></div><div class="method-grid"><article><h3>Student level</h3><p>Undergraduate {signed(int(summary['undergraduate_change']))} + graduate {signed(int(summary['graduate_change']))} = {signed(int(summary['net']))}.</p></article><article><h3>Endpoint accounting</h3><p>Continuing {signed(int(summary['continuing_change']))} + entering {summary['entered_enrollment']:,} - exiting {summary['exited_enrollment']:,} = {signed(int(summary['net']))}.</p></article><article><h3>QA boundary</h3><p>High-priority latest-release records retain their existing analyst publication gate; aggregate inclusion does not clear institution-specific interpretation.</p></article><article><h3>Threshold</h3><p>The top-10 majority rule is an explicit project decision rule, not a universal statistical standard.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/private_nonprofit_growth.csv">Download institution CSV</a><a class="button button-secondary" href="downloads/private_nonprofit_growth.md">Download analysis notes</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Private Nonprofit Growth · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows = build_rows()
    summary = summarize(rows)
    write_csv(rows)
    write_markdown(rows)
    write_html(rows)
    print(
        "Private nonprofit growth: "
        f"net={signed(int(summary['net']))}; positive contributors={summary['positive_count']}; "
        f"top10 share={summary['top10_share_pct']:.1f}%; decision={summary['decision']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
