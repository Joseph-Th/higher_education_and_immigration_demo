"""Build the bounded R06 2023 undocumented pipeline context.

The comparison is ecological and same-year. Annual undocumented high-school
graduates are a flow; undocumented higher-education enrollment is a stock. The
builder therefore exposes geographic concentration and a descriptive stock/flow
scale multiple, but never constructs a college-going, transition, persistence,
or causal rate.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "undocumented_pipeline_reference.csv"
LIBRARY = ROOT / "data" / "research_library.csv"
AGENDA = ROOT / "data" / "research_agenda.csv"
CSV_OUTPUT = ROOT / "data" / "undocumented_pipeline_comparison.csv"
DOC_OUTPUT = ROOT / "docs" / "UNDOCUMENTED_PIPELINE_CONTEXT.md"
HTML_OUTPUT = ROOT / "site" / "undocumented-pipeline.html"

REFERENCE_FIELDS = (
    "geography_id",
    "geography_name",
    "coverage_class",
    "high_school_graduates_annual_2023",
    "higher_ed_enrollment_2023",
    "hs_research_library_id",
    "he_research_library_id",
    "hs_source_url",
    "he_source_url",
    "source_note",
)

OUTPUT_FIELDS = (
    "state",
    "state_name",
    "high_school_graduates_annual_2023",
    "higher_ed_enrollment_2023",
    "hs_national_share_pct",
    "higher_ed_national_share_pct",
    "share_gap_pp",
    "stock_flow_scale_multiple",
    "hs_rank",
    "higher_ed_rank_within_overlap",
    "rank_gap",
    "hs_research_library_id",
    "he_research_library_id",
    "interpretation_gate",
)

EXPECTED_STATE_VALUES = {
    "TX": ("Texas", 12_000, 73_379),
    "CA": ("California", 11_000, 102_938),
    "FL": ("Florida", 8_000, 49_356),
    "NY": ("New York", 4_000, 31_452),
    "NJ": ("New Jersey", 3_000, 19_420),
    "MD": ("Maryland", 3_000, 11_675),
    "MA": ("Massachusetts", 3_000, 12_519),
    "VA": ("Virginia", 3_000, 13_122),
    "GA": ("Georgia", 3_000, 17_303),
    "IL": ("Illinois", 3_000, 27_672),
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_reference(rows: list[dict[str, str]]) -> None:
    if len(rows) != 11:
        raise RuntimeError("R06 reference must contain one national row and ten state rows")
    if tuple(rows[0]) != REFERENCE_FIELDS:
        raise RuntimeError("R06 reference schema mismatch")
    ids = [row["geography_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("R06 geography_id values must be unique")
    if set(ids) != {"US", *EXPECTED_STATE_VALUES}:
        raise RuntimeError("R06 reference geography set changed unexpectedly")

    library = {row["resource_id"]: row for row in read_rows(LIBRARY)}
    for row in rows:
        if any(not row[field].strip() for field in REFERENCE_FIELDS):
            raise RuntimeError(f"Blank R06 reference field in {row['geography_id']}")
        hs = int(row["high_school_graduates_annual_2023"])
        he = int(row["higher_ed_enrollment_2023"])
        if hs <= 0 or he <= 0:
            raise RuntimeError(f"R06 reference values must be positive: {row['geography_id']}")
        for key in ("hs_source_url", "he_source_url"):
            parsed = urlparse(row[key])
            if parsed.scheme != "https" or not parsed.netloc:
                raise RuntimeError(f"R06 source URL must be HTTPS: {row[key]}")
        for id_field, url_field in (
            ("hs_research_library_id", "hs_source_url"),
            ("he_research_library_id", "he_source_url"),
        ):
            source_id = row[id_field]
            if source_id not in library:
                raise RuntimeError(f"Unknown R06 Research Library ID: {source_id}")
            if library[source_id]["url"] != row[url_field]:
                raise RuntimeError(
                    f"R06 source URL does not match Research Library authority: {row['geography_id']} {source_id}"
                )

    national = next(row for row in rows if row["geography_id"] == "US")
    if (
        national["coverage_class"],
        int(national["high_school_graduates_annual_2023"]),
        int(national["higher_ed_enrollment_2023"]),
    ) != ("national", 75_000, 510_000):
        raise RuntimeError("R06 national denominators changed unexpectedly")
    if national["hs_research_library_id"] != "undocumented_hs_graduates_2026":
        raise RuntimeError("R06 national high-school authority changed unexpectedly")
    if national["he_research_library_id"] != "undocumented_higher_ed_2025":
        raise RuntimeError("R06 national higher-education authority changed unexpectedly")

    by_id = {row["geography_id"]: row for row in rows}
    for state, (name, hs, he) in EXPECTED_STATE_VALUES.items():
        row = by_id[state]
        observed = (
            row["geography_name"],
            int(row["high_school_graduates_annual_2023"]),
            int(row["higher_ed_enrollment_2023"]),
        )
        if observed != (name, hs, he):
            raise RuntimeError(f"R06 fixed 2023 state reference changed unexpectedly: {state}")
        if row["coverage_class"] != "top_high_school_state":
            raise RuntimeError(f"R06 state coverage class mismatch: {state}")
        if row["hs_research_library_id"] != "undocumented_hs_graduates_2026":
            raise RuntimeError(f"R06 state high-school authority mismatch: {state}")
        if row["he_research_library_id"] != "portal_top_states_2023":
            raise RuntimeError(f"R06 state higher-education authority mismatch: {state}")

    agenda = {row["research_id"]: row for row in read_rows(AGENDA)}
    if agenda.get("R06", {}).get("status") != "Implemented as bounded 2023 state pipeline context":
        raise RuntimeError("R06 agenda status must identify the implemented bounded state context")


def min_rank(values: list[int], value: int) -> int:
    ordered = sorted(values, reverse=True)
    return ordered.index(value) + 1


def build_rows() -> tuple[list[dict[str, object]], dict[str, float | int | str]]:
    reference = read_rows(REFERENCE)
    validate_reference(reference)
    national = next(row for row in reference if row["geography_id"] == "US")
    national_hs = int(national["high_school_graduates_annual_2023"])
    national_he = int(national["higher_ed_enrollment_2023"])
    state_rows = [row for row in reference if row["geography_id"] != "US"]
    hs_values = [int(row["high_school_graduates_annual_2023"]) for row in state_rows]
    he_values = [int(row["higher_ed_enrollment_2023"]) for row in state_rows]

    output: list[dict[str, object]] = []
    for row in state_rows:
        hs = int(row["high_school_graduates_annual_2023"])
        he = int(row["higher_ed_enrollment_2023"])
        hs_share = hs / national_hs * 100
        he_share = he / national_he * 100
        hs_rank = min_rank(hs_values, hs)
        he_rank = min_rank(he_values, he)
        output.append(
            {
                "state": row["geography_id"],
                "state_name": row["geography_name"],
                "high_school_graduates_annual_2023": hs,
                "higher_ed_enrollment_2023": he,
                "hs_national_share_pct": round(hs_share, 2),
                "higher_ed_national_share_pct": round(he_share, 2),
                "share_gap_pp": round(he_share - hs_share, 2),
                "stock_flow_scale_multiple": round(he / hs, 2),
                "hs_rank": hs_rank,
                "higher_ed_rank_within_overlap": he_rank,
                "rank_gap": he_rank - hs_rank,
                "hs_research_library_id": row["hs_research_library_id"],
                "he_research_library_id": row["he_research_library_id"],
                "interpretation_gate": "Ecological scale context only; stock/flow multiple is NOT a transition rate.",
            }
        )
    output.sort(key=lambda row: (int(row["hs_rank"]), -int(row["high_school_graduates_annual_2023"]), str(row["state"])))

    hs_sum = sum(int(row["high_school_graduates_annual_2023"]) for row in output)
    he_sum = sum(int(row["higher_ed_enrollment_2023"]) for row in output)
    top4_states = {"TX", "CA", "FL", "NY"}
    top4 = [row for row in output if row["state"] in top4_states]
    top4_hs = sum(int(row["high_school_graduates_annual_2023"]) for row in top4)
    top4_he = sum(int(row["higher_ed_enrollment_2023"]) for row in top4)
    tied = [row for row in output if int(row["high_school_graduates_annual_2023"]) == 3_000]
    tied_he = [int(row["higher_ed_enrollment_2023"]) for row in tied]
    ratios = [float(row["stock_flow_scale_multiple"]) for row in output]
    summary: dict[str, float | int | str] = {
        "national_hs": national_hs,
        "national_he": national_he,
        "state_count": len(output),
        "hs_sum": hs_sum,
        "he_sum": he_sum,
        "hs_share_pct": round(hs_sum / national_hs * 100, 1),
        "he_share_pct": round(he_sum / national_he * 100, 1),
        "top4_hs": top4_hs,
        "top4_he": top4_he,
        "top4_hs_share_pct": round(top4_hs / national_hs * 100, 1),
        "top4_he_share_pct": round(top4_he / national_he * 100, 1),
        "tied_state_count": len(tied),
        "tied_he_min": min(tied_he),
        "tied_he_max": max(tied_he),
        "tied_he_multiple": round(max(tied_he) / min(tied_he), 2),
        "min_scale_multiple": min(ratios),
        "max_scale_multiple": max(ratios),
    }
    if (hs_sum, he_sum, top4_hs, top4_he) != (53_000, 358_836, 35_000, 257_125):
        raise RuntimeError("R06 aggregate reconciliation changed unexpectedly")
    return output, summary


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, object]], summary: dict[str, float | int | str]) -> None:
    lines = [
        "# 2023 Undocumented Student Pipeline Context",
        "",
        "R06 asks what the undocumented high-school graduate pipeline implies for higher-education access questions. The public sources support a **bounded same-year ecological comparison**, not an individual transition analysis. The 2023 high-school measure is an estimated **annual flow** of graduates; the 2023 higher-education measure is an estimated **enrollment stock**. They are not the same people, cohort, or denominator.",
        "",
        f"- **States with explicit values in both 2023 source surfaces:** {summary['state_count']}",
        f"- **Those states' share of the national annual high-school graduate estimate:** {summary['hs_share_pct']:.1f}% ({summary['hs_sum']:,} of {summary['national_hs']:,})",
        f"- **Those states' share of the national undocumented higher-education enrollment estimate:** {summary['he_share_pct']:.1f}% ({summary['he_sum']:,} of {summary['national_he']:,})",
        f"- **Shared leading four states (TX, CA, FL, NY):** {summary['top4_hs_share_pct']:.1f}% of the high-school flow and {summary['top4_he_share_pct']:.1f}% of the higher-education stock",
        f"- **Descriptive stock/annual-flow multiple across the ten states:** {summary['min_scale_multiple']:.1f}x to {summary['max_scale_multiple']:.1f}x — **not a transition rate**",
        "",
        "## What the overlap does show",
        "",
        "The same four states — Texas, California, Florida, and New York — lead both source sets, although California and Texas reverse order between the two measures. The ten published high-school states account for nearly the same national concentration in both measures: 70.7% of the annual graduate flow and 70.4% of the higher-education stock. That supports a narrow geographic-planning observation: the largest state contexts recur across both parts of the education pipeline.",
        "",
        f"The comparison also shows why the two measures cannot be converted into a college-going rate. Six states each have a rounded estimate of 3,000 annual undocumented high-school graduates, while their 2023 undocumented higher-education enrollment estimates range from {summary['tied_he_min']:,} to {summary['tied_he_max']:,}, a {summary['tied_he_multiple']:.2f}x spread. Existing higher-education enrollment includes multiple entering cohorts and continuing students, while the high-school estimate represents one annual graduating flow.",
        "",
        "## State comparison",
        "",
        "| State | 2023 annual HS graduates | 2023 higher-ed enrollment | HS national share | HE national share | Stock / annual-flow scale | HS rank | HE rank in overlap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['state_name']} | {int(row['high_school_graduates_annual_2023']):,} | "
            f"{int(row['higher_ed_enrollment_2023']):,} | {float(row['hs_national_share_pct']):.2f}% | "
            f"{float(row['higher_ed_national_share_pct']):.2f}% | {float(row['stock_flow_scale_multiple']):.2f}x | "
            f"{row['hs_rank']} | {row['higher_ed_rank_within_overlap']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- **NOT A RATE:** dividing higher-education enrollment stock by annual high-school graduate flow does not estimate college-going, persistence, completion, or transition probability.",
            "- **Ecological only:** the datasets do not link the same individuals and cannot show whether a state's graduates enrolled in that state, elsewhere, or at all.",
            "- **No causal policy claim:** this note does not combine current tuition-equity, financial-aid, immigration-policy, or institutional-policy status with the 2023 estimates to infer effects.",
            "- **Rounded source values:** the high-school state estimates are published as rounded counts and may not sum exactly to the national estimate.",
            "- **Fixed 2023 comparison:** the living Portal state page may later update; the reviewed 2023 values are preserved in `data/undocumented_pipeline_reference.csv` so later changes cannot silently rewrite this analysis.",
            "",
            "## Sources",
            "",
            "- Presidents' Alliance / Higher Ed Immigration Portal, *A Generation Threatened* (2026), publishing 2023 annual undocumented high-school graduate estimates.",
            "- Presidents' Alliance / Higher Ed Immigration Portal, *Undocumented Students in U.S. Higher Education* (June 2025), using the 1-year 2023 ACS for the national higher-education denominator.",
            "- Higher Ed Immigration Portal, *Top States by Immigrant & International Students*, 2023 undocumented higher-education state table.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, object]], summary: dict[str, float | int | str]) -> None:
    table_rows = "".join(
        f"<tr><td>{html.escape(str(row['state_name']))}</td><td>{int(row['high_school_graduates_annual_2023']):,}</td>"
        f"<td>{int(row['higher_ed_enrollment_2023']):,}</td><td>{float(row['hs_national_share_pct']):.2f}%</td>"
        f"<td>{float(row['higher_ed_national_share_pct']):.2f}%</td><td>{float(row['stock_flow_scale_multiple']):.2f}x</td>"
        f"<td>{row['hs_rank']}</td><td>{row['higher_ed_rank_within_overlap']}</td></tr>"
        for row in rows
    )
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Bounded 2023 ecological comparison of undocumented high-school graduate estimates and undocumented higher-education enrollment estimates across ten states.">
  <meta name="theme-color" content="#10263c">
  <title>Undocumented Pipeline Context | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to undocumented pipeline context</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Pipeline context navigation"><a href="index.html">Brief</a><a href="population-trends.html">Population trends</a><a href="methodology-crosswalk.html">Crosswalk</a><a href="research-library.html">Sources</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">R06 · bounded 2023 ecological context</p><h1>A shared geography is not an individual transition.</h1><p class="lede">Public 2023 estimates make a state-level pipeline comparison possible for ten states. The high-school measure is an annual flow of graduates; the higher-education measure is an enrollment stock. The comparison can describe where scale is concentrated, but it cannot estimate college-going or policy effects.</p><div class="hero-actions"><a class="button button-primary" href="#state-comparison">Compare states</a><a class="button button-secondary" href="downloads/undocumented_pipeline_comparison.csv">Download comparison table</a></div><p class="release-note"><strong>Interpretation gate:</strong> no individual records are linked. Stock/flow multiples are descriptive scale only and are <strong>NOT A RATE</strong>.</p><div class="handoff-summary"><article><strong>{summary['hs_share_pct']:.1f}%</strong><span>national HS graduate flow in the ten states</span></article><article><strong>{summary['he_share_pct']:.1f}%</strong><span>national higher-ed stock in the same states</span></article><article><strong>{summary['state_count']}</strong><span>states with explicit same-year values</span></article><article><strong>NOT A RATE</strong><span>stock / annual-flow comparison</span></article></div></div></section>
    <section class="section shell"><div class="section-heading"><p class="eyebrow">Geographic overlap</p><h2>The same large state contexts appear in both measures.</h2><p>Texas, California, Florida, and New York are the leading four states in both published source sets, though California and Texas switch order. Together they account for {summary['top4_hs_share_pct']:.1f}% of the national annual high-school graduate flow and {summary['top4_he_share_pct']:.1f}% of the national higher-education enrollment stock.</p></div><div class="method-grid"><article><h3>Annual high-school flow</h3><p><strong>{summary['hs_sum']:,}</strong> graduates across the ten states, or <strong>{summary['hs_share_pct']:.1f}%</strong> of the 75,000 national estimate.</p></article><article><h3>Higher-ed enrollment stock</h3><p><strong>{summary['he_sum']:,}</strong> students across the same ten states, or <strong>{summary['he_share_pct']:.1f}%</strong> of the 510,000 national 2023 estimate.</p></article><article><h3>Same four leaders</h3><p>TX, CA, FL, and NY contribute <strong>{summary['top4_hs']:,}</strong> of the annual graduate flow and <strong>{summary['top4_he']:,}</strong> of the higher-ed stock.</p></article><article><h3>Scale is not conversion</h3><p>Across the ten states, the stock is {summary['min_scale_multiple']:.1f}x to {summary['max_scale_multiple']:.1f}x the annual flow. That range is descriptive, not a transition probability.</p></article></div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading"><p class="eyebrow">Why a rate would be wrong</p><h2>Equal annual flows can sit beside very different enrollment stocks.</h2><p>Six states each have a rounded estimate of 3,000 undocumented high-school graduates. Their same-year undocumented higher-education enrollment estimates range from {summary['tied_he_min']:,} to {summary['tied_he_max']:,}, a {summary['tied_he_multiple']:.2f}x spread. Higher-education enrollment contains multiple cohorts and continuing students; it is not the destination count for one graduating class.</p></div><ol class="handoff-gates"><li><strong>Flow</strong><span>The high-school estimate represents students graduating in an annual period.</span></li><li><strong>Stock</strong><span>The higher-education estimate represents students enrolled at a point/period across multiple cohorts.</span></li><li><strong>No linkage</strong><span>The public aggregates do not identify whether graduates later enrolled, where they enrolled, or whether they persisted.</span></li><li><strong>No causal policy test</strong><span>Policy conditions are not time-aligned or modeled here, so this comparison cannot estimate policy effects.</span></li><li><strong>Rounded estimates</strong><span>Published high-school state values are rounded and may not reconcile exactly to the national total.</span></li></ol></div></section>
    <section class="section shell" id="state-comparison"><div class="section-heading"><p class="eyebrow">2023 state comparison</p><h2>Ten states with explicit values in both source surfaces.</h2><p>The national shares use 75,000 annual undocumented high-school graduates and 510,000 undocumented higher-education students as separate denominators.</p></div><div class="table-wrap"><table><thead><tr><th>State</th><th>Annual HS graduates</th><th>Higher-ed enrollment</th><th>HS national share</th><th>HE national share</th><th>Stock / flow scale</th><th>HS rank</th><th>HE rank</th></tr></thead><tbody>{table_rows}</tbody></table></div><p class="release-note"><strong>NOT A RATE:</strong> the stock / flow column is a scale descriptor only. Do not read it as college-going, transition, persistence, completion, or access probability.</p></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading"><p class="eyebrow">Source and use boundary</p><h2>This answers a geography question, not an individual outcome question.</h2></div><div class="method-grid"><article><h3>High-school flow</h3><p><a href="https://www.higheredimmigrationportal.org/wp-content/uploads/2026/02/A-Geneation-Threatened-Undocumented-High-School-Students-Graduate-Feb-2026-final.pdf" target="_blank" rel="noopener">A Generation Threatened</a> publishes the 2023 national and leading-state annual graduate estimates.</p></article><article><h3>Higher-ed stock</h3><p><a href="https://www.higheredimmigrationportal.org/wp-content/uploads/2025/06/Undocumented-Students-in-Higher-Education-June-2025.pdf" target="_blank" rel="noopener">Undocumented Students in U.S. Higher Education</a> provides the fixed 2023 national denominator.</p></article><article><h3>State enrollment</h3><p>The Portal's <a href="https://www.higheredimmigrationportal.org/states/top-states-by-immigrant-international-students/" target="_blank" rel="noopener">Top States</a> table provides the reviewed 2023 state higher-education counts retained in the reference file.</p></article><article><h3>Decision use</h3><p>The overlap identifies states where both pipeline scale and higher-education scale are large enough to justify deeper, method-compatible access research. It does not rank state policy effectiveness.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/undocumented_pipeline_comparison.csv">Download comparison CSV</a><a class="button button-secondary" href="downloads/undocumented_pipeline_context.md">Download analysis notes</a></div></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Undocumented Pipeline Context · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows, summary = build_rows()
    write_csv(rows)
    write_markdown(rows, summary)
    write_html(rows, summary)
    print(
        "Undocumented pipeline context: "
        f"{summary['state_count']} states; HS share={summary['hs_share_pct']:.1f}%; "
        f"HE share={summary['he_share_pct']:.1f}%; stock/flow=NOT A RATE"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
