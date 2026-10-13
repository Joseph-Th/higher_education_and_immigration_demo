"""Validate structured source metadata and generate the current Research Library."""

from __future__ import annotations

import csv
import html
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "research_library.csv"
OUTPUT = ROOT / "docs" / "RESEARCH_LIBRARY.md"
HTML_OUTPUT = ROOT / "site" / "research-library.html"

REQUIRED_FIELDS = (
    "resource_id",
    "title",
    "publisher",
    "resource_type",
    "population_tags",
    "workflow_stage",
    "scope",
    "update_pattern",
    "project_role",
    "url",
    "last_checked",
    "status_note",
)


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_FIELDS:
            raise RuntimeError(
                f"Research library schema mismatch: {reader.fieldnames} != {REQUIRED_FIELDS}"
            )
        rows = list(reader)

    if not rows:
        raise RuntimeError("Research library cannot be empty")
    ids = [row["resource_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Research library resource_id values must be unique")

    for row in rows:
        if any(not row[field].strip() for field in REQUIRED_FIELDS):
            raise RuntimeError(f"Blank research-library field in {row['resource_id']}")
        parsed = urlparse(row["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError(f"Research library URL must be HTTPS: {row['url']}")
        date.fromisoformat(row["last_checked"])

    last_checked = max(date.fromisoformat(row["last_checked"]) for row in rows)
    lines = [
        "# Research Library",
        "",
        "This compact library records the external sources used to collect, interpret, validate, and maintain the project. The CSV in `data/research_library.csv` is the structured source; this document is generated from it.",
        "",
        f"**Latest recorded source review:** {last_checked.isoformat()}",
        "",
        "| Resource | Population / topic | Workflow stage | Type | Update pattern | Project role | Last checked |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| [{row['title']}]({row['url']}) | {row['population_tags'].replace(';', ', ')} | "
            f"{row['workflow_stage']} | {row['resource_type']} | {row['update_pattern']} | "
            f"{row['project_role']} | {row['last_checked']} |"
        )

    lines.extend(
        [
            "",
            "## Resource notes",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['title']}",
                "",
                f"- **Publisher:** {row['publisher']}",
                f"- **Population / topic:** {row['population_tags'].replace(';', ', ')}",
                f"- **Workflow stage:** {row['workflow_stage']}",
                f"- **Scope:** {row['scope']}",
                f"- **Project use:** {row['project_role']}",
                f"- **Status note:** {row['status_note']}",
                "",
            ]
        )

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    resource_types = sorted({row["resource_type"] for row in rows})
    publishers = sorted({row["publisher"] for row in rows})
    population_tags = sorted(
        {
            tag.strip()
            for row in rows
            for tag in row["population_tags"].split(";")
            if tag.strip()
        }
    )
    type_options = "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in resource_types
    )
    population_options = "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in population_tags
    )
    publisher_options = "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in publishers
    )

    cards: list[str] = []
    for row in rows:
        searchable = " ".join(
            [
                row["title"],
                row["publisher"],
                row["resource_type"],
                row["population_tags"],
                row["workflow_stage"],
                row["scope"],
                row["project_role"],
                row["status_note"],
            ]
        ).lower()
        tags = [tag.strip() for tag in row["population_tags"].split(";") if tag.strip()]
        tag_markup = "".join(
            f'<span>{html.escape(tag)}</span>' for tag in tags
        )
        cards.append(
            f"""
            <article class="library-card"
                     data-type="{html.escape(row['resource_type'], quote=True)}"
                     data-publisher="{html.escape(row['publisher'], quote=True)}"
                     data-populations="{html.escape(';'.join(tags), quote=True)}"
                     data-search="{html.escape(searchable, quote=True)}">
              <div class="library-card-head">
                <span class="library-type">{html.escape(row['resource_type'])}</span>
                <span class="library-publisher">{html.escape(row['publisher'])}</span>
              </div>
              <h2>{html.escape(row['title'])}</h2>
              <div class="library-population-tags" aria-label="Population tags">{tag_markup}</div>
              <dl class="library-meta">
                <div><dt>Workflow stage</dt><dd>{html.escape(row['workflow_stage'])}</dd></div>
                <div><dt>Scope</dt><dd>{html.escape(row['scope'])}</dd></div>
                <div><dt>Update pattern</dt><dd>{html.escape(row['update_pattern'])}</dd></div>
                <div><dt>Project role</dt><dd>{html.escape(row['project_role'])}</dd></div>
                <div><dt>Status</dt><dd>{html.escape(row['status_note'])}</dd></div>
              </dl>
              <div class="library-card-footer">
                <span>Checked {html.escape(row['last_checked'])}</span>
                <a href="{html.escape(row['url'], quote=True)}" target="_blank" rel="noopener">Open source</a>
              </div>
            </article>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Searchable Research Library for the higher-education immigration data portfolio, including primary data, methodology, benchmarks, and related research products.">
  <meta name="theme-color" content="#10263c">
  <title>Research Library | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to Research Library</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Research Library navigation"><a href="index.html">Brief</a><a href="research-memo.html">Memo</a><a href="methodology-crosswalk.html">Crosswalk</a><a href="research-operations.html">Operations</a></nav></div></header>
  <main id="main">
    <section class="library-hero"><div class="shell"><p class="eyebrow">Research Library</p><h1>Sources should be easy to find and hard to misuse.</h1><p class="lede">A structured library of the primary data, methodology, release-monitoring, benchmark, and related research sources used to build and maintain this portfolio product.</p><div class="library-summary"><article><strong>{len(rows)}</strong><span>maintained resources</span></article><article><strong>{len(population_tags)}</strong><span>population / topic tags</span></article><article><strong>{len(resource_types)}</strong><span>resource types</span></article><article><strong>{last_checked.isoformat()}</strong><span>latest recorded source review</span></article></div></div></section>
    <section class="section shell library-section">
      <div class="section-heading"><p class="eyebrow">Find a source</p><h2>Search by topic, purpose, publisher, or source type</h2><p>The structured CSV remains the authority. This interface exposes the same metadata for research and maintenance workflows.</p></div>
      <div class="library-controls" aria-label="Research Library filters">
        <div class="library-search-control"><label for="library-search">Search resources</label><input id="library-search" type="search" placeholder="e.g. IPEDS, undocumented, benchmark" autocomplete="off"></div>
        <div><label for="library-population-filter">Population / topic</label><select id="library-population-filter"><option value="">All populations</option>{population_options}</select></div>
        <div><label for="library-type-filter">Resource type</label><select id="library-type-filter"><option value="">All types</option>{type_options}</select></div>
        <div><label for="library-publisher-filter">Publisher</label><select id="library-publisher-filter"><option value="">All publishers</option>{publisher_options}</select></div>
        <button id="library-reset" type="button" class="button button-secondary">Reset</button>
      </div>
      <div class="library-results-bar"><strong id="library-result-count">{len(rows)} of {len(rows)} resources</strong><a href="downloads/research_library.csv">Download structured library</a></div>
      <div id="library-grid" class="library-grid">{''.join(cards)}</div>
      <p id="library-empty" class="library-empty" hidden>No resources match the current filters.</p>
    </section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Library governance</p><h2>Metadata is part of source quality</h2></div><div class="method-grid"><article><h3>Scope before citation</h3><p>Each resource records what it measures so similarly named immigration-related populations are not treated as interchangeable.</p></article><article><h3>Update pattern</h3><p>Annual, periodic, and as-released sources are tracked differently; a stale recurring source is a maintenance issue, not a silent assumption.</p></article><article><h3>Project role</h3><p>Primary input, methodology, benchmark, monitoring source, and related research product are separated so validation sources cannot become hidden analytical inputs.</p></article><article><h3>Review date</h3><p>The last-checked field records human source review. Automated URL health checks supplement it but do not update metadata automatically.</p></article></div></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Research Library · {len(rows)} maintained resources</span><a href="index.html">National brief</a></div></footer>
  <script src="research-library.js" defer></script>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"Research library: {len(rows)} resources; latest review {last_checked.isoformat()}")
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
