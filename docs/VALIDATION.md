# Validation

The project treats reproducibility and validation as part of the research product rather than as hidden implementation detail.

## Source integrity

- 40 official NCES/IPEDS archives are retrieved for 2015-2024.
- Every archive is validated as a ZIP before extraction.
- `data/source_manifest.csv` records the source URL, retrieval timestamp, byte size, SHA-256 checksum, and extracted filenames.
- Historical revised enrollment files (`*_rv.csv`) are preferred when NCES supplies them.

## Cross-year schema audit

`scripts/audit_ipeds_schema.py` checks every year for:

- `UNITID`, `EFALEVEL`, `EFTOTLT`, and `EFNRALT` in Fall Enrollment;
- `UNITID`, `INSTNM`, `STABBR`, `DEGGRANT`, and `PSET4FLG` in the institutional directory;
- the expected meanings of `EFALEVEL` codes 1, 2, and 12.

All ten years currently pass.

## Normalization and arithmetic checks

`scripts/build_analysis.py` enforces:

- one selected row per institution and aggregation level;
- complete same-year joins between selected Fall Enrollment rows and institutional directory records;
- nonnegative enrollment counts;
- U.S. nonresident enrollment no greater than corresponding total enrollment;
- an explicit 50-states-plus-DC geography rule;
- an explicit degree-granting First Look/Digest universe rule.

The resulting analytic dataset contains 40,549 institution-year records and 510 state-year records.

## Independent publication benchmark

The pipeline's 2024 total fall enrollment is **19,659,633**.

NCES Digest of Education Statistics 2025, Table 306.10 reports **19,659.6 thousand** students for 2024 in the degree-granting, 50-states-plus-DC universe. Our result rounds to exactly **19,659.6 thousand**.

Source: https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp

The public site build fails if this benchmark no longer matches, preventing a silently changed analytic universe from being published.

## Publication checks

The static brief exposes:

- source and release notes;
- the population definition;
- provisional status for 2024;
- chart-level source notes;
- methodology and limitations;
- downloadable national, state, institution, source-manifest, and schema-audit files.
