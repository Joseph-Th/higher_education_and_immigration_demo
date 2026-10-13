# Methodology

## Status

This document describes the implemented method used by the current research brief. The cross-year variable mapping has been checked against the official data dictionary for every year from 2015 through 2024.

## Study period

Fall 2015 through Fall 2024.

## Unit of observation

The raw Fall Enrollment files contain multiple rows per institution representing combinations of aggregation level and student characteristics. The analysis dataset will first be constructed at the institution-year level, then aggregated to state-year and national-year levels.

Institution identity will use the IPEDS `UNITID` key.

## Analytic universe

The public analysis is restricted to degree-granting institutions in the IPEDS First Look/Digest Title IV universe, located in the 50 states and District of Columbia.

Operationally, an institution-year is included when:

- `DEGGRANT = 1`; and
- `PSET4FLG` is `1` or `3`; and
- `STABBR` is one of the 50 states or `DC`.

NCES documents `PSET4FLG` as the derived indicator used to select institutions for First Look reports and Digest of Education Statistics tables. Using this universe provides a transparent external benchmark for the national totals.

## Population concept

The primary population is students classified by IPEDS as **U.S. nonresidents** in the Fall Enrollment survey.

This is a specific federal reporting category and is not equivalent to:

- all international students;
- all foreign-born students;
- immigrant-origin students;
- undocumented students;
- DACA recipients; or
- all noncitizens.

The public-facing language will use "U.S. nonresident" when referring to the IPEDS category and will explain the definition in plain language.

## Fall Enrollment scope

IPEDS Fall Enrollment is a snapshot rather than a full-year unduplicated count. For academic reporters, the survey generally reflects the institution's official fall reporting date or October 15. Program reporters use the applicable fall reporting window specified by IPEDS.

The project will not combine Fall Enrollment counts with 12-Month Enrollment counts in a single trend series.

## Measures

The derived measures are:

1. U.S. nonresident enrollment count by institution, state, and nation.
2. Total fall enrollment count by institution, state, and nation.
3. U.S. nonresident share of total fall enrollment.
4. Year-over-year absolute and percentage change.
5. 2015-to-2024 absolute and percentage change.
6. Undergraduate and graduate U.S. nonresident counts where the source structure permits a consistent comparison.

## Aggregation rules

- Institution-year values will be summed only from the verified "all students" aggregation level needed to avoid double counting.
- State assignments will come from the same-year `HDyyyy` directory file.
- U.S. territories and other jurisdictions are retained in raw source data and explicitly excluded from the public 50-states-plus-DC analytic universe.
- Percentage-change rankings will use a documented minimum-baseline rule to prevent tiny starting counts from dominating the ranking.

The current public brief emphasizes absolute state changes and does not publish a percentage-change ranking, so no minimum-baseline threshold is currently applied to a published ranking.

## Cross-year comparability

Each year's data dictionary is checked for:

- variable-name changes;
- label/definition changes;
- category changes;
- aggregation-level changes;
- suppression or imputation conventions;
- changes in survey instructions relevant to U.S. nonresident reporting.

A tracked variable-mapping document records the selected variables and comparability caveats.

Historical source files are not uniformly encoded. The ingestion pipeline first attempts UTF-8 with BOM handling and falls back to Windows-1252 when required. Decode errors are not ignored or replaced.

## QA/QC plan

The analysis will include at minimum:

### Source checks

- Validate each download as a ZIP archive.
- Record SHA-256 checksums and byte sizes.
- Preserve the official data dictionary alongside each raw source table.

### Structural checks

- Confirm `UNITID` uniqueness after selecting the intended aggregation level.
- Verify every enrollment record joins to an institutional directory record or document exceptions.
- Check for duplicate institution-year observations.
- Check missingness in required fields.

### Arithmetic checks

- Confirm U.S. nonresident counts are nonnegative.
- Confirm total enrollment is nonnegative.
- Confirm U.S. nonresident counts do not exceed the corresponding total enrollment for the same analytic unit.
- Recalculate published percentages from counts rather than relying on rounded display values.

### Trend checks

- Flag unusually large year-over-year changes for manual review.
- Distinguish true changes from institution closures, mergers, reporting changes, or missing records where possible.
- Compare selected national totals against an independently generated IPEDS table or other NCES output before publication.

### Independent benchmark

The 2024 national total produced by the pipeline is **19,659,633** students. NCES Digest of Education Statistics 2025, Table 306.10 publishes **19,659.6 thousand** for the same 2024 degree-granting, 50-states-plus-DC universe. The pipeline value rounds to exactly the published value.

Benchmark source: https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp

### Publication checks

- Every chart and headline number must be reproducible from the processed dataset.
- Every chart must state its population, time period, and source.
- Provisional data must be visibly labeled.
- Notes must distinguish counts from shares and fall snapshots from full-year enrollment.

## Limitations to carry into the final brief

1. IPEDS U.S. nonresident status is a reporting category, not a complete measure of immigrant or international-background students.
2. Fall Enrollment is a point-in-time snapshot.
3. Institution reporting practices and institutional structure can change over a ten-year period.
4. The 2024 values may be revised when final data are released.
5. State totals describe enrollment at institutions located in a state, not necessarily students' legal residence or place of origin.

