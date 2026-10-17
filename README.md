# U.S. Nonresident Students in Higher Education

Portfolio research project analyzing national and state-level enrollment trends for U.S. nonresident students in American higher education using the U.S. Department of Education's Integrated Postsecondary Education Data System (IPEDS).

The project is designed as a compact, reproducible research product rather than a generic dashboard. It emphasizes source quality, data definitions, QA/QC, methodological documentation, clear writing, and communication of limitations.

![Research brief preview](docs/assets/research-brief-preview.png)

**Live publication:** https://joseph-th.github.io/higher_education_and_immigration_demo/

## Start here

If you are reviewing this as a work sample, the core case should be clear in about five minutes:

1. **[Live research publication](https://joseph-th.github.io/higher_education_and_immigration_demo/)** — scan the headline findings, state explorer, and latest-release QA judgment.
2. **[`deliverables/research_brief.pdf`](deliverables/research_brief.pdf)** — two-page research/writing sample with findings, limitations, and source/QA trail.
3. **[`deliverables/management_briefing_deck.pptx`](deliverables/management_briefing_deck.pptx)** — five-slide management briefing built from the same validated outputs.

For a technical check, open **[`deliverables/ipeds_portfolio_analysis.xlsx`](deliverables/ipeds_portfolio_analysis.xlsx)** or **[`site/sql-analysis.html`](site/sql-analysis.html)**. The rest of the repository is supporting audit trail and reproducibility evidence, not required reading.

See [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) for the compact reviewer path and role-to-evidence map.

## Research question

How did fall enrollment of U.S. nonresident students change across the United States from 2015 through 2024, and how did those changes vary by state and student level?

## What is included

- **Research publication:** an interactive national/state brief plus a two-page PDF writing sample.
- **Management communication:** a five-slide PowerPoint briefing built from the same validated findings.
- **Technical analysis:** a formula-driven Excel workbook, executable SQL analysis, and reproducible Python pipeline.
- **QA/QC evidence:** cross-year schema checks, arithmetic reconciliation, 24 independent NCES benchmark checks, and evidence-backed review of high- and medium-priority institution anomalies.
- **Methodological judgment:** explicit population/source boundaries so IPEDS U.S. nonresident, SEVIS international, immigrant-origin, undocumented, pipeline, and refugee/asylee measures are not treated as interchangeable.
- **Publication discipline:** source lineage, claim-level holds, release-readiness controls, and a governed public output tree.

Detailed supporting artifacts remain under `docs/`, `data/`, and `site/` for technical or audit review. They are intentionally secondary to the brief, live publication, management deck, workbook, and SQL sample.

## Data

Primary source: National Center for Education Statistics (NCES), Integrated Postsecondary Education Data System (IPEDS).

Initial source tables:

- `EF2015A` through `EF2024A`: Fall Enrollment by race/ethnicity, gender, attendance status, and student level.
- `HD2015` through `HD2024`: Institutional directory information used for institution name, state, and other institutional attributes.

Raw source files are downloaded directly from NCES and are intentionally excluded from Git because they are reproducible and comparatively large. A tracked source manifest records the source URL, file size, SHA-256 hash, and retrieval time for every downloaded archive.

## Reproduce the source-data collection

From the repository root:

```bash
python scripts/fetch_ipeds.py
```

The script downloads the official data archives and data dictionaries for 2015-2024, verifies that each response is a valid ZIP archive, extracts it under `data/raw/ipeds/`, and writes `data/source_manifest.csv`.

To reproduce the cross-year schema audit:

```bash
python -m pip install -r requirements.txt
python scripts/audit_ipeds_schema.py
```

The audit verifies the required enrollment and directory variables, confirms the aggregation labels used by the analysis, prefers revised historical CSVs when NCES provides them, and writes `data/schema_audit.csv`.

Build the normalized analysis outputs and public-site data:

```bash
python scripts/build_analysis.py
python scripts/build_sql_analysis.py
python scripts/build_ad_hoc_analysis.py
python scripts/build_state_recovery_analysis.py
python scripts/build_undergraduate_shift_baseline.py
python scripts/build_planning_scenarios.py
python scripts/build_candidate_directory_preflight.py
python scripts/build_candidate_directory_change_review.py
python scripts/build_update_review.py
python scripts/build_medium_priority_review.py
python scripts/build_qa_resolution_log.py
python scripts/build_high_priority_category_diagnostic.py
python scripts/build_medium_qa_resolution_log.py
python scripts/build_medium_priority_category_diagnostic.py
python scripts/build_candidate_year_qa_watchlist.py
python scripts/build_freshness_monitor.py
python scripts/build_private_nonprofit_analysis.py
python scripts/build_research_library.py
python scripts/build_source_update_triage.py
python scripts/build_undocumented_pipeline.py
python scripts/build_population_crosswalk.py
python scripts/build_population_trends.py
python scripts/build_recurring_report_register.py
python scripts/validate_production_cycle_log.py
python scripts/build_production_cycle.py
python scripts/build_research_agenda.py
python scripts/summarize_findings.py
python scripts/validate_benchmarks.py
python scripts/build_state_profiles.py
python scripts/build_briefing_note.py
python scripts/build_research_memo.py
python scripts/build_publication_handoff.py
python scripts/build_release_readiness.py
python scripts/build_data_governance.py
python scripts/build_site_data.py
```

The public analysis uses degree-granting institutions in the IPEDS First Look/Digest Title IV universe (`DEGGRANT=1` and `PSET4FLG` in `1,3`) located in the 50 states and District of Columbia. This selection makes the headline national total directly benchmarkable against NCES Digest tables.

For the complete offline rebuild and validation path, run:

```bash
python scripts/validate_project.py
```

That command compiles the Python code, reruns the schema audit, rebuilds all derived data, reruns 24 NCES Digest consistency checks, regenerates the public site data, and runs the repository test suite.

The PDF brief is a downstream publication artifact rather than an analytical input. When the research memo changes, regenerate it after installing the optional Playwright dependency:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/build_pdf_brief.py
python scripts/validate_project.py
```

`deliverables/research_brief_manifest.json` records the exact memo SHA-256 used to create the PDF. Repository validation fails if the committed PDF no longer matches the current generated memo.

The PowerPoint deck is also a downstream publication artifact. After installing `requirements-dev.txt`, regenerate it with:

```bash
python scripts/build_management_deck.py
python scripts/validate_project.py
```

`deliverables/management_briefing_manifest.json` binds the five-slide PPTX to the current deck builder and validated CSV/JSON sources by SHA-256.

For browser-level publication QA, install the optional development dependency and Chromium once, then run:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_smoke.py
```

The browser smoke test serves the built site on an ephemeral local port, renders desktop and mobile viewports, checks calculated values and interactive elements, verifies public downloads, detects JavaScript/console errors, and checks for unintended page-level horizontal overflow.

Live source-health checks remain separate from offline validation:

```bash
python scripts/check_for_new_release.py
python scripts/check_candidate_directory.py
python scripts/check_research_library.py
python scripts/check_population_crosswalk.py
python scripts/check_qa_evidence.py
```

The live checks verify the maintained Research Library, the population-crosswalk methodology sources, and the external evidence links used by the manual QA resolution layer. They are intentionally separate from the offline reproducibility build. Script-blocking HTTP 401/403 responses are surfaced as access restrictions requiring manual browser review rather than misclassified as dead links.

## Documentation

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md): scope, audience, questions, and deliverables.
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md): source inventory and release notes.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md): definitions, analytic unit, QA/QC plan, and limitations.
- [`docs/POPULATION_CROSSWALK.md`](docs/POPULATION_CROSSWALK.md): generated source-selection crosswalk for distinct immigration-related student populations.
- [`docs/RECURRING_REPORT_REGISTER.md`](docs/RECURRING_REPORT_REGISTER.md): recurring-report intake, methodology review, QA gate, publication, and handoff model for the three products named in the target role.
- [`docs/PRODUCTION_CYCLE.md`](docs/PRODUCTION_CYCLE.md): generated seven-stage partner-production controls, product kickoff packet, and live-cycle log handling rules.
- [`docs/VARIABLE_MAPPING.md`](docs/VARIABLE_MAPPING.md): verified cross-year variables and aggregation codes.
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md): definitions for generated analysis and audit outputs.
- [`docs/VALIDATION.md`](docs/VALIDATION.md): implemented QA checks and independent NCES benchmark.
- [`docs/FINDINGS.md`](docs/FINDINGS.md): current analytical findings with exact supporting figures.
- [`docs/LATEST_UPDATE_REVIEW.md`](docs/LATEST_UPDATE_REVIEW.md): generated review of the newest annual release and its QA queue.
- [`docs/QA_RESOLUTION_LOG.md`](docs/QA_RESOLUTION_LOG.md): evidence-backed analyst dispositions for the complete current high-priority annual QA queue.
- [`docs/HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md`](docs/HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md): internal IPEDS category-countermovement reconciliation for the 27 high-priority records, with a non-correction and non-clearance boundary.
- [`docs/MEDIUM_PRIORITY_REVIEW.md`](docs/MEDIUM_PRIORITY_REVIEW.md): current medium-priority QA routing by existing trigger type, mixed-direction accounting, candidate-directory overlap, and evidence-review boundary.
- [`docs/MEDIUM_QA_RESOLUTION_LOG.md`](docs/MEDIUM_QA_RESOLUTION_LOG.md): evidence-backed analyst dispositions for all 50 current medium-priority QA records, including scope caveats and next-release revalidation.
- [`docs/MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md`](docs/MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md): internal IPEDS category-countermovement reconciliation for all 50 medium-priority records, with routing and evidence decisions kept separate from the arithmetic signal.
- [`docs/RESEARCH_MEMO.md`](docs/RESEARCH_MEMO.md): concise reviewer-facing writing sample built from validated findings and QA decisions.
- [`docs/BRIEFING_NOTE.md`](docs/BRIEFING_NOTE.md): generated stakeholder briefing with implications, monitoring questions, and interpretation boundaries.
- [`docs/EXCEL_WORKBOOK.md`](docs/EXCEL_WORKBOOK.md): workbook contents, authority boundaries, QA features, and maintenance notes.
- [`docs/POWERPOINT_DECK.md`](docs/POWERPOINT_DECK.md): management-deck contents, authority boundary, freshness manifest, and rebuild instructions.
- [`docs/SQL_ANALYSIS.md`](docs/SQL_ANALYSIS.md): generated SQL query catalog, sample results, and independent reconciliation checks.
- [`docs/AD_HOC_ANALYSIS.md`](docs/AD_HOC_ANALYSIS.md): simulated one-off management questions, compact answers, source authorities, and case-level reconciliation checks.
- [`docs/STATE_RECOVERY_ANALYSIS.md`](docs/STATE_RECOVERY_ANALYSIS.md): 2019-2024 state recovery decomposition, institution concentration, reconciliation controls, and interpretation boundaries.
- [`docs/UNDERGRADUATE_SHIFT_BASELINE.md`](docs/UNDERGRADUATE_SHIFT_BASELINE.md): fixed 2023-2024 R01 baseline, annual context, breadth/concentration measures, and next-release persistence rule.
- [`docs/PRIVATE_NONPROFIT_GROWTH.md`](docs/PRIVATE_NONPROFIT_GROWTH.md): 2015-2024 private-nonprofit institution-contribution concentration analysis with student-level reconciliation and latest-release QA gates.
- [`docs/POPULATION_TREND_COMPARISON.md`](docs/POPULATION_TREND_COMPARISON.md): bounded national comparison of IPEDS U.S. nonresident, immigrant-origin, and undocumented higher-education measures with explicit source-vintage breaks and non-addability rules.
- [`docs/UNDOCUMENTED_PIPELINE_CONTEXT.md`](docs/UNDOCUMENTED_PIPELINE_CONTEXT.md): bounded 2023 state context comparing undocumented annual high-school graduate flow with undocumented higher-education enrollment stock without treating their ratio as a transition rate.
- [`docs/PLANNING_SCENARIOS.md`](docs/PLANNING_SCENARIOS.md): forecast-vs-actual backtest, data-derived planning scenarios, assumptions, and interpretation boundary.
- [`docs/FRESHNESS_MONITOR.md`](docs/FRESHNESS_MONITOR.md): dated next-release availability, year-advance gate, source-review state, and recurring-product monitoring triggers.
- [`docs/CANDIDATE_DIRECTORY_PREFLIGHT.md`](docs/CANDIDATE_DIRECTORY_PREFLIGHT.md): bounded 2025 directory/dictionary compatibility review, frame continuity, hashes, schema delta, and no-year-advance boundary.
- [`docs/CANDIDATE_DIRECTORY_CHANGE_REVIEW.md`](docs/CANDIDATE_DIRECTORY_CHANGE_REVIEW.md): hashed institution-level candidate-directory entry/exit and attribute-change queue with current-year exposure and no-future-enrollment interpretation boundary.
- [`docs/CANDIDATE_YEAR_QA_WATCHLIST.md`](docs/CANDIDATE_YEAR_QA_WATCHLIST.md): reconciled current/candidate institution review union with cross-signal overlaps, carry-forward actions, and explicit revalidation boundaries.
- [`docs/SOURCE_UPDATE_TRIAGE.md`](docs/SOURCE_UPDATE_TRIAGE.md): R07 source-change routing with complete Research Library coverage, escalation rules, and portfolio/non-affiliation boundaries.
- [`docs/RESEARCH_AGENDA.md`](docs/RESEARCH_AGENDA.md): prioritized research questions, data needs, methods, outputs, and decision rules.
- [`docs/RESEARCH_LIBRARY.md`](docs/RESEARCH_LIBRARY.md): generated human-readable view of the structured source library.
- [`docs/PUBLICATION_HANDOFF.md`](docs/PUBLICATION_HANDOFF.md): generated pre-publication claim/QA/disclosure handoff register.
- [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md): consolidated current-release and candidate-year control matrix with explicit blocking scope.
- [`docs/DATA_GOVERNANCE.md`](docs/DATA_GOVERNANCE.md): public-release allowlist, data-minimization rules, and restricted-data handling boundary.
- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md): short portfolio walkthrough and evidence map for hiring/research reviewers.
- [`docs/UPDATE_PLAYBOOK.md`](docs/UPDATE_PLAYBOOK.md): annual release/update procedure.
- [`docs/DATA_CALENDAR.md`](docs/DATA_CALENDAR.md): current coverage and next-release monitoring.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): current GitHub Pages publication procedure plus optional Cloudflare Pages setup.
- [`data/README.md`](data/README.md): data directory conventions.

