"""Validate and publish the recurring partner-production cycle controls."""

from __future__ import annotations

import csv
import html
from pathlib import Path

from validate_production_cycle_log import (
    MATERIALITIES,
    RECORD_TYPES,
    STATUSES,
    read_log,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE = DATA / "production_cycle_register.csv"
REPORTS = DATA / "recurring_report_register.csv"
LOG_TEMPLATE = DATA / "production_cycle_log_template.csv"
DOC_OUTPUT = ROOT / "docs" / "PRODUCTION_CYCLE.md"
HTML_OUTPUT = ROOT / "site" / "production-cycle.html"

FIELDS = (
    "stage_order",
    "stage_id",
    "stage_label",
    "coordination_role",
    "entry_condition",
    "required_record",
    "blocking_condition",
    "exit_condition",
    "next_stage_id",
    "retained_evidence",
)

STAGE_IDS = (
    "kickoff_scope_lock",
    "versioned_intake",
    "method_change_review",
    "reproduction_qa",
    "discrepancy_resolution",
    "publication_gate",
    "archive_handoff",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_stages(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(rows) != len(STAGE_IDS):
        raise RuntimeError("Production cycle must contain exactly seven stages")
    if tuple(row["stage_id"] for row in rows) != STAGE_IDS:
        raise RuntimeError("Production-cycle stage IDs or order do not match the required lifecycle")
    if [int(row["stage_order"]) for row in rows] != list(range(1, len(STAGE_IDS) + 1)):
        raise RuntimeError("Production-cycle stage_order must be sequential from 1 through 7")
    for row in rows:
        for field in FIELDS:
            if not row[field].strip():
                raise RuntimeError(f"Blank {field} in production-cycle stage {row['stage_id']}")
    for index, row in enumerate(rows[:-1]):
        if row["next_stage_id"] != rows[index + 1]["stage_id"]:
            raise RuntimeError(f"Broken production-cycle handoff after {row['stage_id']}")
    if rows[-1]["next_stage_id"] != "COMPLETE":
        raise RuntimeError("Archive stage must terminate the current production cycle")
    return rows


def read_stages() -> list[dict[str, str]]:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(f"Production-cycle schema mismatch: {reader.fieldnames}")
        rows = list(reader)
    return validate_stages(rows)


def main() -> int:
    stages = read_stages()
    reports = read_csv(REPORTS)
    log_rows = read_log(LOG_TEMPLATE, allow_empty=True)
    if log_rows:
        raise RuntimeError("Public production-cycle log template must remain empty")
    if len(reports) != 3:
        raise RuntimeError("Production-cycle packet expects the three recurring-report records")
    if any("confirm" not in row["schedule_status"].lower() for row in reports):
        raise RuntimeError("Production-cycle packet cannot infer schedules from public publication dates")

    markdown = [
        "# Partner Research Production Cycle",
        "",
        "This is a portfolio coordination model for the three recurring research products represented in `data/recurring_report_register.csv`. It does **not** represent the Presidents' Alliance's internal project-management system, staffing model, deadlines, or approval chain. The cycle starts only after a real production kickoff or refreshed partner package is confirmed.",
        "",
        f"**Shared control stages:** {len(stages)}",
        f"**Recurring products covered:** {len(reports)}",
        "**Inferred internal deadlines:** 0",
        "",
        "## Stage control register",
        "",
        "| # | Stage | Coordination role | Entry condition | Blocking condition | Exit condition | Retained evidence |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in stages:
        markdown.append(
            f"| {row['stage_order']} | {row['stage_label']} | {row['coordination_role']} | "
            f"{row['entry_condition']} | {row['blocking_condition']} | {row['exit_condition']} | "
            f"{row['retained_evidence']} |"
        )

    markdown.extend(
        [
            "",
            "## Product kickoff packet",
            "",
            "The shared stages define how work advances; the recurring-report register defines what must be checked for each product.",
            "",
        ]
    )
    for report in reports:
        markdown.extend(
            [
                f"### {report['report_title']}",
                "",
                f"- **Current portfolio position:** {report['portfolio_stage']}",
                f"- **Trigger for a real cycle:** {report['monitoring_trigger']}",
                f"- **Intake evidence:** {report['intake_requirements']}",
                f"- **Method-change review:** {report['method_change_check']}",
                f"- **QA gate:** {report['qa_gate']}",
                f"- **Expected outputs after approval:** {report['publication_outputs']}",
                f"- **Pre-kickoff next action:** {report['next_action']}",
                "",
            ]
        )

    markdown.extend(
        [
            "## Minimum coordination record",
            "",
            "A live cycle should retain, at minimum, a cycle identifier, report ID, stage, opened date, owner role, question or discrepancy, materiality, evidence requested, response/evidence received, decision, disclosure requirement, status, and closed date. Dates and confirmed ownership belong in the real cycle record only after kickoff; they are intentionally absent from this public blank template.",
            "",
            "### Blank live-cycle log template",
            "",
            "`data/production_cycle_log_template.csv` is an intentionally empty, public CSV template for the minimum coordination record. At real kickoff, copy it to the approved working location and validate the populated copy with `python scripts/validate_production_cycle_log.py <path> --require-records`.",
            "",
            f"- **Record types:** {', '.join(sorted(RECORD_TYPES))}",
            f"- **Materiality values:** {', '.join(sorted(MATERIALITIES))}",
            f"- **Statuses:** {', '.join(sorted(STATUSES))}",
            "- **Handling boundary:** completed partner logs are not part of the public release allowlist and must be reviewed separately before any disclosure.",
            "",
            "## Advancement rule",
            "",
            "Calendar time alone never advances a stage. Work moves forward only when the current stage's required record exists, its blocking conditions are cleared or explicitly carried as a hold/disclosure, and its exit condition is documented.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(markdown), encoding="utf-8")

    stage_cards = []
    for row in stages:
        stage_cards.append(
            f"""
            <article class="handoff-card">
              <div class="handoff-card-head"><span>Stage {html.escape(row['stage_order'])}</span><span class="handoff-status handoff-status-ready">{html.escape(row['stage_id'])}</span></div>
              <p class="case-kicker">{html.escape(row['coordination_role'])}</p>
              <h2>{html.escape(row['stage_label'])}</h2>
              <dl class="handoff-meta">
                <div><dt>Entry</dt><dd>{html.escape(row['entry_condition'])}</dd></div>
                <div><dt>Required record</dt><dd>{html.escape(row['required_record'])}</dd></div>
                <div><dt>Stop if</dt><dd>{html.escape(row['blocking_condition'])}</dd></div>
                <div><dt>Exit</dt><dd>{html.escape(row['exit_condition'])}</dd></div>
              </dl>
              <p class="operations-next"><strong>Retain:</strong> {html.escape(row['retained_evidence'])}</p>
            </article>"""
        )

    product_cards = []
    for report in reports:
        product_cards.append(
            f"""
            <article class="operations-card">
              <p class="case-kicker">Pre-kickoff portfolio state</p>
              <h2>{html.escape(report['report_title'])}</h2>
              <dl class="operations-meta">
                <div><dt>Current position</dt><dd>{html.escape(report['portfolio_stage'])}</dd></div>
                <div><dt>Cycle trigger</dt><dd>{html.escape(report['monitoring_trigger'])}</dd></div>
                <div><dt>Intake evidence</dt><dd>{html.escape(report['intake_requirements'])}</dd></div>
                <div><dt>Method review</dt><dd>{html.escape(report['method_change_check'])}</dd></div>
              </dl>
              <div class="operations-gate"><strong>QA gate</strong><p>{html.escape(report['qa_gate'])}</p></div>
              <p class="operations-next"><strong>Next action:</strong> {html.escape(report['next_action'])}</p>
            </article>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Stage-gated partner research production cycle for recurring higher-education immigration research products.">
  <meta name="theme-color" content="#10263c">
  <title>Production Cycle | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to production cycle</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Production cycle navigation"><a href="index.html">Brief</a><a href="research-operations.html">Operations</a><a href="publication-handoff.html">Handoff</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Partner production cycle</p><h1>Work advances on evidence, not on the calendar.</h1><p class="lede">A stage-gated portfolio model for moving recurring partner research from confirmed kickoff through versioned intake, method review, QA, issue resolution, publication decision, and archival handoff.</p><div class="hero-actions"><a class="button button-primary" href="#cycle-register">Review stage controls</a><a class="button button-secondary" href="downloads/production_cycle_register.csv">Download cycle register</a></div><p class="release-note"><strong>Portfolio boundary:</strong> this is a reusable coordination template. It does not represent the Presidents' Alliance's internal project-management system, staffing, deadlines, or approval chain, and it deliberately infers no internal dates from public publication history.</p><div class="handoff-summary"><article><strong>{len(stages)}</strong><span>stage-gated controls</span></article><article><strong>{len(reports)}</strong><span>recurring products covered</span></article><article><strong>0</strong><span>inferred internal deadlines</span></article><article><strong>1</strong><span>evidence record required at every handoff</span></article></div></div></section>
    <section class="section section-tinted" id="cycle-register"><div class="shell"><div class="section-heading"><p class="eyebrow">Cycle register</p><h2>Seven gates from kickoff to archive</h2><p>Each stage has an entry condition, required record, explicit blocker, exit condition, and retained evidence. A stage cannot be completed merely because time passed.</p></div><div class="handoff-grid">{''.join(stage_cards)}</div></div></section>
    <section class="section shell"><div class="section-heading"><p class="eyebrow">Product packet</p><h2>Shared controls, product-specific evidence</h2><p>The three products remain at a pre-kickoff portfolio position until a real partner cycle is confirmed. Their existing registers supply the source-specific intake, method, and QA requirements.</p></div><div class="operations-grid">{''.join(product_cards)}</div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Coordination record</p><h2>What a live cycle must leave behind</h2></div><div class="method-grid"><article><h3>Intake manifest</h3><p>Cycle/report identifiers, delivered files, versions, source vintage, methodology package, delivery date, and completeness exceptions.</p></article><article><h3>Method-change record</h3><p>Prior/current definitions, weighting or model changes, geography, exclusions, uncertainty rules, and expected comparability impact.</p></article><article><h3>Question / discrepancy log</h3><p>Owner role, materiality, evidence request, response, decision, disclosure need, status, and closure date.</p></article><article><h3>Approval + archive</h3><p>Final reviewed outputs, methodology version, publication handoff, approval or hold decision, publication URL, and next-cycle open questions.</p></article></div><div class="section-heading compact"><p class="eyebrow">Operational template</p><h2>Start a real cycle with a controlled log</h2><p>The downloadable CSV is intentionally empty. Copy it into the approved working location at kickoff, then validate populated records against the three report IDs, seven stage IDs, controlled record types, materiality values, statuses, and date rules.</p></div><div class="method-grid"><article><h3>Foreign-key controls</h3><p>Every populated row must reference one of the three recurring report IDs and one of the seven production stage IDs.</p></article><article><h3>Controlled record types</h3><p>{html.escape(', '.join(sorted(RECORD_TYPES)))}</p></article><article><h3>Status discipline</h3><p>{html.escape(', '.join(sorted(STATUSES)))}. Terminal records require a close date; active records cannot carry one.</p></article><article><h3>Public boundary</h3><p>The blank template is public. Completed partner logs are nonpublic by default and require a separate release decision before disclosure.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/production_cycle_log_template.csv">Download blank cycle log</a><a class="button button-secondary" href="downloads/production_cycle.md">Download production-cycle notes</a><a class="button button-secondary" href="research-operations.html">Product operations</a></div><p class="release-note">No named staff, internal dates, or unverified approval roles are asserted by this portfolio model. Those fields belong to the actual production record after kickoff.</p></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Partner Production Cycle · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")

    print(f"Production cycle: {len(stages)} stages; {len(reports)} recurring products")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
