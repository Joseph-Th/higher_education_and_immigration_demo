# U.S. Nonresident Students in Higher Education

Portfolio research demonstration using NCES/IPEDS Fall Enrollment data to show end-to-end higher-education research work: source selection, reproducible analysis, QA/QC, methodological judgment, and communication for nontechnical readers.

![Research brief preview](docs/assets/research-brief-preview.png)

**Live publication:** https://joseph-th.github.io/higher_education_and_immigration_demo/

## Start here

The core work sample is designed to be reviewable in about five minutes:

1. **[Live research publication](https://joseph-th.github.io/higher_education_and_immigration_demo/)** — headline findings, state analysis, and visible latest-release QA judgment.
2. **[`deliverables/research_brief.pdf`](deliverables/research_brief.pdf)** — two-page research/writing sample with findings, limitations, and source/QA trail.
3. **[`deliverables/management_briefing_deck.pptx`](deliverables/management_briefing_deck.pptx)** — five-slide management briefing built from the same validated outputs.

For a technical check, open **[`deliverables/ipeds_portfolio_analysis.xlsx`](deliverables/ipeds_portfolio_analysis.xlsx)** or **[`site/sql-analysis.html`](site/sql-analysis.html)**. The rest of the repository is supporting evidence, not required reading.

## Research question

How did fall enrollment of U.S. nonresident students change across the United States from 2015 through 2024, and how did those changes vary by state and student level?

## What this demonstrates

| Capability | Evidence |
| --- | --- |
| Research and source selection | Official NCES/IPEDS files, cross-year schema review, population/source crosswalk |
| Quantitative analysis | National, state, student-level, institutional-control, and institution-continuity analysis |
| QA/QC and judgment | Arithmetic reconciliation, 24 NCES benchmark checks, evidence-backed anomaly review, explicit claim holds |
| Excel / SQL / Python | Formula-driven workbook, executable SQL query pack, reproducible Python pipeline |
| Research writing | Two-page brief and public research memo |
| Leadership communication | Five-slide management briefing |
| Publication discipline | Source lineage, release readiness, claim-level controls, governed public outputs |

The primary population is the IPEDS **U.S. nonresident** reporting category. It is not treated as interchangeable with all international, immigrant-origin, undocumented, DACA, refugee/asylee, or other noncitizen populations.

## Data and method

- **Source:** National Center for Education Statistics, Integrated Postsecondary Education Data System (IPEDS).
- **Coverage:** Fall 2015 through Fall 2024, 50 states + DC.
- **Universe:** degree-granting institutions in the IPEDS First Look/Digest Title IV selection.
- **Core inputs:** `EF2015A`–`EF2024A` Fall Enrollment files and same-year `HD` institutional directory files.
- **Raw archives:** reproducibly downloaded from NCES and excluded from Git; tracked manifests preserve source URLs, retrieval metadata, file sizes, and SHA-256 hashes.

Method definitions and interpretation boundaries are documented in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) and [`docs/POPULATION_CROSSWALK.md`](docs/POPULATION_CROSSWALK.md).

## Reproduce and verify

Install the core dependencies, fetch the official source package, and run the authoritative offline rebuild:

```bash
python -m pip install -r requirements.txt
python scripts/fetch_ipeds.py
python scripts/validate_project.py
```

`validate_project.py` reruns the schema audit, rebuilds derived outputs, executes the SQL and analytical checks, validates against NCES benchmarks, rebuilds publication data, and runs the repository test suite. A successful run ends with `VALIDATION PASS`.

For browser/publication QA:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_smoke.py
```

The browser lane renders desktop and mobile layouts, exercises interactive elements, verifies public downloads, and checks for browser errors and horizontal overflow.

See [`TESTING.md`](TESTING.md) and [`docs/VALIDATION.md`](docs/VALIDATION.md) for the complete verification contract. Annual update and deployment procedures live in [`docs/UPDATE_PLAYBOOK.md`](docs/UPDATE_PLAYBOOK.md) and [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Go deeper only if useful

- [`docs/REVIEWER_GUIDE.md`](docs/REVIEWER_GUIDE.md) — compact reviewer path and role-to-evidence map.
- [`docs/FINDINGS.md`](docs/FINDINGS.md) — current analytical findings and exact supporting figures.
- [`docs/QA_RESOLUTION_LOG.md`](docs/QA_RESOLUTION_LOG.md) and [`docs/MEDIUM_QA_RESOLUTION_LOG.md`](docs/MEDIUM_QA_RESOLUTION_LOG.md) — evidence-backed institution-level publication decisions.
- [`docs/SQL_ANALYSIS.md`](docs/SQL_ANALYSIS.md) — six read-only SQL queries and independent reconciliations.
- [`docs/EXCEL_WORKBOOK.md`](docs/EXCEL_WORKBOOK.md) — workbook structure, formula-driven review, and authority boundary.
- [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md) — current-publication readiness separated from candidate-year advancement.
- [`docs/DATA_GOVERNANCE.md`](docs/DATA_GOVERNANCE.md) — public-release allowlist and data-minimization controls.

## Status boundary

The live site, PDF, PowerPoint, Excel workbook, and SQL page are downstream presentation artifacts. Validated CSV/JSON outputs and their owning QA/methodology controls remain authoritative. Current institution-specific claim holds are intentionally preserved rather than converted into unsupported narrative, and a partial next-year source package does not advance the configured analysis year.
