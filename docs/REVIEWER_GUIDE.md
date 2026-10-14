# Reviewer Guide

This repository is intended to be evaluated as a small recurring research product, not only as a coding exercise. A reviewer should be able to understand the research question, inspect the public result, trace a number to source data, and see how the product would be maintained when a new release appears.

Live publication: `https://joseph-th.github.io/higher_education_and_immigration_demo/`

## Reviewer path

1. Open `deliverables/research_brief.pdf`. It is the fastest reviewer-facing artifact: headline findings, analyst judgment, interpretation boundaries, and a compact source/QA trail in three pages.
2. Open `site/index.html` through a local static server or deployed Pages URL. Read the six longitudinal findings, the latest-release review, inspect the state explorer, and open the three analyst case studies.
3. Open `site/methodology-crosswalk.html`. This shows how the project distinguishes IPEDS U.S. nonresident data from immigrant-origin, SEVIS international, undocumented, high-school-pipeline, and refugee/asylee concepts before attempting a comparison.
4. Open `site/research-operations.html`. This is the portfolio model for coordinating the three recurring products named in the vacancy: kickoff, versioned partner intake, method-change review, quantitative QA, discrepancy resolution, publication gating, and archival handoff.
5. Open `site/production-cycle.html`. This turns the shared partner workflow into seven explicit stage gates with entry conditions, required records, blockers, exit conditions, and retained evidence, while keeping all three products at a truthful pre-kickoff portfolio state. Download the blank live-cycle log to see the record a real kickoff would populate and validate.
6. Open `site/research-library.html`. Search and filter by population/topic, source type, and publisher; inspect the workflow-stage metadata that distinguishes collection, methodology, validation, publication context, and recurring research.
7. Open `site/publication-handoff.html`. This is the final pre-publication control: each public claim is tied to an authority, source, QA gate, disclosure, and publication status, including claim-level holds where institution evidence is unresolved.
8. Open `site/data-governance.html`. This shows the data-minimization boundary and exact public-release allowlist. The build rejects any file under `site/downloads/` or `site/data/` that is not explicitly approved.
9. Open `deliverables/ipeds_portfolio_analysis.xlsx`. Review the formula-driven executive summary, change the state lookup dropdown, and inspect the reconciliation/benchmark sheets.
10. Open `deliverables/management_briefing_deck.pptx`. Review the six-slide management story: KPI summary, national trend, state recovery, structural drivers, and interpretation/QA guardrails.
11. Open `site/sql-analysis.html`. Inspect the six read-only queries and their independent checks, then open `sql/portfolio_queries.sql` to see CTEs, joins, conditional aggregation, ranking, and window functions in executable form.
12. Open `site/ad-hoc-analysis.html`. Review the three constructed management questions and how each one is narrowed to the minimum useful calculation, tied to a source authority, reconciled, and returned as a short response without inventing a requester or deadline.
13. Open `site/planning-scenarios.html`. Review the 2024 forecast-vs-actual backtest and the three 2025 planning cases; note that the assumptions are visible and the page explicitly treats them as planning anchors rather than predictions.
14. Open `site/research-memo.html` or `docs/RESEARCH_MEMO.md` for the full writing sample, then `docs/FINDINGS.md` for the exact numerical basis behind it.
15. Read `docs/METHODOLOGY.md` and `docs/POPULATION_CROSSWALK.md` for universe rules, source-selection decisions, definitions, endpoint matching, and limitations.
16. Inspect `docs/QA_RESOLUTION_LOG.md`, then `data/source_manifest.csv`, `data/schema_audit.csv`, `data/benchmark_audit.csv`, `data/sql_analysis_audit.csv`, `data/ad_hoc_analysis_results.csv`, `data/planning_scenarios.csv`, `data/research_library.csv`, `data/production_cycle_register.csv`, `data/production_cycle_log_template.csv`, and `data/public_release_register.csv` to see how automated flags become analyst publication decisions and how coordination/provenance/release authority are retained.
17. Run `python scripts/validate_project.py`. If browser tooling is available, also run `python scripts/browser_smoke.py`.
18. Read `docs/UPDATE_PLAYBOOK.md` and `docs/DATA_CALENDAR.md` to see how the next NCES release would be detected, reviewed, and published.

## What the project demonstrates

