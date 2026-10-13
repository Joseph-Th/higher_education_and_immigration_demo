"""Validate and publish the population/source definitions crosswalk."""

from __future__ import annotations

import csv
import html
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "population_crosswalk.csv"
DOC_OUTPUT = ROOT / "docs" / "POPULATION_CROSSWALK.md"
HTML_OUTPUT = ROOT / "site" / "methodology-crosswalk.html"

FIELDS = (
    "population_id",
    "population_label",
    "measure_type",
    "primary_source",
    "current_vintage",
    "unit_of_analysis",
    "inclusion_rule",
    "explicit_exclusions",
    "geography",
    "best_use",
    "comparison_warning",
    "project_status",
    "source_url",
    "last_checked",
)

REQUIRED_IDS = {
    "ipeds_us_nonresident",
    "immigrant_origin",
    "international_sevis",
    "undocumented_higher_ed",
    "undocumented_hs_graduates",
    "refugee_asylee",
}


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(f"Population crosswalk schema mismatch: {reader.fieldnames}")
        rows = list(reader)

    ids = [row["population_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Population crosswalk IDs must be unique")
    if set(ids) != REQUIRED_IDS:
        raise RuntimeError(f"Population crosswalk must contain the required populations: {REQUIRED_IDS}")

    for row in rows:
        for field in FIELDS:
            if not row[field].strip():
                raise RuntimeError(f"Blank {field} in {row['population_id']}")
        parsed = urlparse(row["source_url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError(f"Crosswalk source must be HTTPS: {row['source_url']}")
        date.fromisoformat(row["last_checked"])

    by_id = {row["population_id"]: row for row in rows}
    ipeds = by_id["ipeds_us_nonresident"]
    if "undocumented" not in ipeds["explicit_exclusions"].lower():
        raise RuntimeError("IPEDS crosswalk row must explicitly document undocumented-student exclusion")

    lines = [
        "# Population and Source Crosswalk",
        "",
        "This crosswalk prevents a common analytical error in higher-education immigration research: treating datasets with similar labels as if they measure the same population. The structured authority is `data/population_crosswalk.csv`; this document is generated from it.",
        "",
        "## Decision rule",
        "",
        "A source can be compared directly with the project series only when population definition, reference period, unit of analysis, geography, and denominator are compatible. Otherwise it is contextual evidence, a separate companion series, or a documented data need.",
        "",
        "| Population | Measurement | Current vintage | Best use | Project status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| [{row['population_label']}]({row['source_url']}) | {row['measure_type']} | "
            f"{row['current_vintage']} | {row['best_use']} | {row['project_status']} |"
        )

    lines.extend(["", "## Population notes", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['population_label']}",
                "",
                f"- **Primary source:** {row['primary_source']}",
                f"- **Unit of analysis:** {row['unit_of_analysis']}",
                f"- **Included:** {row['inclusion_rule']}",
                f"- **Excluded / not identified:** {row['explicit_exclusions']}",
                f"- **Geography:** {row['geography']}",
                f"- **Comparison warning:** {row['comparison_warning']}",
                f"- **Source checked:** {row['last_checked']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Implication for this project",
            "",
            "The current longitudinal analysis intentionally stays with IPEDS U.S. nonresident enrollment because that measure is institution-reported, annual, and available consistently across the full period. The crosswalk identifies where a separate companion analysis would require CPS, ACS-derived estimates, SEVIS, or another population-specific source rather than relabeling the IPEDS series.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    cards = []
    for row in rows:
        cards.append(
            f"""
            <article class="crosswalk-card" id="population-{html.escape(row['population_id'])}">
              <div class="crosswalk-card-head">
                <p class="case-kicker">{html.escape(row['project_status'])}</p>
                <h2>{html.escape(row['population_label'])}</h2>
                <p class="crosswalk-measure">{html.escape(row['measure_type'])}</p>
              </div>
              <dl class="crosswalk-definition-list">
                <div><dt>Current source / vintage</dt><dd>{html.escape(row['primary_source'])}<br><small>{html.escape(row['current_vintage'])}</small></dd></div>
                <div><dt>Who is included?</dt><dd>{html.escape(row['inclusion_rule'])}</dd></div>
                <div><dt>What is excluded or not identified?</dt><dd>{html.escape(row['explicit_exclusions'])}</dd></div>
                <div><dt>Best use</dt><dd>{html.escape(row['best_use'])}</dd></div>
              </dl>
              <div class="crosswalk-warning"><strong>Comparison rule</strong><p>{html.escape(row['comparison_warning'])}</p></div>
              <a class="crosswalk-source" href="{html.escape(row['source_url'], quote=True)}" target="_blank" rel="noopener">Review source methodology</a>
            </article>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Population and source crosswalk for higher-education immigration data, including IPEDS, immigrant-origin, international, undocumented, and refugee/asylee measures.">
  <meta name="theme-color" content="#10263c">
  <title>Population & Source Crosswalk | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to crosswalk</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Crosswalk navigation"><a href="index.html">Brief</a><a href="research-memo.html">Memo</a><a href="index.html#methods">Methods</a><a href="index.html#downloads">Data</a></nav></div></header>
  <main id="main">
    <section class="crosswalk-hero"><div class="shell"><p class="eyebrow">Methods crosswalk</p><h1>Similar labels do not mean the same population.</h1><p class="lede">A source-selection guide for IPEDS U.S. nonresident, immigrant-origin, international, undocumented, high-school pipeline, and refugee/asylee research.</p><div class="hero-actions"><a class="button button-primary" href="#crosswalk-cards">Compare definitions</a><a class="button button-secondary" href="downloads/population_crosswalk.csv">Download structured crosswalk</a></div></div></section>
    <section class="section shell crosswalk-intro"><div class="section-heading"><p class="eyebrow">Decision rule</p><h2>Compare only after definitions and denominators line up</h2><p>The current project uses IPEDS because it provides a consistent annual institution-reported series. Other Portal populations often require survey estimation, legal-status modeling, or different administrative systems. Those sources can answer important questions, but they should not be merged into one series merely because all relate to immigration and higher education.</p></div><div class="crosswalk-rule-grid"><article><strong>1</strong><span>Check population definition</span></article><article><strong>2</strong><span>Check reference period</span></article><article><strong>3</strong><span>Check geography and unit</span></article><article><strong>4</strong><span>Check denominator and exclusions</span></article></div></section>
    <section class="section section-tinted" id="crosswalk-cards"><div class="shell"><div class="section-heading"><p class="eyebrow">Population definitions</p><h2>Six research concepts, six different measurement rules</h2><p>Each card states what the source measures, what it excludes, and whether the current IPEDS analysis can support a direct comparison.</p></div><div class="crosswalk-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Research implication</p><h2>Use the right source for the question</h2></div><div class="method-grid"><article><h3>Current longitudinal series</h3><p>Use IPEDS U.S. nonresident when the question is annual institution/state/national enrollment under the IPEDS reporting definition.</p></article><article><h3>Domestic immigrant-origin students</h3><p>Use the CPS/MPI framework when the question concerns first- and second-generation domestic students rather than temporary-study visa holders.</p></article><article><h3>Undocumented students</h3><p>Use report-specific ACS-based estimates and preserve their modeled-estimate limitations instead of treating IPEDS visa categories as a proxy.</p></article><article><h3>Refugee/asylee students</h3><p>Do not make subgroup claims from this project. A population-specific source is needed because the current series does not identify refugee or asylum status.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/population_crosswalk.md">Download methodology notes</a><a class="button button-secondary" href="index.html#methods">Return to project methods</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Population & Source Crosswalk</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"Population crosswalk: {len(rows)} definitions")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
