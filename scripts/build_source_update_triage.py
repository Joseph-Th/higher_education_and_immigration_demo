"""Validate and render the R07 source-update routing register.

The register classifies the expected next change for every maintained Research
Library resource. A baseline route is not a blanket authorization: method,
definition, geography, privacy, or material-conclusion changes escalate before a
routine refresh can proceed.
"""

from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source_update_triage.csv"
LIBRARY = ROOT / "data" / "research_library.csv"
AGENDA = ROOT / "data" / "research_agenda.csv"
DOC_OUTPUT = ROOT / "docs" / "SOURCE_UPDATE_TRIAGE.md"
HTML_OUTPUT = ROOT / "site" / "source-update-triage.html"

FIELDS = (
    "resource_id",
    "baseline_route",
    "baseline_trigger",
    "methodology_escalation",
    "research_question_escalation",
    "affected_surface",
    "review_boundary",
)

ROUTES = (
    "ROUTINE_REFRESH",
    "METHODOLOGY_REVIEW",
    "RESEARCH_QUESTION_REVIEW",
    "GOVERNANCE_REVIEW",
    "MONITOR_ONLY",
    "ARCHIVAL_REFERENCE",
)

ROUTE_LABELS = {
    "ROUTINE_REFRESH": "Routine refresh",
    "METHODOLOGY_REVIEW": "Methodology review",
    "RESEARCH_QUESTION_REVIEW": "Research-question review",
    "GOVERNANCE_REVIEW": "Governance review",
    "MONITOR_ONLY": "Monitor only",
    "ARCHIVAL_REFERENCE": "Archival reference",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(rows: list[dict[str, str]], library: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError("Source-update triage register cannot be empty")
    if tuple(rows[0]) != FIELDS:
        raise RuntimeError("Source-update triage schema mismatch")
    ids = [row["resource_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Source-update triage resource_id values must be unique")
    library_ids = [row["resource_id"] for row in library]
    if set(ids) != set(library_ids) or len(ids) != len(library_ids):
        missing = sorted(set(library_ids) - set(ids))
        extra = sorted(set(ids) - set(library_ids))
        raise RuntimeError(
            f"Source-update triage must cover the Research Library exactly; missing={missing} extra={extra}"
        )
    for row in rows:
        if any(not row[field].strip() for field in FIELDS):
            raise RuntimeError(f"Blank source-update triage field in {row['resource_id']}")
        if row["baseline_route"] not in ROUTES:
            raise RuntimeError(
                f"Unknown source-update route in {row['resource_id']}: {row['baseline_route']}"
            )
        combined = " ".join(row.values()).lower()
        if "deadline" in combined and "not" not in combined:
            raise RuntimeError(f"Source-update triage must not infer deadlines: {row['resource_id']}")

    by_id = {row["resource_id"]: row for row in rows}
    expected_routes = {
        "ipeds_race_ethnicity_definitions": "METHODOLOGY_REVIEW",
        "portal_methodology": "METHODOLOGY_REVIEW",
        "portal_national_data": "RESEARCH_QUESTION_REVIEW",
        "undocumented_higher_ed_2023_aic": "ARCHIVAL_REFERENCE",
        "tuition_equity_privacy_2026": "GOVERNANCE_REVIEW",
    }
    for resource_id, route in expected_routes.items():
        if by_id[resource_id]["baseline_route"] != route:
            raise RuntimeError(f"Required R07 route changed unexpectedly: {resource_id}")

    agenda = {row["research_id"]: row for row in read_rows(AGENDA)}
    if agenda.get("R07", {}).get("status") != "Implemented as source-update triage register":
        raise RuntimeError("R07 agenda status must identify the implemented source-update triage register")


def joined_rows() -> list[dict[str, str]]:
    library = read_rows(LIBRARY)
    triage = read_rows(SOURCE)
    validate(triage, library)
    library_by_id = {row["resource_id"]: row for row in library}
    output: list[dict[str, str]] = []
    for row in triage:
        source = library_by_id[row["resource_id"]]
        output.append(
            {
                **row,
                "title": source["title"],
                "publisher": source["publisher"],
                "workflow_stage": source["workflow_stage"],
                "population_tags": source["population_tags"],
                "update_pattern": source["update_pattern"],
                "last_checked": source["last_checked"],
                "url": source["url"],
            }
        )
    return output


def write_markdown(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["baseline_route"] for row in rows)
    lines = [
        "# Source Update Triage",
        "",
        "R07 asks which external source changes should trigger a routine product refresh, a methodology review, or a new research question. This register covers every maintained Research Library resource and applies a **baseline route plus escalation rules**. A newer file or publication date alone is not evidence that a definition, conclusion, or research question changed.",
        "",
        f"- **Research Library coverage:** {len(rows)}/{len(rows)} resources",
        f"- **Routine-refresh baseline:** {counts['ROUTINE_REFRESH']}",
        f"- **Methodology-review baseline:** {counts['METHODOLOGY_REVIEW']}",
        f"- **Special routes:** {len(rows) - counts['ROUTINE_REFRESH'] - counts['METHODOLOGY_REVIEW']} (research-question, governance, monitor-only, or archival)",
        "- **Inferred deadlines:** 0",
        "",
        "## Decision ladder",
        "",
        "1. **Metadata-only change:** update the source catalog; do not manufacture an analytical finding.",
        "2. **New values/vintage under unchanged methods:** route through the normal refresh, reconciliation, QA, and publication gates.",
        "3. **Definition, denominator, model, schema, geography, or reference-period change:** stop routine trend use and complete methodology review first.",
        "4. **New population/geography or a material conclusion shift under stable methods:** review the research agenda and open/reprioritize a question only when the population, decision need, method, and boundary can be stated explicitly.",
        "5. **Privacy, handling, or release-rule change:** route through data-governance review before changing collection or publication practice.",
        "",
        "## Source-specific routing",
        "",
        "| Source | Baseline route | Expected trigger | Methodology escalation | New-research escalation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| [{row['title']}]({row['url']}) | {ROUTE_LABELS[row['baseline_route']]} | "
            f"{row['baseline_trigger']} | {row['methodology_escalation']} | {row['research_question_escalation']} |"
        )
    lines.extend(
        [
            "",
            "## Operating boundary",
            "",
            "This is a portfolio routing model built from public source metadata. It does **not** represent the Presidents' Alliance's internal refresh schedule, approval workflow, partner delivery calendar, or research-prioritization process. Public publication dates are signals to review; they are not inferred internal deadlines.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["baseline_route"] for row in rows)
    special = len(rows) - counts["ROUTINE_REFRESH"] - counts["METHODOLOGY_REVIEW"]
    cards: list[str] = []
    for row in rows:
        cards.append(
            f"""
          <article class="handoff-card" data-source-route="{html.escape(row['baseline_route'])}">
            <div class="handoff-card-head"><span>{html.escape(row['resource_id'])}</span><span class="library-type">{html.escape(ROUTE_LABELS[row['baseline_route']])}</span></div>
            <p class="case-kicker">{html.escape(row['publisher'])} · {html.escape(row['workflow_stage'])}</p>
            <h2>{html.escape(row['title'])}</h2>
            <dl class="handoff-meta">
              <div><dt>Expected trigger</dt><dd>{html.escape(row['baseline_trigger'])}</dd></div>
              <div><dt>Escalate to methodology review when</dt><dd>{html.escape(row['methodology_escalation'])}</dd></div>
              <div><dt>Review a new research question when</dt><dd>{html.escape(row['research_question_escalation'])}</dd></div>
              <div><dt>Affected surface</dt><dd>{html.escape(row['affected_surface'])}</dd></div>
              <div><dt>Boundary</dt><dd>{html.escape(row['review_boundary'])}</dd></div>
            </dl>
            <a class="crosswalk-source" href="{html.escape(row['url'], quote=True)}" target="_blank" rel="noopener">Open maintained source</a>
          </article>"""
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="R07 source-update triage for routine refresh, methodology review, governance review, and new research-question routing.">
  <meta name="theme-color" content="#10263c">
  <title>Source Update Triage | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to source update triage</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Source update triage navigation"><a href="index.html">Brief</a><a href="research-library.html">Library</a><a href="freshness-monitor.html">Freshness</a><a href="research-operations.html">Operations</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">R07 · source-change routing</p><h1>A new file is a review trigger, not automatically a new finding.</h1><p class="lede">Every maintained source has a default route and explicit escalation conditions. Same-method updates can follow routine refresh controls; changes to definitions, denominators, models, geography, privacy rules, or material conclusions move into a higher review path before public interpretation changes.</p><div class="hero-actions"><a class="button button-primary" href="#routing-rules">Review decision ladder</a><a class="button button-secondary" href="downloads/source_update_triage.csv">Download routing register</a></div><p class="release-note"><strong>Portfolio boundary:</strong> this is a public-source routing model, not the Presidents' Alliance's internal refresh schedule, approval workflow, partner delivery calendar, or prioritization process.</p><div class="handoff-summary"><article><strong>{len(rows)}</strong><span>Research Library sources covered</span></article><article><strong>{counts['ROUTINE_REFRESH']}</strong><span>routine-refresh baselines</span></article><article><strong>{counts['METHODOLOGY_REVIEW']}</strong><span>methodology-review baselines</span></article><article><strong>{special}</strong><span>special routes; 0 inferred deadlines</span></article></div></div></section>
    <section class="section shell" id="routing-rules"><div class="section-heading"><p class="eyebrow">Decision ladder</p><h2>Route the kind of change, not merely the publication date.</h2><p>The first applicable material-change gate controls the review. A routine refresh is available only after higher-order definition and governance questions are cleared.</p></div><ol class="handoff-gates"><li><strong>Metadata only</strong><span>URL, title, or date changes update the catalog without manufacturing a research finding.</span></li><li><strong>Same method, new values</strong><span>Run the normal refresh, reconciliation, QA, and publication gates.</span></li><li><strong>Method changed</strong><span>Definition, denominator, model, schema, geography, or reference-period changes stop routine trend use until reviewed.</span></li><li><strong>Question changed</strong><span>New coverage or a material same-method conclusion shift can open or reprioritize a research question with an explicit decision rule.</span></li><li><strong>Governance changed</strong><span>Privacy, handling, or release-rule changes are reviewed before collection or publication practice changes.</span></li></ol></section>
    <section class="section section-tinted" id="source-map"><div class="shell"><div class="section-heading"><p class="eyebrow">Complete source map</p><h2>All {len(rows)} maintained sources have an explicit route.</h2><p>The register covers the Research Library one-for-one. A source cannot disappear from this routing layer without failing validation.</p></div><div class="handoff-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">R07 outcome</p><h2>Refresh, review methodology, or open a question for a stated reason.</h2></div><div class="method-grid"><article><h3>Routine refresh</h3><p>Use for method-equivalent new IPEDS, benchmark, and recurring-report vintages. Reconciliation and publication QA still apply.</p></article><article><h3>Methodology review</h3><p>Use when definitions, models, denominators, geography, schema, or timing change. Preserve a vintage break rather than splicing incompatible segments.</p></article><article><h3>Research-question review</h3><p>Use when new population/geography coverage makes a held question feasible or a material same-method conclusion shift changes the decision need.</p></article><article><h3>Governance review</h3><p>Use when privacy, handling, or release guidance changes. Do not expand sensitive-data collection by default.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/source_update_triage.csv">Download triage CSV</a><a class="button button-secondary" href="downloads/source_update_triage.md">Download routing note</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Source Update Triage · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows = joined_rows()
    write_markdown(rows)
    write_html(rows)
    counts = Counter(row["baseline_route"] for row in rows)
    print(
        "Source update triage: "
        f"{len(rows)}/{len(rows)} sources covered; "
        f"routine={counts['ROUTINE_REFRESH']}; methodology={counts['METHODOLOGY_REVIEW']}; "
        "inferred deadlines=0"
    )
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
