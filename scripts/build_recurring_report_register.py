"""Validate and publish the recurring-report operations register."""

from __future__ import annotations

import csv
import html
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE = DATA / "recurring_report_register.csv"
DOC_OUTPUT = ROOT / "docs" / "RECURRING_REPORT_REGISTER.md"
HTML_OUTPUT = ROOT / "site" / "research-operations.html"

FIELDS = (
    "report_id",
    "report_title",
    "population_id",
    "research_library_id",
    "partner_context",
    "latest_publication_date",
    "latest_data_vintage",
    "schedule_status",
    "portfolio_stage",
    "monitoring_trigger",
    "intake_requirements",
    "method_change_check",
    "qa_gate",
    "publication_outputs",
    "next_action",
    "last_reviewed",
)

REQUIRED_IDS = {
    "undocumented_higher_ed",
    "immigrant_origin_higher_ed",
    "undocumented_hs_graduates",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(f"Recurring-report register schema mismatch: {reader.fieldnames}")
        rows = list(reader)

    ids = [row["report_id"] for row in rows]
    if set(ids) != REQUIRED_IDS or len(ids) != len(set(ids)):
        raise RuntimeError("Recurring-report register must contain exactly the three required report IDs")

    library = {row["resource_id"]: row for row in read_csv(DATA / "research_library.csv")}
    populations = {row["population_id"]: row for row in read_csv(DATA / "population_crosswalk.csv")}

    enriched: list[dict[str, str]] = []
    for row in rows:
        for field in FIELDS:
            if not row[field].strip():
                raise RuntimeError(f"Blank {field} in recurring report {row['report_id']}")
        date.fromisoformat(row["latest_publication_date"])
        date.fromisoformat(row["last_reviewed"])
        if row["research_library_id"] not in library:
            raise RuntimeError(
                f"Unknown Research Library foreign key for {row['report_id']}: {row['research_library_id']}"
            )
        if row["population_id"] not in populations:
            raise RuntimeError(
                f"Unknown population-crosswalk foreign key for {row['report_id']}: {row['population_id']}"
            )
        if "confirm" not in row["schedule_status"].lower():
            raise RuntimeError(
                f"Recurring-report schedule must avoid inventing an unverified fixed cadence: {row['report_id']}"
            )
        enriched.append(
            {
                **row,
                "source_title": library[row["research_library_id"]]["title"],
                "source_url": library[row["research_library_id"]]["url"],
                "population_label": populations[row["population_id"]]["population_label"],
            }
        )

    lines = [
        "# Recurring Research Product Operations Register",
        "",
        "This is a portfolio operations model for the three recurring research products named in the target role. It does **not** claim access to, responsibility for, or knowledge of the Presidents' Alliance's internal production schedule. Its purpose is to show how partner-delivered research would be tracked, reviewed, documented, and moved toward publication without inventing deadlines or changing source values.",
        "",
        "## Current product register",
        "",
        "| Product | Population | Latest publication | Current data vintage | Portfolio stage |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in enriched:
        lines.append(
            f"| [{row['report_title']}]({row['source_url']}) | {row['population_label']} | "
            f"{row['latest_publication_date']} | {row['latest_data_vintage']} | {row['portfolio_stage']} |"
        )

    lines.extend(
        [
            "",
            "## Shared production lifecycle",
            "",
            "1. **Kickoff and scope lock:** confirm partner contacts, roles, decision owner, delivery format, milestones, current population definition, and release target. Do not infer an annual deadline from a prior publication date.",
            "2. **Versioned intake:** preserve the delivered files, codebook/model notes, prior methodology, change log, table shells, and uncertainty/suppression rules as one dated package before analysis begins.",
            "3. **Method-change review:** compare definitions, source vintage, geography, denominators, weighting/model rules, exclusions, and table structure with the prior published product and the population crosswalk.",
            "4. **Reproduction and QA:** reproduce partner headline totals from the delivered package, reconcile component tables, compare with the prior report, and open a discrepancy log for every unexplained material break.",
            "5. **Analyst review:** separate confirmed findings from unresolved issues; document questions sent back to the partner and the evidence used to close them.",
            "6. **Publication gate:** update methodology/source notes, tables, Portal content, and citations only after material discrepancies are resolved or explicitly disclosed and the designated reviewer/sign-off owner approves the product.",
            "7. **Archive and handoff:** preserve the final source package, reviewed tables, methodology version, discrepancy log, approval record, and publication URL so the next cycle starts from known institutional knowledge.",
            "",
            "## Product-specific review notes",
            "",
        ]
    )
    for row in enriched:
        lines.extend(
            [
                f"### {row['report_title']}",
                "",
                f"- **Partner context:** {row['partner_context']}",
                f"- **Schedule rule:** {row['schedule_status']}",
                f"- **Monitoring trigger:** {row['monitoring_trigger']}",
                f"- **Intake package:** {row['intake_requirements']}",
                f"- **Method-change check:** {row['method_change_check']}",
                f"- **QA gate:** {row['qa_gate']}",
                f"- **Expected publication outputs:** {row['publication_outputs']}",
                f"- **Next action:** {row['next_action']}",
                "",
            ]
        )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    cards = []
    for row in enriched:
        cards.append(
            f"""
            <article class="operations-card">
              <p class="case-kicker">{html.escape(row['population_label'])}</p>
              <h2>{html.escape(row['report_title'])}</h2>
              <dl class="operations-meta">
                <div><dt>Latest publication</dt><dd>{html.escape(row['latest_publication_date'])}</dd></div>
                <div><dt>Current data vintage</dt><dd>{html.escape(row['latest_data_vintage'])}</dd></div>
                <div><dt>Partner context</dt><dd>{html.escape(row['partner_context'])}</dd></div>
                <div><dt>Schedule rule</dt><dd>{html.escape(row['schedule_status'])}</dd></div>
              </dl>
              <div class="operations-gate"><strong>QA gate</strong><p>{html.escape(row['qa_gate'])}</p></div>
              <p class="operations-next"><strong>Next action:</strong> {html.escape(row['next_action'])}</p>
              <a class="crosswalk-source" href="{html.escape(row['source_url'], quote=True)}" target="_blank" rel="noopener">Open current public product</a>
            </article>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Portfolio recurring-report operations model for three higher-education immigration research products.">
  <meta name="theme-color" content="#10263c">
  <title>Recurring Research Operations | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to recurring research operations</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Research operations navigation"><a href="index.html">Brief</a><a href="research-memo.html">Memo</a><a href="methodology-crosswalk.html">Crosswalk</a><a href="index.html#downloads">Data</a></nav></div></header>
  <main id="main">
    <section class="operations-hero"><div class="shell"><p class="eyebrow">Research operations</p><h1>Recurring reports need a repeatable handoff, not a memory of last year.</h1><p class="lede">A portfolio model for partner intake, method-change review, quantitative QA, publication gating, and institutional-knowledge handoff across the three recurring products named in the target role.</p><div class="hero-actions"><a class="button button-primary" href="#report-register">Review product register</a><a class="button button-secondary" href="downloads/recurring_report_register.csv">Download operations register</a></div><p class="release-note"><strong>Portfolio demonstration:</strong> this page models a defensible workflow from public information. It does not represent the Presidents' Alliance's internal schedule or claim responsibility for these reports.</p></div></section>
    <section class="section shell operations-lifecycle"><div class="section-heading"><p class="eyebrow">Shared lifecycle</p><h2>Seven controls from partner kickoff to archive</h2><p>The workflow keeps schedule assumptions, source files, methodology changes, discrepancies, publication decisions, and final handoff explicit.</p></div><ol class="lifecycle-grid"><li><strong>Kickoff</strong><span>Confirm roles, scope, milestones, population, and deliverables.</span></li><li><strong>Intake</strong><span>Version the data, codebook/model notes, change log, and table shells.</span></li><li><strong>Method review</strong><span>Compare definitions, source vintage, weighting/model rules, and exclusions.</span></li><li><strong>Reproduce</strong><span>Rebuild headline totals and reconcile components before interpretation.</span></li><li><strong>Resolve</strong><span>Track partner questions and unexplained breaks to documented closure.</span></li><li><strong>Publish</strong><span>Gate tables, methodology, Portal updates, and citations on QA/sign-off.</span></li><li><strong>Archive</strong><span>Preserve final inputs, review log, approvals, and publication URL.</span></li></ol></section>
    <section class="section section-tinted" id="report-register"><div class="shell"><div class="section-heading"><p class="eyebrow">Current public references</p><h2>Three recurring products, three distinct data-generation methods</h2><p>The operations register links each product to the Research Library and population crosswalk so a method or population change cannot be treated as a routine data refresh.</p></div><div class="operations-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Handoff principle</p><h2>Institutional knowledge is part of the deliverable</h2></div><div class="method-grid"><article><h3>What gets archived</h3><p>Source package, codebook/model notes, methodology version, reviewed tables, discrepancy log, approval record, and publication URL.</p></article><article><h3>What never gets assumed</h3><p>A fixed deadline, unchanged partner role, unchanged methodology, or direct comparability with a prior population/source merely because the report title is similar.</p></article><article><h3>What blocks publication</h3><p>Unreconciled headline totals, unexplained definition changes, missing source lineage, unresolved material discrepancies, or absent review/sign-off ownership.</p></article><article><h3>What starts the next cycle</h3><p>A known prior package, explicit open questions, current source metadata, and a schedule confirmed with the actual partner rather than inferred from history.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/recurring_report_register.md">Download operations notes</a><a class="button button-secondary" href="methodology-crosswalk.html">Population crosswalk</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Recurring Research Operations · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"Recurring report register: {len(enriched)} products")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
