# Methodology

## Status

This document describes the implemented method used by the current research brief. The cross-year variable mapping has been checked against the official data dictionary for every year from 2015 through 2024.

## Study period

Fall 2015 through Fall 2024.

## Unit of observation

The raw Fall Enrollment files contain multiple rows per institution representing combinations of aggregation level and student characteristics. The analysis dataset is first constructed at the institution-year level, then aggregated to state-year, institutional-control-year, and national-year levels.

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

### Companion population/source selection

The project maintains `data/population_crosswalk.csv` and generated `docs/POPULATION_CROSSWALK.md` before attempting any companion analysis involving immigrant-origin, international, undocumented, high-school-pipeline, or refugee/asylee populations.

A direct quantitative comparison is permitted only when the population definition, reference period, unit of analysis, geography, and denominator are compatible. Otherwise the outside source is treated as contextual evidence, a separate companion series, or a documented data need. In particular:

- CPS immigrant-origin estimates describe domestic first- and second-generation students and exclude temporary-study visa holders from the first-generation estimate;
- SEVIS international-student records use a different administrative system and timing from IPEDS;
- undocumented-student and undocumented-high-school-graduate products rely on modeled survey estimates rather than an observed IPEDS legal-status field; and
- the current project does not separately identify refugee/asylee students, even though those populations can be represented inside a broader immigrant-origin definition.

The crosswalk is a source-selection control, not an attempt to force these populations into one common series.

### Data minimization and public-release boundary

The current portfolio uses public administrative data and contains no person-level student records, direct student identifiers, or observed immigration-status field. Institution-level IPEDS records describe public institutional entities, not individual students.

`data/public_release_register.csv` is the authority for the downloadable public artifact tree. Each registered artifact states its source, public destination, unit of record, data class, person-level/immigration-status flags, release basis, and release rule. `scripts/build_data_governance.py` rejects raw-source paths, rejects any PUBLIC registration marked as person-level or containing observed immigration-status data, copies only registered artifacts, and fails when an unregistered file appears under `site/downloads/` or `site/data/`.

If future partner work requires restricted microdata, those inputs start nonpublic by default. Access, retention, disclosure, aggregation, and destruction rules would be governed by the actual partner agreement and applicable policy before analysis begins. Only separately reviewed aggregate outputs could be considered for the public-release register.

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
7. U.S. nonresident enrollment by institutional control: public, private nonprofit, and private for-profit.
8. Endpoint institution dynamics using `UNITID` to separate change at continuing institutions from changes associated with entering or leaving the analytic universe.
9. Latest-release QA triage comparing the newest year with the immediately preceding year, including reason-coded institution review priority.

## Aggregation rules

- Institution-year values will be summed only from the verified "all students" aggregation level needed to avoid double counting.
- State assignments will come from the same-year `HDyyyy` directory file.
- Institutional control will come from the same-year `CONTROL` field in `HDyyyy` and is aggregated only within the same analytic universe used for national/state results.
- Institution endpoint comparisons match on `UNITID`. For a continuing institution, contribution to change is its end-year minus start-year count. An institution appearing only in the end-year universe contributes its end-year count; an institution appearing only in the start-year universe contributes the negative of its start-year count.
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
- Separate continuing-institution change from analytic-universe entry/exit, and avoid treating entry/exit automatically as openings/closures.
- Distinguish true changes from institution closures, mergers, UNITID restructuring, reporting changes, or missing records where possible.
- Compare selected national totals against an independently generated IPEDS table or other NCES output before publication.

### Latest-release review rules

`scripts/build_update_review.py` creates a deterministic review queue for the newest year. The queue is triage, not automated error detection.

For continuing institutions, review priority increases when any of these conditions apply:

- absolute U.S. nonresident enrollment change is at least 250, 500, or 1,000 students for low, medium, or high priority respectively;
- percentage change is at least 25%, 50%, or 100% from a prior-year baseline of at least 100 students;
- a zero/nonzero endpoint discontinuity conflicts with substantial recent history; or
- the imputation/status flag changes to or from a code other than reported (`R`) or implied zero (`Z`).

Institutions entering or leaving the analytic universe are always surfaced at low priority, and move to medium priority when the affected endpoint includes at least 100 U.S. nonresident students. Multiple triggers can apply to one record; the highest priority is retained and every reason is written to the review output.

The review also reconciles the newest national change independently across undergraduate/graduate components, state totals, and institution-universe accounting. A failure in any reconciliation stops the build.

### Independent benchmark

The pipeline compares four national measures for each year from 2019 through 2024 against NCES Digest of Education Statistics 2025, Table 306.10: total fall enrollment, total U.S. nonresident enrollment, undergraduate U.S. nonresident enrollment, and graduate/postbaccalaureate U.S. nonresident enrollment.

All **24 metric-year checks** currently pass the documented consistency thresholds. For 2024, the pipeline total is **19,659,633** versus approximately **19,659,600** after converting the Digest's rounded value. The current U.S. nonresident subgroup is **1,044,137** versus approximately **1,047,100** in the March 2026 Digest. That small subgroup difference is retained as release-vintage evidence rather than overwritten.

Benchmark source: https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp

### Publication checks

- Every chart and headline number must be reproducible from the processed dataset.
- Every chart must state its population, time period, and source.
- Provisional data must be visibly labeled.
- Notes must distinguish counts from shares and fall snapshots from full-year enrollment.
- A separate browser smoke test must render the built site at desktop and mobile widths without console errors or unintended page-level overflow before deployment.
- The reviewer-facing PDF brief must be regenerated when `site/research-memo.html` changes. `deliverables/research_brief_manifest.json` records both the memo and PDF SHA-256 values so a stale PDF fails repository validation.
- The population/source crosswalk must render six required concepts and publish byte-identical CSV/Markdown downloads.
- The public-release register must contain only explicitly approved non-person-level artifacts, and the generated public download/data trees must contain no unregistered files.

## Limitations to carry into the final brief

1. IPEDS U.S. nonresident status is a reporting category, not a complete measure of immigrant or international-background students.
2. Fall Enrollment is a point-in-time snapshot.
3. Institution reporting practices and institutional structure can change over a ten-year period.
4. The 2024 values may be revised when final data are released.
5. State totals describe enrollment at institutions located in a state, not necessarily students' legal residence or place of origin.
6. `UNITID` matching is useful for endpoint accounting but does not resolve every merger, split, acquisition, or institutional restructuring; analytic-universe entry/exit is not synonymous with opening/closure.

