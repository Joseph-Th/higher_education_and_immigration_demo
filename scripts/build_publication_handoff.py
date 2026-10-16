"""Generate a publication handoff register from validated research outputs.

The register models the final QA/QC step between completed analysis and a public
data-page refresh. It does not represent the Presidents' Alliance's internal
workflow. Every public claim is tied to a project authority, a maintained source,
an explicit QA gate, a disclosure, and a publication decision.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

from project_config import END_YEAR, START_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
CSV_OUTPUT = DATA / "publication_handoff.csv"
DOC_OUTPUT = ROOT / "docs" / "PUBLICATION_HANDOFF.md"
HTML_OUTPUT = ROOT / "site" / "publication-handoff.html"

FIELDS = (
    "claim_id",
    "surface",
    "claim_type",
    "public_copy",
    "authority",
    "source_locator",
    "research_library_id",
    "qa_gate",
    "release_disclosure",
    "publication_status",
)
ALLOWED_STATUSES = {"READY", "READY WITH CONTEXT", "READY WITH CLAIM-LEVEL HOLDS"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed_int(value: int) -> str:
    return f"{value:+,}" if value else "0"


def signed_pct(value: float) -> str:
    return f"{value:+.1f}%" if value else "0.0%"


def main() -> int:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "latest_update_review.json").read_text(encoding="utf-8"))
    resolution = json.loads((DATA / "qa_resolution_summary.json").read_text(encoding="utf-8"))
    medium_resolution = json.loads((DATA / "medium_qa_resolution_summary.json").read_text(encoding="utf-8"))
    benchmark = read_csv(DATA / "benchmark_audit.csv")
    states = read_csv(PROCESSED / "state_profile_index.csv")
    population_trends = read_csv(DATA / "population_trend_comparison.csv")
    pipeline = read_csv(DATA / "undocumented_pipeline_comparison.csv")
    source_triage = read_csv(DATA / "source_update_triage.csv")
    undergraduate_baseline = read_csv(DATA / "undergraduate_shift_baseline.csv")
    candidate_watchlist = read_csv(DATA / "candidate_year_qa_watchlist.csv")
    medium_review = read_csv(DATA / "medium_priority_review.csv")
    library = {row["resource_id"]: row for row in read_csv(DATA / "research_library.csv")}
    crosswalk = {row["population_id"]: row for row in read_csv(DATA / "population_crosswalk.csv")}

    if len(states) != 51:
        raise RuntimeError("Publication handoff requires all 50 states plus DC")
    if any(row["status"] != "PASS" for row in benchmark):
        raise RuntimeError("Publication handoff cannot be generated with failed benchmark checks")
    if sum(int(row["latest_nonresident"]) for row in states) != findings["headline"]["latest_nonresident"]:
        raise RuntimeError("State publication package does not reconcile to the national headline")
    ipeds_definition = crosswalk["ipeds_us_nonresident"]
    if "undocumented" not in ipeds_definition["explicit_exclusions"].lower():
        raise RuntimeError("Publication handoff requires the IPEDS population exclusion to remain explicit")
    if len(population_trends) != 12:
        raise RuntimeError("Publication handoff requires the complete 12-row bounded population comparison")
    undocumented_segments = {
        row["trend_segment"]
        for row in population_trends
        if row["population_id"] == "undocumented_higher_ed"
    }
    if undocumented_segments != {"undocumented_2019_2021", "undocumented_2023_2024"}:
        raise RuntimeError("Publication handoff requires the undocumented source-vintage break")
    if len(pipeline) != 10:
        raise RuntimeError("Publication handoff requires all ten R06 state comparison rows")
    pipeline_hs = sum(int(row["high_school_graduates_annual_2023"]) for row in pipeline)
    pipeline_he = sum(int(row["higher_ed_enrollment_2023"]) for row in pipeline)
    if (pipeline_hs, pipeline_he) != (53_000, 358_836):
        raise RuntimeError("Publication handoff R06 aggregate values do not reconcile")
    if not all("NOT a transition rate" in row["interpretation_gate"] for row in pipeline):
        raise RuntimeError("Publication handoff requires the R06 stock/flow interpretation gate")
    triage_ids = {row["resource_id"] for row in source_triage}
    if triage_ids != set(library) or len(source_triage) != len(library):
        raise RuntimeError("Publication handoff requires complete Research Library source-update routing")
    triage_counts = Counter(row["baseline_route"] for row in source_triage)
    if triage_counts["ROUTINE_REFRESH"] != 8 or triage_counts["METHODOLOGY_REVIEW"] != 3:
        raise RuntimeError("Publication handoff source-update route counts changed unexpectedly")

    headline = findings["headline"]
    levels = findings["level_decomposition"]
    recovery = findings["recovery"]
    controls = {row["control"]: row for row in findings["institution_control"]["changes"]}
    dynamics = findings["institution_dynamics"]["decade"]
    latest = review["national"]
    prior_year = review["coverage"]["prior_year"]
    status = findings["coverage"]["latest_data_status"]
    nonprofit = controls["Private nonprofit"]
    benchmark_passed = sum(row["status"] == "PASS" for row in benchmark)
    if len(undergraduate_baseline) != 51:
        raise RuntimeError("Publication handoff requires the complete 51-state/DC R01 baseline")
    baseline_undergraduate_change = sum(
        int(row["undergraduate_change"]) for row in undergraduate_baseline
    )
    baseline_positive_states = sum(
        int(row["undergraduate_change"]) > 0 for row in undergraduate_baseline
    )
    baseline_public_change = sum(
        int(row["public_undergraduate_change"]) for row in undergraduate_baseline
    )
    if baseline_undergraduate_change != latest["undergraduate_change"]:
        raise RuntimeError("Publication handoff R01 baseline does not reconcile to latest undergraduate change")
    if baseline_positive_states != 45:
        raise RuntimeError("Publication handoff R01 state breadth changed unexpectedly")
    if len(candidate_watchlist) != 226 or len({row["unitid"] for row in candidate_watchlist}) != 226:
        raise RuntimeError("Publication handoff requires the complete 226-row candidate-year QA watchlist")
    candidate_watchlist_high = [row for row in candidate_watchlist if row["current_review_priority"] == "high"]
    candidate_watchlist_medium = [row for row in candidate_watchlist if row["current_review_priority"] == "medium"]
    candidate_watchlist_directory = [row for row in candidate_watchlist if row["candidate_change_class"]]
    candidate_watchlist_overlap = [
        row for row in candidate_watchlist
        if row["carry_forward_group"] == "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"
    ]
    candidate_watchlist_high_overlap = [
        row for row in candidate_watchlist
        if row["carry_forward_group"] == "CURRENT_HIGH_PLUS_DIRECTORY_CHANGE"
    ]
    if (
        len(candidate_watchlist_high),
        len(candidate_watchlist_medium),
        len(candidate_watchlist_directory),
        len(candidate_watchlist_overlap),
        len(candidate_watchlist_high_overlap),
    ) != (27, 50, 154, 5, 0):
        raise RuntimeError("Publication handoff candidate-year QA watchlist counts do not reconcile")
    if len(medium_review) != 50 or len({row["unitid"] for row in medium_review}) != 50:
        raise RuntimeError("Publication handoff requires the complete 50-row medium-priority QA routing table")
    if (
        medium_resolution.get("reviewed_count") != 50
        or medium_resolution.get("medium_priority_total") != 50
        or medium_resolution.get("safe_with_context") != 20
        or medium_resolution.get("hold_for_confirmation") != 30
        or not medium_resolution.get("required_medium_priority_covered")
    ):
        raise RuntimeError("Publication handoff requires complete medium-priority evidence-backed dispositions")
    medium_routes = Counter(row["review_route"] for row in medium_review)
    if medium_routes != Counter(
        {
            "PERCENTAGE_MOVEMENT": 28,
            "ABSOLUTE_MOVEMENT": 11,
            "ABSOLUTE_AND_PERCENTAGE": 8,
            "STRUCTURAL_OR_REPORTING": 3,
        }
    ):
        raise RuntimeError("Publication handoff medium-priority QA route counts do not reconcile")
    medium_overlap = [row for row in medium_review if row["candidate_directory_overlap"] == "yes"]
    if len(medium_overlap) != 5:
        raise RuntimeError("Publication handoff medium-priority candidate-directory overlap count changed")

    rows = [
        {
            "claim_id": "N01",
            "surface": "National headline",
            "claim_type": "Headline metric",
            "public_copy": f"Fall {END_YEAR} U.S. nonresident enrollment: {headline['latest_nonresident']:,} students.",
            "authority": "data/processed/national_year.csv",
            "source_locator": f"year={END_YEAR}; nonresident_enrollment",
            "research_library_id": f"ef{END_YEAR}a",
            "qa_gate": "State totals and student-level components reconcile to the national value; NCES benchmark is within threshold.",
            "release_disclosure": f"Fall {END_YEAR} is {status}.",
            "publication_status": "READY",
        },
        {
            "claim_id": "N02",
            "surface": "National headline",
            "claim_type": "Calculated share",
            "public_copy": f"U.S. nonresident students are {headline['latest_share_pct']:.2f}% of fall enrollment in the analytic universe.",
            "authority": "data/processed/national_year.csv",
            "source_locator": f"year={END_YEAR}; nonresident_enrollment / total_enrollment",
            "research_library_id": f"ef{END_YEAR}a",
            "qa_gate": "Published percentage is recalculated from current counts in repository tests.",
            "release_disclosure": "Share applies only to the documented degree-granting First Look/Digest universe.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "N03",
            "surface": "Longitudinal finding",
            "claim_type": "Endpoint comparison",
            "public_copy": f"U.S. nonresident enrollment is {signed_int(headline['change_since_2015'])} ({signed_pct(headline['change_since_2015_pct'])}) from {START_YEAR} to {END_YEAR}.",
            "authority": "data/processed/national_year.csv",
            "source_locator": f"years={START_YEAR},{END_YEAR}; nonresident_enrollment",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "Endpoint difference reconciles to student-level and institutional-control decompositions.",
            "release_disclosure": f"The endpoint includes {END_YEAR} {status} data.",
            "publication_status": "READY",
        },
        {
            "claim_id": "N04",
            "surface": "Student-level finding",
            "claim_type": "Component decomposition",
            "public_copy": f"Across {START_YEAR}-{END_YEAR}, graduate U.S. nonresident enrollment changed {signed_int(levels['graduate_change_students'])} while undergraduate enrollment changed {signed_int(levels['undergraduate_change_students'])}.",
            "authority": "data/processed/national_year.csv",
            "source_locator": f"years={START_YEAR},{END_YEAR}; undergraduate_nonresident, graduate_nonresident",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "Undergraduate plus graduate counts reconcile exactly to total U.S. nonresident enrollment for every year.",
            "release_disclosure": "Student-level categories follow IPEDS aggregation codes documented in the methodology.",
            "publication_status": "READY",
        },
        {
            "claim_id": "N05",
            "surface": "Latest release update",
            "claim_type": "Year-over-year decomposition",
            "public_copy": f"From {prior_year} to {END_YEAR}, enrollment changed {signed_int(latest['absolute_change'])}: undergraduate {signed_int(latest['undergraduate_change'])}, graduate {signed_int(latest['graduate_change'])}.",
            "authority": "data/latest_update_review.json",
            "source_locator": "national absolute_change; undergraduate_change; graduate_change",
            "research_library_id": f"ef{END_YEAR}a",
            "qa_gate": "Student-level changes reconcile exactly to the national annual change and the institution-accounting bridge.",
            "release_disclosure": "One annual movement is not treated as evidence of a durable trend change.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "N06",
            "surface": "R01 current-data baseline",
            "claim_type": "Latest-year breadth / persistence baseline",
            "public_copy": f"The {prior_year}-{END_YEAR} undergraduate increase was {signed_int(baseline_undergraduate_change)} and was positive in {baseline_positive_states} of 51 states/DC; public institutions contributed {signed_int(baseline_public_change)}.",
            "authority": "data/undergraduate_shift_baseline.csv",
            "source_locator": "51 state/DC rows; undergraduate_change; public_undergraduate_change; institution-continuity accounting",
            "research_library_id": f"ef{END_YEAR}a",
            "qa_gate": "State, institutional-control, and institution-continuity undergraduate decompositions reconcile to the national latest-year change; annual history fixes the pre-next-release baseline.",
            "release_disclosure": "This establishes the 2024 comparison baseline but does not answer persistence; the next complete Fall Enrollment release must pass schema review before R01 is classified.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "S01",
            "surface": "State data package",
            "claim_type": "Coverage / reconciliation",
            "public_copy": f"{recovery['states_at_or_above_baseline']} states/DC are at or above {recovery['baseline_year']} U.S. nonresident enrollment; {recovery['states_below_baseline']} remain below.",
            "authority": "data/processed/state_change_summary.csv",
            "source_locator": "51 geography rows; recovery_status",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": f"All {len(states)} state/DC profiles are present and their latest counts sum exactly to {headline['latest_nonresident']:,}.",
            "release_disclosure": "State is institution location, not student residence, nationality, or immigration status.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "C01",
            "surface": "Institutional-control finding",
            "claim_type": "Sector comparison",
            "public_copy": f"Private nonprofit institutions changed {signed_int(nonprofit['absolute_change'])} U.S. nonresident students from {START_YEAR} to {END_YEAR}.",
            "authority": "data/processed/control_year.csv",
            "source_locator": f"control=Private nonprofit; years={START_YEAR},{END_YEAR}",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "Public, private nonprofit, and private for-profit totals reconcile exactly to the national series in every year.",
            "release_disclosure": "Institutional control comes from each year's IPEDS directory file.",
            "publication_status": "READY",
        },
        {
            "claim_id": "I01",
            "surface": "Institution-universe finding",
            "claim_type": "Endpoint accounting",
            "public_copy": f"Continuing institutions contributed {signed_int(dynamics['continuing_change'])} to the {START_YEAR}-{END_YEAR} change; universe entry/exit netted {signed_int(dynamics['entry_exit_net'])}.",
            "authority": "data/processed/institution_change_summary.csv",
            "source_locator": "UNITID endpoint status and absolute_change",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "All endpoint institution contributions sum exactly to the national change.",
            "release_disclosure": "Universe entry/exit can reflect mergers, eligibility, or identifier restructuring, not only openings/closures.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "Q01",
            "surface": "Institution-level QA",
            "claim_type": "Publication gate",
            "public_copy": f"{resolution['reviewed_count']} high-priority records have manual dispositions: {resolution['safe_with_context']} safe with context and {resolution['hold_for_confirmation']} held for confirmation.",
            "authority": "data/qa_resolution_log.csv",
            "source_locator": "publication_class; disposition; evidence_url",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": f"All {resolution['high_priority_total']} current high-priority rows have explicit publication dispositions; evidence links are separately health-checked.",
            "release_disclosure": "Automated flags are triage, not corrections; held records remain in official aggregate calculations.",
            "publication_status": "READY WITH CLAIM-LEVEL HOLDS",
        },
        {
            "claim_id": "Q02",
            "surface": "Candidate-year institution QA",
            "claim_type": "Carry-forward review control",
            "public_copy": "The next full-package institution QA watchlist contains 226 unique UNITIDs: 27 current high-priority rows, 50 medium-priority rows, and 154 candidate-directory structural changes with five medium/directory overlaps and no high/directory overlap.",
            "authority": "data/candidate_year_qa_watchlist.csv",
            "source_locator": "226 unique UNITIDs; carry_forward_group; current_review_priority; candidate_change_class; next_release_action",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "The watchlist reconciles 27 + 50 + 154 - 5 to 226 unique UNITIDs, preserves all current high- and medium-priority dispositions only as context, and contains no candidate-year enrollment values.",
            "release_disclosure": "This is pre-release triage, not a 2025 enrollment finding or standing institution-publication approval; every row must be revalidated after the complete Fall Enrollment build.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "Q03",
            "surface": "Medium-priority institution QA",
            "claim_type": "Evidence review and publication gate",
            "public_copy": f"All 50 current medium-priority institution flags are routed and evidence-reviewed: 28 percentage-movement, 11 absolute-movement, 8 combined absolute/percentage, and 3 structural/reporting-context cases; {medium_resolution['safe_with_context']} are safe with context and {medium_resolution['hold_for_confirmation']} remain held for confirmation.",
            "authority": "data/medium_priority_review.csv; data/medium_qa_resolution_log.csv",
            "source_locator": "50 current medium rows; review_route; publication_class; disposition; evidence_url",
            "research_library_id": "ipeds_complete_data",
            "qa_gate": "Every medium-priority row maps to exactly one non-severity route and has an evidence-backed publication disposition; five candidate-directory overlaps are retained as context without changing priority.",
            "release_disclosure": "Medium-priority evidence can clear only a bounded current-release narrative claim; it does not correct IPEDS values, add a new risk score, or create standing approval for the next release.",
            "publication_status": "READY WITH CLAIM-LEVEL HOLDS",
        },
        {
            "claim_id": "M01",
            "surface": "Definition / methodology",
            "claim_type": "Population boundary",
            "public_copy": "IPEDS U.S. nonresident is not a measure of undocumented, DACA, immigrant-origin, refugee/asylee, or all foreign-born students.",
            "authority": "data/population_crosswalk.csv",
            "source_locator": "population_id=ipeds_us_nonresident; explicit_exclusions; comparison_warning",
            "research_library_id": "ipeds_race_ethnicity_definitions",
            "qa_gate": "Population crosswalk explicitly records inclusion, exclusion, source vintage, unit, geography, and comparison warning.",
            "release_disclosure": "Other Portal populations require their own source systems and methods.",
            "publication_status": "READY",
        },
        {
            "claim_id": "M02",
            "surface": "Population trend comparison",
            "claim_type": "Non-addability / vintage gate",
            "public_copy": "Companion IPEDS, immigrant-origin, and undocumented-student values remain separate and are not addable; no 2021-2023 undocumented trend is calculated.",
            "authority": "data/population_trend_comparison.csv",
            "source_locator": "population_id; trend_segment; comparison_class; comparison_note",
            "research_library_id": "portal_methodology",
            "qa_gate": "The comparison contains 12 validated rows and preserves separate undocumented 2019-2021 and 2023-2024 source segments.",
            "release_disclosure": "Population definitions, denominators, source vintages, and geography differ; cross-population arithmetic is contextual only.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "P01",
            "surface": "Undocumented pipeline context",
            "claim_type": "Ecological stock / flow comparison",
            "public_copy": "Across the ten overlapping 2023 states, 53,000 annual undocumented high-school graduates represent 70.7% of the national estimate and 358,836 undocumented higher-education students represent 70.4%.",
            "authority": "data/undocumented_pipeline_comparison.csv",
            "source_locator": "10 state rows; separate 75,000 high-school and 510,000 higher-education national denominators",
            "research_library_id": "undocumented_hs_graduates_2026",
            "qa_gate": "All ten state rows reconcile to the fixed R06 source values and every row retains the stock/flow NOT-a-transition-rate interpretation gate.",
            "release_disclosure": "High-school graduates are an annual flow and higher-education enrollment is a stock; the comparison is ecological, non-causal, and not a college-going rate.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "G01",
            "surface": "Source update governance",
            "claim_type": "Refresh / escalation control",
            "public_copy": f"All {len(source_triage)} maintained Research Library sources have an explicit update route: {triage_counts['ROUTINE_REFRESH']} routine-refresh baselines and {triage_counts['METHODOLOGY_REVIEW']} methodology-review baselines, with zero inferred internal deadlines.",
            "authority": "data/source_update_triage.csv",
            "source_locator": "one row per Research Library resource_id; baseline_route; escalation rules",
            "research_library_id": "ipeds_release_schedule",
            "qa_gate": "The routing register covers the Research Library one-for-one with controlled routes and explicit methodology/new-research escalation conditions.",
            "release_disclosure": "This is a portfolio routing model, not the Presidents' Alliance's internal refresh schedule, approval workflow, or partner delivery calendar.",
            "publication_status": "READY WITH CONTEXT",
        },
        {
            "claim_id": "B01",
            "surface": "External validation",
            "claim_type": "Benchmark status",
            "public_copy": f"{benchmark_passed}/{len(benchmark)} NCES Digest consistency checks pass for 2019-{END_YEAR}.",
            "authority": "data/benchmark_audit.csv",
            "source_locator": "status=PASS across all metric-year rows",
            "research_library_id": "digest_306_10",
            "qa_gate": "Current IPEDS values stay within documented thresholds without being overwritten to match an older publication vintage.",
            "release_disclosure": "Digest values are rounded and come from a different release vintage.",
            "publication_status": "READY WITH CONTEXT",
        },
    ]

    for row in rows:
        missing = [field for field in FIELDS if not str(row[field]).strip()]
        if missing:
            raise RuntimeError(f"Publication handoff {row['claim_id']} has blank fields: {missing}")
        if row["research_library_id"] not in library:
            raise RuntimeError(
                f"Publication handoff {row['claim_id']} references unknown Research Library ID {row['research_library_id']}"
            )
        if row["publication_status"] not in ALLOWED_STATUSES:
            raise RuntimeError(f"Unknown publication status: {row['publication_status']}")

    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    markdown = [
        "# Publication Handoff Register",
        "",
        "This is a portfolio demonstration of the final QA/QC handoff between validated analysis and a public data-page refresh. It does **not** represent the Presidents' Alliance's internal publication workflow or approval chain.",
        "",
        f"**Current release:** Fall {END_YEAR} ({status})",
        f"**Claim/register rows:** {len(rows)}",
        f"**State/DC profiles:** {len(states)}",
        f"**External benchmark checks:** {benchmark_passed}/{len(benchmark)} PASS",
        "",
        "## Publication claims",
        "",
        "| ID | Surface | Public copy | QA gate | Disclosure | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        markdown.append(
            f"| {row['claim_id']} | {row['surface']} | {row['public_copy']} | {row['qa_gate']} | "
            f"{row['release_disclosure']} | {row['publication_status']} |"
        )
    markdown.extend(
        [
            "",
            "## Handoff rule",
            "",
            "A value is not publication-ready merely because the calculation ran. The handoff checks the population definition, release status, arithmetic reconciliation, citation/source role, claim scope, and any unresolved institution-level evidence before the public copy is approved.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(markdown), encoding="utf-8")

    cards = []
    for row in rows:
        source = library[row["research_library_id"]]
        status_class = "handoff-status-hold" if "HOLDS" in row["publication_status"] else "handoff-status-ready"
        cards.append(
            f"""
            <article class="handoff-card">
              <div class="handoff-card-head"><span>{html.escape(row['claim_id'])}</span><span class="handoff-status {status_class}">{html.escape(row['publication_status'])}</span></div>
              <p class="case-kicker">{html.escape(row['surface'])} · {html.escape(row['claim_type'])}</p>
              <h2>{html.escape(row['public_copy'])}</h2>
              <dl class="handoff-meta">
                <div><dt>Authority</dt><dd><code>{html.escape(row['authority'])}</code><br><small>{html.escape(row['source_locator'])}</small></dd></div>
                <div><dt>QA gate</dt><dd>{html.escape(row['qa_gate'])}</dd></div>
                <div><dt>Required disclosure</dt><dd>{html.escape(row['release_disclosure'])}</dd></div>
              </dl>
              <a class="crosswalk-source" href="{html.escape(source['url'], quote=True)}" target="_blank" rel="noopener">Source: {html.escape(source['title'])}</a>
            </article>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Publication handoff register tying public higher-education data claims to sources, QA gates, disclosures, and publication decisions.">
  <meta name="theme-color" content="#10263c">
  <title>Publication Handoff | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to publication handoff</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Publication handoff navigation"><a href="index.html">Brief</a><a href="research-memo.html">Memo</a><a href="research-library.html">Library</a><a href="research-operations.html">Operations</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Publication handoff</p><h1>A calculation is not ready just because it ran.</h1><p class="lede">A portfolio release packet tying each public claim to its analytical authority, maintained source, QA gate, required disclosure, and publication decision.</p><div class="hero-actions"><a class="button button-primary" href="#handoff-register">Review publication register</a><a class="button button-secondary" href="downloads/publication_handoff.csv">Download handoff CSV</a></div><p class="release-note"><strong>Portfolio demonstration:</strong> this models a defensible pre-publication review. It does not represent the Presidents' Alliance's internal approval workflow.</p><div class="handoff-summary"><article><strong>{len(rows)}</strong><span>publication claims / controls</span></article><article><strong>{len(states)}</strong><span>state + DC profiles reconciled</span></article><article><strong>{benchmark_passed}/{len(benchmark)}</strong><span>external benchmark checks</span></article><article><strong>{resolution['reviewed_count']}</strong><span>high-priority institution flags manually reviewed</span></article></div></div></section>
    <section class="section shell"><div class="section-heading"><p class="eyebrow">Publication gate</p><h2>Five questions before copy moves to a public page</h2><p>The register makes the checks explicit so a source refresh cannot silently change population meaning, release status, arithmetic, or claim scope.</p></div><ol class="handoff-gates"><li><strong>Definition</strong><span>Does the population and denominator still mean what the copy says?</span></li><li><strong>Release</strong><span>Is the newest source final, provisional, revised, or from a different publication vintage?</span></li><li><strong>Reconcile</strong><span>Do components, states, and endpoint accounting reproduce the headline?</span></li><li><strong>Citation</strong><span>Is the maintained source appropriate as input, benchmark, methodology, or context?</span></li><li><strong>Scope</strong><span>Does unresolved QA require context or a claim-level hold before publication?</span></li></ol></section>
    <section class="section section-tinted" id="handoff-register"><div class="shell"><div class="section-heading"><p class="eyebrow">Claim register</p><h2>Every public statement has an authority and a gate</h2><p>These rows are generated from the same validated outputs that drive the research brief. The structured CSV is the portable handoff artifact.</p></div><div class="handoff-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">State package</p><h2>National and state publication move together</h2></div><div class="method-grid"><article><h3>51 geographies</h3><p>All 50 states plus DC have generated publication profiles with the current series, latest share, level composition, recovery status, and leading institutions.</p></article><article><h3>Exact reconciliation</h3><p>The {len(states)} latest state/DC counts sum exactly to the national headline of {headline['latest_nonresident']:,}.</p></article><article><h3>Separate claim gate</h3><p>Institution-level anomalies remain in the official aggregates but cannot become institution-specific narrative until the evidence/disposition layer permits it.</p></article><article><h3>Method boundary</h3><p>State means institution location. The publication does not relabel it as student residence, nationality, legal status, or country of origin.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/publication_handoff.md">Download handoff notes</a><a class="button button-secondary" href="research-operations.html">Recurring research operations</a><a class="button button-secondary" href="data-governance.html">Data governance</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Publication Handoff · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")

    print(f"Publication handoff: {len(rows)} claims; {len(states)} state/DC profiles")
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