| Analyst responsibility | Evidence in this repository |
| --- | --- |
| Acquire public administrative data | `scripts/fetch_ipeds.py` retrieves official NCES data and dictionaries and records exact source URLs |
| Preserve source lineage | `data/source_manifest.csv` records retrieval time, bytes, SHA-256 hashes, and extracted files |
| Handle changing schemas | `scripts/audit_ipeds_schema.py`, `data/schema_audit.csv`, and `docs/VARIABLE_MAPPING.md` verify required variables and labels year by year |
| Define an analytic universe | `docs/METHODOLOGY.md` documents the degree-granting First Look/Digest universe and 50-states-plus-DC rule |
| Distinguish populations and choose compatible sources | `data/population_crosswalk.csv`, `scripts/build_population_crosswalk.py`, and `site/methodology-crosswalk.html` document inclusion/exclusion rules, source vintages, units, and comparison warnings for six immigration-related student concepts |
| Coordinate recurring partner research products | `data/recurring_report_register.csv`, `scripts/build_recurring_report_register.py`, and `site/research-operations.html` model versioned intake, methodology-change review, QA gates, publication outputs, partner-confirmed scheduling, and archival handoff for the three recurring reports named in the role |
| Manage stage-gated partner production | `data/production_cycle_register.csv`, `scripts/build_production_cycle.py`, and `site/production-cycle.html` define seven evidence-based stage gates from confirmed kickoff through archive, including blockers, handoff records, and zero inferred internal deadlines |
| Maintain a live coordination log | `data/production_cycle_log_template.csv` plus `scripts/validate_production_cycle_log.py` provide a controlled record format with report/stage foreign keys, lifecycle statuses, materiality, evidence, decisions, closure dates, and a nonpublic-by-default boundary for completed partner logs |
| Build reproducible transformations | `scripts/build_analysis.py` creates institution-, state-, control-, and national-level outputs from the same normalized records |
| Perform substantive analysis | `scripts/summarize_findings.py` produces level, geography, control, concentration, recovery, and institution-dynamics findings |
| Investigate apparent discrepancies | `scripts/validate_benchmarks.py` quantifies release-vintage differences instead of forcing current data to match an older Digest publication |
| Review a new annual release | `scripts/build_update_review.py`, `docs/LATEST_UPDATE_REVIEW.md`, and `data/processed/latest_release_institution_review.csv` reconcile the new year and produce a reason-coded QA queue |
| Resolve flagged records with analyst judgment | `data/qa_resolution_log.csv`, `scripts/build_qa_resolution_log.py`, and `docs/QA_RESOLUTION_LOG.md` tie selected high-priority flags to external evidence, scope checks, and explicit publication decisions |
| Write a publication-ready research product | `scripts/build_research_memo.py`, `docs/RESEARCH_MEMO.md`, `site/research-memo.html`, and `deliverables/research_brief.pdf` turn validated findings and QA decisions into web, Markdown, and reviewer-ready PDF products |
| Brief nontechnical stakeholders | `scripts/build_briefing_note.py` generates `docs/BRIEFING_NOTE.md` directly from validated findings, QA, and benchmark outputs |
| Analyze and quality-control data in Excel | `deliverables/ipeds_portfolio_analysis.xlsx` uses formulas, structured tables, state lookup/data validation, reconciliation columns, conditional formatting, benchmark review, and charting |
| Build management-ready PowerPoint reporting | `deliverables/management_briefing_deck.pptx`, `scripts/build_management_deck.py`, and `deliverables/management_briefing_manifest.json` turn validated outputs into a six-slide KPI/trend/geography/driver/QA briefing with source and builder freshness hashes |
| Query and reconcile data in SQL | `sql/portfolio_queries.sql`, `scripts/build_sql_analysis.py`, `data/sql_analysis_audit.csv`, and `site/sql-analysis.html` demonstrate read-only joins, grouping, CTEs, conditional aggregation, ranking, and window functions with six independent checks against canonical CSV outputs |
| Answer bounded ad hoc management questions | `scripts/build_ad_hoc_analysis.py`, `data/ad_hoc_analysis_results.csv`, `docs/AD_HOC_ANALYSIS.md`, and `site/ad-hoc-analysis.html` show three explicitly simulated request-to-response cases with source selection, minimal calculation, reconciliation, and concise delivery |
| Support planning and variance review | `scripts/build_planning_scenarios.py`, `data/planning_scenarios.csv`, `docs/PLANNING_SCENARIOS.md`, and `site/planning-scenarios.html` demonstrate a forecast-vs-actual backtest plus three transparent forward planning cases with an explicit non-predictive boundary |
| Maintain national and state-level data products | `scripts/build_state_profiles.py` generates 51 state/DC briefs, a machine-readable profile dataset, and `state_profile_index.csv`; `state.html` provides a shareable state-level publication view |
| Assess emerging data needs and new research opportunities | `data/research_agenda.csv` and `docs/RESEARCH_AGENDA.md` distinguish questions answerable now from questions requiring partner/population-specific data and define proposed methods and decision rules |
| Organize a Research Library | `data/research_library.csv`, `scripts/build_research_library.py`, and `site/research-library.html` maintain a structured, searchable catalog with population/topic, resource-type, publisher, workflow-stage, source-role, and freshness metadata |
| Quality-control published numbers, definitions, citations, and copy | `data/publication_handoff.csv`, `scripts/build_publication_handoff.py`, and `site/publication-handoff.html` require each public claim to name its analytical authority, source role, QA gate, disclosure, and publication decision before handoff |
| Minimize sensitive data and control public release | `data/public_release_register.csv`, `scripts/build_data_governance.py`, and `site/data-governance.html` classify every public artifact, prohibit person-level/observed immigration-status data from the PUBLIC register, and fail the build on unregistered public files |
| Quality-control generated products | `tests/test_research_product.py` checks reconciliation identities, coverage, shares, outputs, downloads, foreign keys, publication handoff, and benchmark status |
| Communicate to nontechnical readers | `site/` turns the analysis into a concise research brief with plain-language definitions and limitations |
| Validate the published artifact | `scripts/browser_smoke.py` checks desktop/mobile rendering, interactions, downloads, console errors, and overflow |
| Maintain a recurring product | `scripts/check_for_new_release.py`, `scripts/check_research_library.py`, `scripts/check_population_crosswalk.py`, `docs/DATA_CALENDAR.md`, and `docs/UPDATE_PLAYBOOK.md` separate live monitoring from offline validation and publication |

