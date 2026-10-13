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
- Downloadable analysis tables, source lineage, and schema-audit files.

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
python scripts/summarize_findings.py
python scripts/build_site_data.py
```

The public analysis uses degree-granting institutions in the IPEDS First Look/Digest Title IV universe (`DEGGRANT=1` and `PSET4FLG` in `1,3`) located in the 50 states and District of Columbia. This selection makes the headline national total directly benchmarkable against NCES Digest tables.

## Documentation

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md): scope, audience, questions, and deliverables.
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md): source inventory and release notes.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md): definitions, analytic unit, QA/QC plan, and limitations.
- [`docs/VARIABLE_MAPPING.md`](docs/VARIABLE_MAPPING.md): verified cross-year variables and aggregation codes.
- [`docs/VALIDATION.md`](docs/VALIDATION.md): implemented QA checks and independent NCES benchmark.
- [`data/README.md`](data/README.md): data directory conventions.

## Current status

The first complete research brief is built locally. Primary-source collection covers 2015-2024 with 40 official NCES data/dictionary archives and SHA-256 provenance. The cross-year schema audit passes all ten years, the normalized analytic universe contains 40,549 institution-year records, and the 2024 national enrollment total independently matches NCES Digest 2025 Table 306.10 after published rounding. The static site is ready for deployment once a remote/deployment target is configured.

