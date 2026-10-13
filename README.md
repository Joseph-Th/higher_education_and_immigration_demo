# U.S. Nonresident Students in Higher Education

Portfolio research project analyzing national and state-level enrollment trends for U.S. nonresident students in American higher education using the U.S. Department of Education's Integrated Postsecondary Education Data System (IPEDS).

The project is designed as a compact, reproducible research product rather than a generic dashboard. It emphasizes source quality, data definitions, QA/QC, methodological documentation, clear writing, and communication of limitations.

![Research brief preview](docs/assets/research-brief-preview.png)

**Live publication:** https://joseph-th.github.io/higher_education_and_immigration_demo/

## Start here

For a quick review of the finished work:

1. [Live research publication](https://joseph-th.github.io/higher_education_and_immigration_demo/) - interactive national/state analysis, methods, QA, and public downloads.
2. [`deliverables/research_brief.pdf`](deliverables/research_brief.pdf) - three-page policy/research writing sample with findings, analyst QA decisions, and methods/source trail.
3. [`docs/POPULATION_CROSSWALK.md`](docs/POPULATION_CROSSWALK.md) - source-selection guide distinguishing IPEDS, immigrant-origin, SEVIS international, undocumented, pipeline, and refugee/asylee concepts.
4. [`docs/RECURRING_REPORT_REGISTER.md`](docs/RECURRING_REPORT_REGISTER.md) - portfolio operations model for partner intake, methodology-change review, QA, publication gating, and institutional-knowledge handoff across the three recurring reports named in the target role.
5. [`deliverables/ipeds_portfolio_analysis.xlsx`](deliverables/ipeds_portfolio_analysis.xlsx) - formula-driven Excel review workbook with state lookup, reconciliation, benchmark QA, and source metadata.
6. [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) - evidence map from research responsibilities to specific files, scripts, and validation outputs.

The interactive publication is under [`site/`](site/); deployment instructions are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Research question

How did fall enrollment of U.S. nonresident students change across the United States from 2015 through 2024, and how did those changes vary by state and student level?

## Outputs

- A polished static research brief in [`site/`](site/) with national, level, state, and institution views.
- Interactive charts and a state explorer designed for nontechnical readers.
- Reproducible source-data collection and transformation scripts.
- A transparent methodology and data-quality record.
- Downloadable analysis tables, source lineage, schema audit, and external benchmark audit.
- A generated latest-release review packet with reason-coded institution-level QA triage.
- An analyst-reviewed QA resolution log that documents evidence, disposition, and publication decisions for selected high-priority flags without rewriting source values.
- A standalone research memo in Markdown and HTML that combines validated findings, interpretation boundaries, and three evidence-backed analyst case studies.
- A reviewer-ready three-page PDF research brief generated from the validated memo, with a source/PDF SHA-256 manifest that detects stale publication copies.
- A generated stakeholder briefing note that translates validated findings into a concise management-facing update.
- A reviewer-ready Excel workbook with formula-driven KPIs, state lookup, reconciliation checks, benchmark QA, and source metadata.
- Fifty-one generated state/DC research profiles linked directly from the interactive state explorer.
- A structured population/source crosswalk covering IPEDS U.S. nonresident, immigrant-origin, SEVIS international, undocumented higher-education, undocumented high-school-graduate, and refugee/asylee research concepts.
- A relational recurring-report register for the three named research products, linked to the Research Library and population crosswalk rather than maintained as disconnected prose.
- A structured research agenda/data-needs register that separates immediately answerable IPEDS questions from work requiring partner or population-specific data.
- A structured Research Library describing source scope, update pattern, project use, and review date.
- A documented annual update workflow and deployment path.
- Separate offline data validation and browser-level publication QA lanes.

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
python scripts/build_update_review.py
python scripts/build_qa_resolution_log.py
python scripts/build_research_library.py
python scripts/build_population_crosswalk.py
python scripts/build_recurring_report_register.py
python scripts/build_research_agenda.py
python scripts/summarize_findings.py
python scripts/validate_benchmarks.py
python scripts/build_state_profiles.py
python scripts/build_briefing_note.py
python scripts/build_research_memo.py
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
- [`docs/VARIABLE_MAPPING.md`](docs/VARIABLE_MAPPING.md): verified cross-year variables and aggregation codes.
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md): definitions for generated analysis and audit outputs.
- [`docs/VALIDATION.md`](docs/VALIDATION.md): implemented QA checks and independent NCES benchmark.
- [`docs/FINDINGS.md`](docs/FINDINGS.md): current analytical findings with exact supporting figures.
- [`docs/LATEST_UPDATE_REVIEW.md`](docs/LATEST_UPDATE_REVIEW.md): generated review of the newest annual release and its QA queue.
- [`docs/QA_RESOLUTION_LOG.md`](docs/QA_RESOLUTION_LOG.md): evidence-backed analyst dispositions for selected high-priority annual QA flags.
- [`docs/RESEARCH_MEMO.md`](docs/RESEARCH_MEMO.md): concise reviewer-facing writing sample built from validated findings and QA decisions.
- [`docs/BRIEFING_NOTE.md`](docs/BRIEFING_NOTE.md): generated stakeholder briefing with implications, monitoring questions, and interpretation boundaries.
- [`docs/EXCEL_WORKBOOK.md`](docs/EXCEL_WORKBOOK.md): workbook contents, authority boundaries, QA features, and maintenance notes.
- [`docs/RESEARCH_AGENDA.md`](docs/RESEARCH_AGENDA.md): prioritized research questions, data needs, methods, outputs, and decision rules.
- [`docs/RESEARCH_LIBRARY.md`](docs/RESEARCH_LIBRARY.md): generated human-readable view of the structured source library.
- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md): short portfolio walkthrough and evidence map for hiring/research reviewers.
- [`docs/UPDATE_PLAYBOOK.md`](docs/UPDATE_PLAYBOOK.md): annual release/update procedure.
- [`docs/DATA_CALENDAR.md`](docs/DATA_CALENDAR.md): current coverage and next-release monitoring.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): Cloudflare Pages publication instructions.
- [`data/README.md`](data/README.md): data directory conventions.

