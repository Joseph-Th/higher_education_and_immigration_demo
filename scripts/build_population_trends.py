"""Build a bounded national comparison across distinct immigration-related populations.

The output deliberately keeps IPEDS U.S. nonresident enrollment, immigrant-origin
survey estimates, and undocumented-student modeled estimates as separate measures.
It permits arithmetic only within a compatible population/source segment and never
constructs a combined immigration-related enrollment total.
"""

from __future__ import annotations

import csv
import html
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "population_trend_reference.csv"
NATIONAL = ROOT / "data" / "processed" / "national_year.csv"
LIBRARY = ROOT / "data" / "research_library.csv"
CSV_OUTPUT = ROOT / "data" / "population_trend_comparison.csv"
DOC_OUTPUT = ROOT / "docs" / "POPULATION_TREND_COMPARISON.md"
HTML_OUTPUT = ROOT / "site" / "population-trends.html"

REFERENCE_FIELDS = (
    "reference_id",
    "population_id",
    "population_label",
    "observation_year",
    "estimate",
    "share_pct",
    "source_vintage",
    "measurement",
    "trend_segment",
    "reported_change_pct",
    "research_library_id",
    "source_url",
    "comparison_note",
)

OUTPUT_FIELDS = (
    "population_id",
    "population_label",
    "observation_year",
    "estimate",
    "share_pct",
    "measurement",
    "source_vintage",
    "trend_segment",
    "segment_start_year",
    "segment_start_value",
    "within_segment_change",
    "within_segment_change_pct",
    "reported_change_pct",
    "research_library_id",
    "source_url",
    "comparison_class",
    "comparison_note",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def validate_reference(rows: list[dict[str, str]]) -> None:
    if len(rows) != 6:
        raise RuntimeError("Population trend reference must contain exactly six external observations")
    ids = [row["reference_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Population trend reference_id values must be unique")
    expected_ids = {"IO2000", "IO2023", "UD2019", "UD2021", "UD2023", "UD2024"}
    if set(ids) != expected_ids:
        raise RuntimeError(f"Population trend reference IDs do not match expected set: {expected_ids}")

    library = {row["resource_id"]: row for row in read_rows(LIBRARY)}
    library_ids = set(library)
    for row in rows:
        if tuple(row) != REFERENCE_FIELDS:
            raise RuntimeError("Population trend reference schema mismatch")
        if row["population_id"] not in {"immigrant_origin", "undocumented_higher_ed"}:
            raise RuntimeError(f"Unexpected comparison population: {row['population_id']}")
        year = int(row["observation_year"])
        estimate = int(row["estimate"])
        if year < 2000 or estimate <= 0:
            raise RuntimeError(f"Invalid reference observation: {row['reference_id']}")
        if row["share_pct"] and not 0 < float(row["share_pct"]) < 100:
            raise RuntimeError(f"Invalid share in {row['reference_id']}")
        if row["reported_change_pct"]:
            float(row["reported_change_pct"])
        parsed = urlparse(row["source_url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError(f"Reference URL must be HTTPS: {row['source_url']}")
        if row["research_library_id"] not in library_ids:
            raise RuntimeError(
                f"Unknown research_library_id in {row['reference_id']}: {row['research_library_id']}"
            )
        if row["source_url"] != library[row["research_library_id"]]["url"]:
            raise RuntimeError(
                f"Source URL does not match Research Library authority for {row['reference_id']}"
            )
        for field in (
            "population_label",
            "source_vintage",
            "measurement",
            "trend_segment",
            "research_library_id",
            "comparison_note",
        ):
            if not row[field].strip():
                raise RuntimeError(f"Blank {field} in {row['reference_id']}")

    by_id = {row["reference_id"]: row for row in rows}
    exact = {
        "IO2000": (2000, 2_900_000, "immigrant_origin_2000_2023"),
        "IO2023": (2023, 5_991_000, "immigrant_origin_2000_2023"),
        "UD2019": (2019, 427_000, "undocumented_2019_2021"),
        "UD2021": (2021, 408_000, "undocumented_2019_2021"),
        "UD2023": (2023, 510_000, "undocumented_2023_2024"),
        "UD2024": (2024, 525_000, "undocumented_2023_2024"),
    }
    for reference_id, (year, estimate, segment) in exact.items():
        row = by_id[reference_id]
        if (int(row["observation_year"]), int(row["estimate"]), row["trend_segment"]) != (
            year,
            estimate,
            segment,
        ):
            raise RuntimeError(f"Reference observation changed unexpectedly: {reference_id}")
    if by_id["IO2023"]["reported_change_pct"] != "107.0":
        raise RuntimeError("Immigrant-origin endpoint must retain the source-reported 107% increase")
    if by_id["UD2021"]["reported_change_pct"] != "-4.2":
        raise RuntimeError("Historical undocumented endpoint must retain source-reported -4.2% change")


def add_segment_math(rows: list[dict[str, object]]) -> None:
    segments: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        segments.setdefault(str(row["trend_segment"]), []).append(row)
    for segment_rows in segments.values():
        segment_rows.sort(key=lambda row: int(row["observation_year"]))
        first = segment_rows[0]
        start_year = int(first["observation_year"])
        start_value = int(first["estimate"])
        for row in segment_rows:
            value = int(row["estimate"])
            row["segment_start_year"] = start_year
            row["segment_start_value"] = start_value
            row["within_segment_change"] = value - start_value
            row["within_segment_change_pct"] = round((value / start_value - 1) * 100, 2)


def build_rows() -> list[dict[str, object]]:
    reference = read_rows(REFERENCE)
    validate_reference(reference)
    national = {int(row["year"]): row for row in read_rows(NATIONAL)}
    missing_years = [year for year in range(2019, 2025) if year not in national]
    if missing_years:
        raise RuntimeError(f"IPEDS national comparison years missing: {missing_years}")

    output: list[dict[str, object]] = []
    for year in range(2019, 2025):
        row = national[year]
        output.append(
            {
                "population_id": "ipeds_us_nonresident",
                "population_label": "IPEDS U.S. nonresident",
                "observation_year": year,
                "estimate": int(row["nonresident_enrollment"]),
                "share_pct": row["nonresident_share_pct"],
                "measurement": "Institution-reported Fall Enrollment administrative count",
                "source_vintage": f"Fall {year} IPEDS complete-data file",
                "trend_segment": "ipeds_2019_2024",
                "segment_start_year": "",
                "segment_start_value": "",
                "within_segment_change": "",
                "within_segment_change_pct": "",
                "reported_change_pct": "",
                "research_library_id": "ipeds_complete_data",
                "source_url": "https://nces.ed.gov/ipeds/help/complete-data-files",
                "comparison_class": "Primary annual series",
                "comparison_note": "Temporary-status U.S. nonresident category; not a proxy for immigrant-origin or undocumented students.",
            }
        )

    for row in reference:
        output.append(
            {
                "population_id": row["population_id"],
                "population_label": row["population_label"],
                "observation_year": int(row["observation_year"]),
                "estimate": int(row["estimate"]),
                "share_pct": row["share_pct"],
                "measurement": row["measurement"],
                "source_vintage": row["source_vintage"],
                "trend_segment": row["trend_segment"],
                "segment_start_year": "",
                "segment_start_value": "",
                "within_segment_change": "",
                "within_segment_change_pct": "",
                "reported_change_pct": row["reported_change_pct"],
                "research_library_id": row["research_library_id"],
                "source_url": row["source_url"],
                "comparison_class": "Contextual companion series",
                "comparison_note": row["comparison_note"],
            }
        )

    add_segment_math(output)
    output.sort(key=lambda row: (str(row["population_id"]), int(row["observation_year"])))
    return output


def write_csv(rows: list[dict[str, object]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def lookup(rows: list[dict[str, object]], population_id: str, year: int) -> dict[str, object]:
    return next(
        row
        for row in rows
        if row["population_id"] == population_id and int(row["observation_year"]) == year
    )


def write_markdown(rows: list[dict[str, object]]) -> None:
    ipeds_2019 = lookup(rows, "ipeds_us_nonresident", 2019)
    ipeds_2024 = lookup(rows, "ipeds_us_nonresident", 2024)
    immigrant_2000 = lookup(rows, "immigrant_origin", 2000)
    immigrant_2023 = lookup(rows, "immigrant_origin", 2023)
    undoc_2019 = lookup(rows, "undocumented_higher_ed", 2019)
    undoc_2021 = lookup(rows, "undocumented_higher_ed", 2021)
    undoc_2023 = lookup(rows, "undocumented_higher_ed", 2023)
    undoc_2024 = lookup(rows, "undocumented_higher_ed", 2024)
    ipeds_2023 = lookup(rows, "ipeds_us_nonresident", 2023)

    lines = [
        "# National Population Trend Comparison",
        "",
        "## Decision boundary",
        "",
        "These are **separate population measures, not one combined enrollment series**. IPEDS U.S. nonresident, immigrant-origin, and undocumented-student estimates use different definitions and data systems. Same-year values are shown only for scale context and **must not be added, subtracted, or interpreted as mutually exclusive categories**.",
        "",
        "## What the compatible segments show",
        "",
        f"- **IPEDS U.S. nonresident:** {int(ipeds_2019['estimate']):,} in 2019 to {int(ipeds_2024['estimate']):,} in 2024, {signed(int(ipeds_2024['within_segment_change']))} ({float(ipeds_2024['within_segment_change_pct']):.1f}%). This is the project's institution-reported annual series.",
        f"- **Immigrant-origin students:** approximately {int(immigrant_2000['estimate']) / 1_000_000:.1f} million in 2000 to {int(immigrant_2023['estimate']):,} in 2023. The source reports a **107%** increase and a rise from about 20% to 32% of higher-education enrollment. Nonimmigrant international students are excluded from this immigrant-origin estimate.",
        f"- **Undocumented students, historical segment:** {int(undoc_2019['estimate']):,} in 2019 to more than {int(undoc_2021['estimate']):,} in 2021. The source reports a **4.2% decline**; rounded headline counts do not exactly reproduce that percentage.",
        f"- **Undocumented students, current segment:** {int(undoc_2023['estimate']):,} in 2023 to {int(undoc_2024['estimate']):,} in 2024, {signed(int(undoc_2024['within_segment_change']))} ({float(undoc_2024['within_segment_change_pct']):.1f}%). The 2024 estimate represents 2.4% of postsecondary students in the current source.",
        "",
        "The project does **not** calculate a 2021-2023 undocumented trend. The historical and current estimates are retained as separate source segments until the underlying modeling vintages are shown to be equivalent enough for a continuous series.",
        "",
        "## 2023 scale context: not addable",
        "",
        "| Population measure | 2023 national estimate | Interpretation |",
        "| --- | ---: | --- |",
        f"| IPEDS U.S. nonresident | {int(ipeds_2023['estimate']):,} | Temporary-status institution-reported category |",
        f"| Immigrant-origin | {int(immigrant_2023['estimate']):,} | Domestic first- and second-generation survey estimate; excludes nonimmigrant international students |",
        f"| Undocumented higher education | {int(undoc_2023['estimate']):,} | Modeled legal-status estimate; conceptually part of the broader first-generation immigrant-origin population |",
        "",
        "These values answer different questions. Their relative size can be described, but they are not components of a single total.",
        "",
        "## Comparison rules",
        "",
        "1. **IPEDS vs immigrant-origin:** not directly comparable. The immigrant-origin measure focuses on domestic first- and second-generation students and excludes nonimmigrant international students, while IPEDS U.S. nonresident captures temporary-status noncitizens under the federal reporting definition.",
        "2. **IPEDS vs undocumented:** not directly comparable. IPEDS U.S. nonresident explicitly does not identify undocumented or DACA students as that category.",
        "3. **Immigrant-origin vs undocumented:** the undocumented population is conceptually included within the broader first-generation immigrant-origin framework, but the estimates come from different surveys/models. Do not subtract one from the other or infer a share without aligned universes and denominators.",
        "4. **State comparison remains held:** IPEDS geography is institution location, while CPS/ACS estimates generally follow student residence. A state-level comparison needs an explicit geography crosswalk rather than assuming equivalence.",
        "",
        "## Source authority",
        "",
        "- IPEDS values: `data/processed/national_year.csv` generated from official NCES complete-data files.",
        "- Immigrant-origin observations: Presidents' Alliance / Migration Policy Institute 2026 report using the 2000 and 2023 CPS October Supplements.",
        "- Historical undocumented observations: American Immigration Council 2023 fact sheet using 2019 and 2021 ACS estimates.",
        "- Current undocumented observations: American Immigration Council 2026 fact sheet using 2023 and 2024 ACS estimates.",
        "- Structured external observations and provenance: `data/population_trend_reference.csv`.",
        "",
    ]
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, object]]) -> None:
    ipeds_2019 = lookup(rows, "ipeds_us_nonresident", 2019)
    ipeds_2023 = lookup(rows, "ipeds_us_nonresident", 2023)
    ipeds_2024 = lookup(rows, "ipeds_us_nonresident", 2024)
    immigrant_2000 = lookup(rows, "immigrant_origin", 2000)
    immigrant_2023 = lookup(rows, "immigrant_origin", 2023)
    undoc_2019 = lookup(rows, "undocumented_higher_ed", 2019)
    undoc_2021 = lookup(rows, "undocumented_higher_ed", 2021)
    undoc_2023 = lookup(rows, "undocumented_higher_ed", 2023)
    undoc_2024 = lookup(rows, "undocumented_higher_ed", 2024)

    ipeds_rows = [row for row in rows if row["population_id"] == "ipeds_us_nonresident"]
    ipeds_max = max(int(row["estimate"]) for row in ipeds_rows)
    ipeds_visual = "".join(
        f"""<div class="population-ipeds-row">
          <strong>{int(row['observation_year'])}</strong>
          <div class="population-ipeds-track"><i style="width:{int(row['estimate']) / ipeds_max * 100:.2f}%"></i></div>
          <span>{int(row['estimate']):,}</span><small>{float(row['share_pct']):.2f}%</small>
        </div>"""
        for row in ipeds_rows
    )

    same_year_values = (
        ("IPEDS U.S. nonresident", int(ipeds_2023["estimate"]), "institution-reported temporary-status category"),
        ("Immigrant-origin", int(immigrant_2023["estimate"]), "domestic first- and second-generation survey estimate"),
        ("Undocumented higher education", int(undoc_2023["estimate"]), "modeled legal-status estimate"),
    )
    same_year_max = max(value for _, value, _ in same_year_values)
    same_year_visual = "".join(
        f"""<div class="population-scale-row">
          <div><strong>{html.escape(label)}</strong><span>{html.escape(note)}</span></div>
          <div class="population-scale-track"><i style="width:{value / same_year_max * 100:.2f}%"></i></div>
          <b>{value:,}</b>
        </div>"""
        for label, value, note in same_year_values
    )

    ipeds_table = "".join(
        f"<tr><td>{int(row['observation_year'])}</td><td>{int(row['estimate']):,}</td><td>{float(row['share_pct']):.2f}%</td></tr>"
        for row in rows
        if row["population_id"] == "ipeds_us_nonresident"
    )
    source_links = {
        row["research_library_id"]: row["source_url"]
        for row in rows
        if row["population_id"] != "ipeds_us_nonresident"
    }
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Bounded national comparison of IPEDS U.S. nonresident, immigrant-origin, and undocumented higher-education trends without combining distinct population measures.">
  <meta name="theme-color" content="#10263c">
  <title>Population Trend Comparison | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to population trend comparison</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Population comparison navigation"><a href="index.html">Brief</a><a href="methodology-crosswalk.html">Crosswalk</a><a href="research-library.html">Sources</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">R04 · bounded national comparison</p><h1>Three population measures should not become one enrollment series.</h1><p class="lede">IPEDS U.S. nonresident, immigrant-origin, and undocumented-student estimates answer different questions. This comparison keeps their definitions and source vintages visible, permits trend arithmetic only inside compatible segments, and uses same-year values only for scale context.</p><div class="hero-actions"><a class="button button-primary" href="#same-year">Compare 2023 scale</a><a class="button button-secondary" href="downloads/population_trend_comparison.csv">Download comparison table</a></div><p class="release-note"><strong>Non-addability rule:</strong> cross-population values are contextual. Do not add, subtract, or treat these measures as mutually exclusive components of a common total.</p><div class="handoff-summary"><article><strong>{float(ipeds_2024['within_segment_change_pct']):+.1f}%</strong><span>IPEDS 2019–2024</span></article><article><strong>+107%</strong><span>immigrant-origin 2000–2023, source reported</span></article><article><strong>{float(undoc_2024['within_segment_change_pct']):+.1f}%</strong><span>undocumented 2023–2024</span></article><article><strong>3</strong><span>separate population measures</span></article></div></div></section>
    <section class="section shell" id="trend-segments"><div class="section-heading"><p class="eyebrow">Compatible trend segments</p><h2>Only method-compatible endpoints are connected.</h2><p>The annual IPEDS series is continuous inside the project universe. Immigrant-origin remains one long source-compatible comparison, while undocumented estimates are intentionally split by vintage.</p></div><div class="population-segment-grid"><article class="population-segment-card"><p class="case-kicker">Continuous project series</p><h3>IPEDS U.S. nonresident</h3><div class="population-endpoints"><span><b>2019</b>{int(ipeds_2019['estimate']):,}</span><i></i><span><b>2024</b>{int(ipeds_2024['estimate']):,}</span></div><strong>{float(ipeds_2024['within_segment_change_pct']):+.1f}%</strong><small>{signed(int(ipeds_2024['within_segment_change']))} within the same administrative series</small></article><article class="population-segment-card"><p class="case-kicker">Source-reported segment</p><h3>Immigrant-origin</h3><div class="population-endpoints"><span><b>2000</b>{int(immigrant_2000['estimate']) / 1_000_000:.1f}M</span><i></i><span><b>2023</b>{int(immigrant_2023['estimate']) / 1_000_000:.3f}M</span></div><strong>+107%</strong><small>source-reported increase; about 20% → 32% of enrollment</small></article><article class="population-segment-card population-undoc-card"><p class="case-kicker">Two separate source segments</p><h3>Undocumented higher education</h3><div class="population-undoc-segment"><span><b>2019</b>{int(undoc_2019['estimate']):,}</span><i></i><span><b>2021</b>&gt;{int(undoc_2021['estimate']):,}</span><strong>−4.2%</strong></div><div class="population-vintage-break"><span>NO 2021–2023 TREND</span></div><div class="population-undoc-segment"><span><b>2023</b>{int(undoc_2023['estimate']):,}</span><i></i><span><b>2024</b>{int(undoc_2024['estimate']):,}</span><strong>{float(undoc_2024['within_segment_change_pct']):+.1f}%</strong></div></article></div><p class="release-note"><strong>Vintage break:</strong> no 2021–2023 undocumented trend is calculated. The 2019–2021 and 2023–2024 published estimates remain separate until model equivalence is established.</p></section>
    <section class="section section-tinted" id="same-year"><div class="shell"><div class="section-heading"><p class="eyebrow">2023 national scale</p><h2>Same year, different measures. Compare scale, not components.</h2><p>Bars use one numeric scale so relative magnitude is visible, but they are deliberately separate rather than stacked. The populations overlap conceptually and use different definitions and denominators.</p></div><div class="population-scale-visual">{same_year_visual}<div class="population-not-addable"><strong>NOT ADDABLE</strong><span>These three values are not mutually exclusive parts of a common total.</span></div></div><div class="method-grid"><article><h3>IPEDS</h3><p>Institution-reported temporary-status U.S. nonresident category. It does not identify undocumented or DACA students as this category.</p></article><article><h3>Immigrant-origin</h3><p>Domestic first- and second-generation survey estimate. Nonimmigrant international students studying temporarily in the U.S. are excluded.</p></article><article><h3>Undocumented</h3><p>Modeled legal-status estimate from ACS microdata. It is conceptually part of the broader first-generation immigrant-origin population, not an independent add-on.</p></article><article><h3>Geography</h3><p>This note stays national. IPEDS uses institution location; CPS/ACS population estimates generally use residence, so state arithmetic is held.</p></article></div></div></section>
    <section class="section shell" id="ipeds-context"><div class="section-heading"><p class="eyebrow">IPEDS annual context</p><h2>The primary project series remains separately reproducible.</h2><p>The six annual observations are shown as their own continuous sequence. External estimates are never spliced into this series.</p></div><div class="population-ipeds-visual">{ipeds_visual}</div><details class="evidence-details population-ipeds-audit"><summary>Inspect the six-year IPEDS values and enrollment shares</summary><div class="table-wrap"><table><thead><tr><th>Year</th><th>U.S. nonresident enrollment</th><th>Share of total enrollment</th></tr></thead><tbody>{ipeds_table}</tbody></table></div></details></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading"><p class="eyebrow">Source and interpretation controls</p><h2>Definitions come before cross-series arithmetic.</h2></div><div class="method-grid"><article><h3>Immigrant-origin source</h3><p>Presidents' Alliance / Migration Policy Institute, CPS October Supplements. <a href="{html.escape(source_links['immigrant_origin_2026'], quote=True)}" target="_blank" rel="noopener">Review source</a>.</p></article><article><h3>Historical undocumented source</h3><p>American Immigration Council, 2019/2021 ACS-based estimates. <a href="{html.escape(source_links['undocumented_higher_ed_2023_aic'], quote=True)}" target="_blank" rel="noopener">Review source</a>.</p></article><article><h3>Current undocumented source</h3><p>American Immigration Council, 2023/2024 ACS-based estimates. <a href="{html.escape(source_links['undocumented_higher_ed_2026_aic'], quote=True)}" target="_blank" rel="noopener">Review source</a>.</p></article><article><h3>Methods authority</h3><p>The six-population <a href="methodology-crosswalk.html">source crosswalk</a> remains the decision rule for whether a comparison is direct, contextual, or held.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/population_trend_comparison.csv">Download comparison CSV</a><a class="button button-secondary" href="downloads/population_trend_comparison.md">Download analysis notes</a></div></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Population Trend Comparison · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows = build_rows()
    write_csv(rows)
    write_markdown(rows)
    write_html(rows)
    current = lookup(rows, "undocumented_higher_ed", 2024)
    immigrant = lookup(rows, "immigrant_origin", 2023)
    print(
        "Population trend comparison: 12 rows; "
        f"2023 immigrant-origin={int(immigrant['estimate']):,}; "
        f"2024 undocumented={int(current['estimate']):,}; cross-population arithmetic=BLOCKED"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