## A concise project explanation

The project asks how U.S. nonresident fall enrollment changed across U.S. degree-granting institutions from 2015 through 2024. I built the series from official IPEDS complete-data files, audited the variables and aggregation codes across all ten years, restricted the data to a documented NCES/Digest universe, and created national, state, student-level, institutional-control, and institution-panel analyses. I then added structural QA, an independent NCES Digest benchmark, source hashes, downloadable outputs, and a static public brief. The project also includes an update playbook and release checker so it can operate as a recurring data product rather than a one-time analysis.

## Findings worth discussing

The strongest findings are not merely descriptive rankings:

- The 2015-2024 national increase came entirely from graduate enrollment. Graduate U.S. nonresident enrollment rose by 138,765 while undergraduate enrollment fell by 75,365.
- Recovery is geographically uneven. Thirty-three states/DC were at or above 2019 by 2024, while 18 remained below.
- Private nonprofit institutions account for the major positive shift by control, adding 82,825 U.S. nonresident students over the decade.
- Institution-panel accounting shows the +63,400 national increase was not created by adding more institutions to the analytic universe. Continuing institutions contributed +66,981 while universe entry and exit netted -3,581.
- The newest release has a different short-run composition: from 2023 to 2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment decreased by 2,053, producing a net increase of 29,539.
- Current IPEDS subgroup values differ slightly from the March 2026 Digest publication even though the overall enrollment universe is effectively identical. The project records that source-vintage difference rather than hiding it.

## Interpretation boundaries

The project deliberately avoids claims the data cannot support. IPEDS U.S. nonresident status is not a complete measure of international, immigrant-origin, undocumented, DACA, or foreign-born students. Fall Enrollment is a point-in-time snapshot. State values are based on institution location. UNITID matching helps with endpoint accounting but does not fully resolve mergers, splits, acquisitions, or reorganizations.

## Reproduction commands

Core rebuild and validation:

```bash
python scripts/validate_project.py
```

Optional browser publication QA:

```bash
python scripts/browser_smoke.py
```

Live source/release checks:

```bash
python scripts/check_for_new_release.py
python scripts/check_research_library.py
python scripts/check_population_crosswalk.py
python scripts/check_qa_evidence.py
```

The core validation command is intentionally offline once raw IPEDS files have been collected. Release detection, Research Library health, population-methodology source health, and QA evidence-link checks are intentionally online and separate, so changes in external websites cannot silently change the reproducibility of the current published result.
