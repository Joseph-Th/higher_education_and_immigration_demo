# U.S. Nonresident Students in Higher Education

Portfolio research project analyzing national and state-level enrollment trends for U.S. nonresident students in American higher education using the U.S. Department of Education's Integrated Postsecondary Education Data System (IPEDS).

The project is designed as a compact, reproducible research product rather than a generic dashboard. It emphasizes source quality, data definitions, QA/QC, methodological documentation, clear writing, and communication of limitations.

## Research question

How did fall enrollment of U.S. nonresident students change across the United States from 2015 through 2024, and how did those changes vary by state and student level?

## Outputs

- A polished static research brief in [`site/`](site/) with national, level, state, and institution views.
- Interactive charts and a state explorer designed for nontechnical readers.
- Reproducible source-data collection and transformation scripts.
- A transparent methodology and data-quality record.
- Downloadable analysis tables, source lineage, schema audit, and external benchmark audit.
- A generated latest-release review packet with reason-coded institution-level QA triage.
- A generated stakeholder briefing note that translates validated findings into a concise management-facing update.
- A reviewer-ready Excel workbook with formula-driven KPIs, state lookup, reconciliation checks, benchmark QA, and source metadata.
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
python scripts/build_research_library.py
python scripts/summarize_findings.py
python scripts/validate_benchmarks.py
python scripts/build_briefing_note.py
python scripts/build_site_data.py
```

The public analysis uses degree-granting institutions in the IPEDS First Look/Digest Title IV universe (`DEGGRANT=1` and `PSET4FLG` in `1,3`) located in the 50 states and District of Columbia. This selection makes the headline national total directly benchmarkable against NCES Digest tables.

For the complete offline rebuild and validation path, run:

```bash
python scripts/validate_project.py
```

That command compiles the Python code, reruns the schema audit, rebuilds all derived data, reruns 24 NCES Digest consistency checks, regenerates the public site data, and runs the repository test suite.

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
```

The second command verifies every maintained Research Library URL and reports redirects/status without making a live website a dependency of the reproducible analysis build. Script-blocking HTTP 401/403 responses are surfaced as access restrictions requiring manual browser review rather than misclassified as dead links.

## Documentation

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md): scope, audience, questions, and deliverables.
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md): source inventory and release notes.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md): definitions, analytic unit, QA/QC plan, and limitations.
- [`docs/VARIABLE_MAPPING.md`](docs/VARIABLE_MAPPING.md): verified cross-year variables and aggregation codes.
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md): definitions for generated analysis and audit outputs.
- [`docs/VALIDATION.md`](docs/VALIDATION.md): implemented QA checks and independent NCES benchmark.
- [`docs/FINDINGS.md`](docs/FINDINGS.md): current analytical findings with exact supporting figures.
- [`docs/LATEST_UPDATE_REVIEW.md`](docs/LATEST_UPDATE_REVIEW.md): generated review of the newest annual release and its QA queue.
- [`docs/BRIEFING_NOTE.md`](docs/BRIEFING_NOTE.md): generated stakeholder briefing with implications, monitoring questions, and interpretation boundaries.
- [`docs/EXCEL_WORKBOOK.md`](docs/EXCEL_WORKBOOK.md): workbook contents, authority boundaries, QA features, and maintenance notes.
- [`docs/RESEARCH_LIBRARY.md`](docs/RESEARCH_LIBRARY.md): generated human-readable view of the structured source library.
- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md): short portfolio walkthrough and evidence map for hiring/research reviewers.
- [`docs/UPDATE_PLAYBOOK.md`](docs/UPDATE_PLAYBOOK.md): annual release/update procedure.
- [`docs/DATA_CALENDAR.md`](docs/DATA_CALENDAR.md): current coverage and next-release monitoring.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): Cloudflare Pages publication instructions.
- [`data/README.md`](data/README.md): data directory conventions.

## Current status

The research brief is built locally and passes both the complete offline validation path and the browser publication smoke test at desktop and 390px mobile widths. Primary-source collection covers 2015-2024 with 40 official NCES data/dictionary archives and SHA-256 provenance. The cross-year schema audit passes all ten years, the normalized analytic universe contains 40,549 institution-year records, 18 repository tests pass, and 24 external NCES Digest consistency checks pass across 2019-2024. A six-sheet Excel review workbook is tracked as a downstream presentation artifact and published with the site. The Research Library contains 11 reviewed resources from NCES and the Higher Ed Immigration Portal, including the three recurring research products named in the target role. Portal pages that block scripted requests are explicitly routed to manual browser review instead of being treated as broken links.

Current substantive findings include a graduate-driven decade-level increase, 33 states/DC at or above their 2019 U.S. nonresident enrollment by 2024, concentration of roughly half of national U.S. nonresident enrollment in the 100 largest institutions, a shift toward private nonprofit institutions, and evidence that national growth occurred within continuing institutions rather than being created by a larger institution universe. The newest-release review also identifies a short-run composition shift: 2023-2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment decreased by 2,053. The site surfaces small release-vintage differences between the March 2026 Digest and the later IPEDS files instead of forcing the current data to reproduce an older publication.

The static site is ready for Cloudflare Pages deployment once a remote or direct-upload target is configured.