## Current status

README does not maintain a second copy of mutable findings, QA dispositions, release counts, or verification totals. Use the owning authority for the current state:

| Question | Current authority |
| --- | --- |
| What does the analysis currently conclude? | [`docs/FINDINGS.md`](docs/FINDINGS.md) plus the topic-specific generated analyses linked in [Documentation](#documentation) |
| Which institution-level claims are publishable, held, or context-limited? | [`docs/QA_RESOLUTION_LOG.md`](docs/QA_RESOLUTION_LOG.md), [`docs/MEDIUM_QA_RESOLUTION_LOG.md`](docs/MEDIUM_QA_RESOLUTION_LOG.md), and [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md) |
| What is the current next-release / year-advance state? | [`docs/FRESHNESS_MONITOR.md`](docs/FRESHNESS_MONITOR.md) and the candidate-year preflight/watchlist documents |
| Which research questions are complete, open, or awaiting new data? | [`docs/RESEARCH_AGENDA.md`](docs/RESEARCH_AGENDA.md) |
| Which sources, definitions, vintages, and update routes apply? | [`docs/POPULATION_CROSSWALK.md`](docs/POPULATION_CROSSWALK.md), [`docs/RESEARCH_LIBRARY.md`](docs/RESEARCH_LIBRARY.md), and [`docs/SOURCE_UPDATE_TRIAGE.md`](docs/SOURCE_UPDATE_TRIAGE.md) |
| What is cleared for publication? | [`docs/PUBLICATION_HANDOFF.md`](docs/PUBLICATION_HANDOFF.md), [`docs/DATA_GOVERNANCE.md`](docs/DATA_GOVERNANCE.md), and [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md) |
| How is the current repository verified? | [`TESTING.md`](TESTING.md) and [`docs/VALIDATION.md`](docs/VALIDATION.md) |
| How is the public site deployed? | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |

The live site and deliverables listed in [Start here](#start-here) are downstream publication artifacts. Their presence does not override the analytical, QA, freshness, or governance authorities above. Version control owns prior release state; this README intentionally does not retain a running research or validation diary.