## Current status

The research brief is built locally and passes both the complete offline validation path and browser publication QA at desktop and 390px mobile widths. Primary-source collection covers 2015-2024 with 40 official NCES data/dictionary archives and SHA-256 provenance. The cross-year schema audit passes all ten years, the normalized analytic universe contains 40,549 institution-year records, and 24 external NCES Digest consistency checks pass across 2019-2024. The latest-release workflow includes automated reason-coded triage and a manually reviewed evidence/disposition log for selected high-priority records. A standalone HTML/Markdown research memo and a three-page PDF brief are generated from the same validated findings, with the PDF bound to the exact memo source by SHA-256. A six-sheet Excel review workbook is tracked as a downstream presentation artifact and published with the site. The pipeline also generates 51 state/DC profiles with current composition, longitudinal change, top institutions, and a ten-year state series. A six-population methodology crosswalk makes source compatibility explicit before IPEDS is compared with immigrant-origin, SEVIS international, undocumented, high-school-pipeline, or refugee/asylee concepts. A separate recurring-report operations register links the three public products named in the target role to those source definitions and Research Library records, then defines versioned intake, methodology-change review, QA, publication gating, and archival handoff without inventing the organization's internal deadlines. The structured research agenda records that the methods crosswalk is complete while compatible companion trend data remain a separate research need. The Research Library contains 12 reviewed resources from NCES and the Higher Ed Immigration Portal, including the official IPEDS U.S. nonresident definition source and the three recurring research products named in the target role. Portal pages that block scripted requests are explicitly routed to manual browser review instead of being treated as broken links.

Current substantive findings include a graduate-driven decade-level increase, 33 states/DC at or above their 2019 U.S. nonresident enrollment by 2024, concentration of roughly half of national U.S. nonresident enrollment in the 100 largest institutions, a shift toward private nonprofit institutions, and evidence that national growth occurred within continuing institutions rather than being created by a larger institution universe. The newest-release review also identifies a short-run composition shift: 2023-2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment decreased by 2,053. The site surfaces small release-vintage differences between the March 2026 Digest and the later IPEDS files instead of forcing the current data to reproduce an older publication.

The repository is connected to GitHub and the static `site/` output is ready for a Cloudflare Pages project connected to the `main` branch. Deployment remains a separate publication step so only a locally validated build is promoted.

