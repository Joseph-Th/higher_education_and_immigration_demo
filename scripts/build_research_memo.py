"""Generate a reviewer-facing research memo from validated analytical outputs."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC_OUTPUT = ROOT / "docs" / "RESEARCH_MEMO.md"
HTML_OUTPUT = ROOT / "site" / "research-memo.html"

CASE_LABELS = {
    "unresolved_anomaly": "Hold the anomaly",
    "corroborated_movement": "Corroborate the direction",
    "structural_change": "Explain the structural change",
}

CASE_PRINT_SUMMARIES = {
    "unresolved_anomaly": "Exact all-student totals corroborate the institutional frame, but the public source does not expose a comparable U.S. nonresident series. Keep the institution-specific claim held.",
    "corroborated_movement": "Official Fall reporting shows a large same-direction increase on a nearly identical enrollment frame. Keep IPEDS as the numerical authority and publish only bounded direction-level context.",
    "structural_change": "An official closure record explains the institution's exit from the analytic universe. Treat the movement as a structural event rather than unexplained enrollment loss.",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed_int(value: int) -> str:
    return f"{value:+,}" if value else "0"


def signed_pct(value: float) -> str:
    return f"{value:+.1f}%" if value else "0.0%"


def decision_copy(case: dict[str, object]) -> str:
    if case["publication_class"] == "safe_with_context":
        return "Publish with context"
    return "Hold institution-specific claim"


def main() -> int:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "latest_update_review.json").read_text(encoding="utf-8"))
    resolution = json.loads((DATA / "qa_resolution_summary.json").read_text(encoding="utf-8"))
    benchmark = read_csv(DATA / "benchmark_audit.csv")
    undergraduate_baseline = read_csv(DATA / "undergraduate_shift_baseline.csv")

    if not benchmark or any(row["status"] != "PASS" for row in benchmark):
        raise RuntimeError("Cannot publish research memo while external benchmark checks fail")
    cases = resolution.get("case_studies", [])
    if len(cases) != 3 or {case["case_type"] for case in cases} != set(CASE_LABELS):
        raise RuntimeError("Research memo requires the three defined analyst case-study types")
    if len(undergraduate_baseline) != 51:
        raise RuntimeError("Research memo requires the complete 51-state/DC undergraduate baseline")

    coverage = findings["coverage"]
    headline = findings["headline"]
    levels = findings["level_decomposition"]
    recovery = findings["recovery"]
    dynamics = findings["institution_dynamics"]["decade"]
    latest = review["national"]
    accounting = review["institution_accounting"]
    top_gain = review["state_change"]["largest_gains"][0]
    start_year = coverage["start_year"]
    end_year = coverage["end_year"]
    prior_year = review["coverage"]["prior_year"]
    baseline_undergraduate_change = sum(int(row["undergraduate_change"]) for row in undergraduate_baseline)
    baseline_positive_states = sum(int(row["undergraduate_change"]) > 0 for row in undergraduate_baseline)
    baseline_public_change = sum(int(row["public_undergraduate_change"]) for row in undergraduate_baseline)
    if baseline_undergraduate_change != latest["undergraduate_change"]:
        raise RuntimeError("Research memo undergraduate baseline does not reconcile to latest-year change")
    if baseline_positive_states != 45:
        raise RuntimeError("Research memo undergraduate state breadth changed unexpectedly")

    md = [
        f"# Research Memo: U.S. Nonresident Enrollment in Higher Education, {start_year}-{end_year}",
        "",
        f"**Latest data:** Fall {end_year} ({coverage['latest_data_status']})  ",
        "**Universe:** degree-granting institutions in the IPEDS First Look/Digest Title IV universe, 50 states + DC  ",
        f"**QA review date:** {resolution['latest_reviewed_on']}",
        "",
        "## Bottom line",
        "",
        f"U.S. nonresident enrollment reached **{headline['latest_nonresident']:,}** in Fall {end_year}, **{headline['latest_share_pct']:.2f}%** of enrollment in the analytic universe. The national count is **{signed_int(headline['change_since_2015'])} ({signed_pct(headline['change_since_2015_pct'])})** above {start_year}, but the composition of that growth changed: the decade-level increase was entirely graduate-driven, while the newest annual increase was undergraduate-led.",
        "",
        f"From {prior_year} to {end_year}, U.S. nonresident enrollment increased **{signed_int(latest['absolute_change'])} ({signed_pct(latest['pct_change'])})**. Undergraduate enrollment increased **{signed_int(latest['undergraduate_change'])}**, with growth in **{baseline_positive_states} of 51 states/DC** and **{signed_int(baseline_public_change)}** contributed by public institutions, while graduate enrollment declined **{signed_int(latest['graduate_change'])}**. R01 remains a fixed baseline, not a persistence finding: the next complete release must remain positive nationally and in at least **26 of 51 states/DC** before the project calls the shift broadly persistent.",
        "",
        "## Three findings that matter",
        "",
        f"1. **The recovery is real, but it is structurally different.** Graduate enrollment is **{signed_int(levels['graduate_change_students'])}** above {start_year}, while undergraduate enrollment is **{signed_int(levels['undergraduate_change_students'])}** below it. Graduate students now make up the majority of U.S. nonresident enrollment.",
        f"2. **Geography remains uneven.** **{recovery['states_at_or_above_baseline']}** states/DC are at or above their {recovery['baseline_year']} level, while **{recovery['states_below_baseline']}** remain below. {top_gain['state']} posted the largest {prior_year}-{end_year} increase at **{signed_int(top_gain['absolute_change'])}**.",
        f"3. **The growth is not an artifact of a larger institution universe.** Continuing institutions contribute **{signed_int(dynamics['continuing_change'])}** over {start_year}-{end_year}; institution entry and exit net to **{signed_int(dynamics['entry_exit_net'])}**. In the latest year, continuing institutions likewise contribute **{signed_int(accounting['continuing_change'])}** of the national change.",
        "",
        "## Analyst judgment changes what gets published",
        "",
        f"The automated queue identified **{review['review_queue']['high']} high-priority** latest-release records. The manual review layer now covers **{resolution['reviewed_count']}/{resolution['high_priority_total']}** of them: **{resolution['safe_with_context']}** are safe to discuss with explicit context and **{resolution['hold_for_confirmation']}** remain held for institution-specific interpretation. The examples below show why a flag is a review request rather than an error label.",
        "",
    ]
    for case in cases:
        md.extend(
            [
                f"### {CASE_LABELS[str(case['case_type'])]}: {case['institution']}",
                "",
                f"**Observed change:** {signed_int(int(case['absolute_change']))}  ",
                f"**Publication decision:** {decision_copy(case)}  ",
                f"**Evidence:** [{case['evidence_label']}]({case['evidence_url']})",
                "",
                str(case["analyst_note"]),
                "",
            ]
        )

    md.extend(
        [
            "## Interpretation boundary",
            "",
            "IPEDS U.S. nonresident status is a federal reporting category, not a complete measure of international, immigrant-origin, undocumented, DACA, or foreign-born students. The analysis supports enrollment monitoring and publication QA, not causal claims about immigration policy. State totals reflect institution location, and institution structures or reporting practices can change over time.",
            "",
            "The project maintains `docs/POPULATION_CROSSWALK.md` to document which companion sources are appropriate for immigrant-origin, international, undocumented, high-school-pipeline, and refugee/asylee questions rather than treating those populations as interchangeable.",
            "",
            "## Methods and evidence",
            "",
            f"The series uses official NCES/IPEDS Fall Enrollment and institutional directory files for {start_year}-{end_year}. Source archives are hashed and logged, required variables and aggregation labels are audited across years, state/control/student-level totals reconcile to the national series, and **{len(benchmark)}/{len(benchmark)}** independent NCES Digest consistency checks pass. The newest release also receives institution-level reason-coded triage and evidence-backed manual disposition before institution-specific claims are promoted into narrative.",
            "",
            "See `docs/METHODOLOGY.md`, `docs/POPULATION_CROSSWALK.md`, `docs/LATEST_UPDATE_REVIEW.md`, and `docs/QA_RESOLUTION_LOG.md` for full definitions and review detail.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(md), encoding="utf-8")

    case_cards = []
    for case in cases:
        case_cards.append(
            f"""
            <article class="qa-case-card">
              <p class="case-kicker">{html.escape(CASE_LABELS[str(case['case_type'])])}</p>
              <h3>{html.escape(str(case['institution']))}</h3>
              <p class="case-change">{html.escape(signed_int(int(case['absolute_change'])))} students</p>
              <p>{html.escape(str(case['analyst_note']))}</p>
              <div class="case-footer">
                <span class="case-decision">{html.escape(decision_copy(case))}</span>
                <a href="{html.escape(str(case['evidence_url']), quote=True)}" target="_blank" rel="noopener">Review evidence</a>
              </div>
            </article>"""
        )

    print_case_cards = []
    for case in cases:
        case_type = str(case["case_type"])
        print_case_cards.append(
            f"""<article><span>{html.escape(CASE_LABELS[case_type])}</span><h3>{html.escape(str(case['institution']))}</h3><strong>{html.escape(signed_int(int(case['absolute_change'])))} students · {html.escape(decision_copy(case))}</strong><p>{html.escape(CASE_PRINT_SUMMARIES[case_type])}</p></article>"""
        )

    latest_change_scale = max(
        abs(int(latest["undergraduate_change"])),
        abs(int(latest["graduate_change"])),
        abs(int(latest["absolute_change"])),
        1,
    )

    def change_bar_width(value: int) -> float:
        return 50 * abs(value) / latest_change_scale

    latest_change_rows = (
        ("Undergraduate", int(latest["undergraduate_change"]), "positive"),
        ("Graduate", int(latest["graduate_change"]), "negative"),
        ("Net change", int(latest["absolute_change"]), "net"),
    )
    latest_change_visual = "".join(
        f"""<div class="memo-change-row"><span>{html.escape(label)}</span><div class="memo-change-track"><i class="memo-change-bar {bar_class}" style="width:{change_bar_width(value):.1f}%"></i></div><strong>{html.escape(signed_int(value))}</strong></div>"""
        for label, value, bar_class in latest_change_rows
    )

    html_output = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Research memo on U.S. nonresident enrollment trends and publication QA using NCES/IPEDS data.">
  <meta name="theme-color" content="#10263c">
  <title>Research Memo | U.S. Nonresident Enrollment</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to memo</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a>
      <nav aria-label="Research memo navigation"><a href="index.html">Brief</a><a href="index.html#states">States</a><a href="index.html#methods">Methods</a><a href="index.html#downloads">Data</a></nav>
    </div>
  </header>
  <main id="main" class="memo-page">
    <section class="memo-hero">
      <div class="shell">
        <p class="eyebrow">Research memo · Fall {end_year}</p>
        <h1>Enrollment recovered. The latest growth was undergraduate-led.</h1>
        <p class="lede">A concise research and publication-QA memo on U.S. nonresident enrollment at degree-granting U.S. institutions.</p>
        <div class="memo-meta"><span>Fall {end_year} {html.escape(str(coverage['latest_data_status']))}</span><span>{start_year}-{end_year}</span><span>50 states + DC</span></div>
      </div>
    </section>

    <section class="shell memo-layout">
      <article class="memo-copy">
        <p class="eyebrow">Bottom line</p>
        <h2>Recovery is national. Its composition is not the same as before.</h2>
        <p>U.S. nonresident enrollment reached <strong id="memo-total">{headline['latest_nonresident']:,}</strong> in Fall {end_year}, or <strong>{headline['latest_share_pct']:.2f}%</strong> of the analytic universe and <strong>{signed_int(headline['change_since_2015'])}</strong> above {start_year}.</p>
        <p>The newest annual movement breaks with the decade pattern: undergraduate enrollment rose <strong>{signed_int(latest['undergraduate_change'])}</strong> across <strong>{baseline_positive_states} of 51 states/DC</strong>, while graduate enrollment fell <strong>{signed_int(latest['graduate_change'])}</strong>, producing a net <strong id="memo-latest-change">{signed_int(latest['absolute_change'])}</strong>. <strong>R01 remains a fixed baseline:</strong> call the shift persistent only if the next complete release is positive nationally and in at least <strong>26 of 51 states/DC</strong>.</p>

        <div class="memo-change-visual" aria-label="2023 to 2024 U.S. nonresident enrollment change by student level">
          <div class="memo-change-head"><strong>{prior_year}→{end_year}</strong><span>Change in U.S. nonresident enrollment</span></div>
          {latest_change_visual}
        </div>

        <h2>Three findings that matter</h2>
        <div class="memo-findings">
          <article><span>01</span><h3>The recovery became graduate-heavy</h3><p>Graduate enrollment is {signed_int(levels['graduate_change_students'])} above {start_year}; undergraduate enrollment is {signed_int(levels['undergraduate_change_students'])} below it.</p></article>
          <article><span>02</span><h3>State recovery remains uneven</h3><p>{recovery['states_at_or_above_baseline']} states/DC are at or above {recovery['baseline_year']}; {recovery['states_below_baseline']} remain below. {top_gain['state']} led the latest annual increase at {signed_int(top_gain['absolute_change'])}.</p></article>
          <article><span>03</span><h3>Institution-universe change does not explain the gain</h3><p>Continuing institutions contribute {signed_int(dynamics['continuing_change'])} over {start_year}-{end_year}, while universe entry/exit nets to {signed_int(dynamics['entry_exit_net'])}.</p></article>
        </div>
      </article>

      <aside class="memo-facts" aria-label="Memo at a glance">
        <p class="eyebrow">At a glance</p>
        <dl>
          <div><dt>Fall {end_year}</dt><dd>{headline['latest_nonresident']:,}</dd></div>
          <div><dt>Change since {start_year}</dt><dd>{signed_pct(headline['change_since_2015_pct'])}</dd></div>
          <div><dt>{prior_year}-{end_year}</dt><dd>{signed_pct(latest['pct_change'])}</dd></div>
          <div><dt>Undergraduate change</dt><dd>{signed_int(latest['undergraduate_change'])}</dd></div>
          <div><dt>High-priority QA reviewed</dt><dd>{resolution['reviewed_count']}/{resolution['high_priority_total']}</dd></div>
          <div><dt>NCES benchmark checks</dt><dd>{len(benchmark)}/{len(benchmark)}</dd></div>
        </dl>
      </aside>
    </section>

    <section class="section section-tinted memo-cases" id="analyst-cases">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Analyst judgment</p><h2>A flag does not automatically become a finding</h2><p>The same QA process can lead to three different publication decisions. These examples are drawn from the current evidence-backed review log.</p></div>
        <div class="qa-case-grid" id="memo-case-studies">{''.join(case_cards)}</div>
      </div>
    </section>

    <section class="section shell memo-methods">
      <div class="section-heading compact"><p class="eyebrow">Interpretation boundary</p><h2>What this memo can support</h2></div>
      <div class="method-grid">
        <article><h3>Population</h3><p>IPEDS U.S. nonresident status is a federal reporting category. It is not a complete measure of immigrant-origin, undocumented, DACA, foreign-born, or all international students. The population crosswalk documents which companion source should answer each of those questions.</p></article>
        <article><h3>Use</h3><p>The analysis supports enrollment monitoring and publication QA. It does not identify the causes of enrollment change or estimate immigration-policy effects.</p></article>
        <article><h3>Evidence</h3><p>Official source archives, schema audits, arithmetic reconciliation, external NCES benchmarking, and institution-level evidence review are kept separate so each claim can be traced to its support.</p></article>
        <article><h3>Publication</h3><p>Unresolved institution anomalies remain in official aggregate calculations but are withheld from institution-specific narrative until directly comparable evidence is available.</p></article>
      </div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/research_brief.pdf">Download PDF brief</a><a class="button button-secondary" href="methodology-crosswalk.html">Population crosswalk</a><a class="button button-secondary" href="downloads/research_memo.md">Memo notes</a><a class="button button-secondary" href="index.html#methods">Full methods</a></div>
      <div class="memo-print-notes print-only">
        <p class="eyebrow">Analyst judgment</p>
        <h2>Three flags, three publication decisions</h2>
        <div class="memo-print-cases">{''.join(print_case_cards)}</div>
        <h2 class="memo-print-methods-title">Methods and source trail</h2>
        <div class="memo-print-grid">
          <article><h3>Primary measure</h3><p>The series uses NCES/IPEDS Fall Enrollment <code>EFNRALT</code> for U.S. nonresident students. The analytic universe is degree-granting institutions in the First Look/Digest Title IV selection, located in the 50 states and District of Columbia.</p></article>
          <article><h3>Population comparability</h3><p>IPEDS U.S. nonresident, SEVIS international-student records, CPS immigrant-origin estimates, and ACS-derived undocumented-student estimates answer different questions. The project maintains a separate population/source crosswalk before any companion comparison is attempted.</p></article>
          <article><h3>Release control</h3><p>Historical revised IPEDS files are preferred when available. Fall {end_year} is treated as provisional. Source URLs, archive sizes, retrieval records, and SHA-256 hashes are retained so later revisions can be distinguished from analysis errors.</p></article>
          <article><h3>Independent checks</h3><p>All {len(benchmark)} NCES Digest consistency checks pass. State, institutional-control, and student-level aggregates reconcile to the national series, and institution entry/exit accounting is separated from continuing-institution change.</p></article>
          <article><h3>Publication QA</h3><p>The latest-release queue contains {review['review_queue']['high']} high-priority records. {resolution['reviewed_count']} high-priority records have evidence-backed manual dispositions; unresolved cases remain in official aggregate calculations but are withheld from institution-specific claims.</p></article>
          <article><h3>Use boundary</h3><p>This is an enrollment-monitoring and research-QA product. It does not estimate causal policy effects and it does not convert one immigration-related population definition into another.</p></article>
        </div>
        <p class="memo-print-footnote">Portfolio research demonstration. Not affiliated with NCES or the Presidents' Alliance on Higher Education and Immigration.</p>
      </div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Research memo · U.S. Nonresident Students in Higher Education</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_output, encoding="utf-8")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    print(
        f"Research memo: {headline['latest_nonresident']:,} latest; "
        f"{len(cases)} analyst cases; {len(benchmark)}/{len(benchmark)} benchmarks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
