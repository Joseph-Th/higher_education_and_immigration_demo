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
- `UNITID`, `INSTNM`, `STABBR`, `CONTROL`, `DEGGRANT`, and `PSET4FLG` in the institutional directory;
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

`scripts/validate_benchmarks.py` compares independently derived national results against selected rows from NCES Digest of Education Statistics 2025, Table 306.10.

The audit covers four measures for each year from 2019 through 2024:

- total fall enrollment;
- U.S. nonresident enrollment;
- undergraduate U.S. nonresident enrollment;
- graduate/postbaccalaureate U.S. nonresident enrollment.

This produces **24 metric-year checks**. All currently pass their documented consistency thresholds.

The thresholds are intentionally stricter for the total-enrollment universe (0.02%) than for subgroup counts (1.0%). The Digest values are rounded to one decimal thousand and were prepared from a different publication vintage than the files currently posted by IPEDS, so subgroup equality is not expected to be exact.

For 2024:

- current total fall enrollment is **19,659,633** versus approximately **19,659,600** in the Digest, a **+0.0002%** difference;
- current U.S. nonresident enrollment is **1,044,137** versus approximately **1,047,100**, a **-0.2830%** difference;
- current undergraduate U.S. nonresident enrollment is **488,236** versus approximately **490,900**, a **-0.5427%** difference;
- current graduate U.S. nonresident enrollment is **555,901** versus approximately **556,100**, a **-0.0358%** difference.

Source: https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp

The audit output is committed as `data/benchmark_audit.csv`. The public-site data build refuses to proceed if any benchmark check has failed.

This design is deliberate: the external publication is a validation source, not an input. Current IPEDS values are never overwritten merely to reproduce an older Digest vintage.

## Repository test suite

`tests/test_research_product.py` verifies the generated research product after the pipeline is rebuilt. Current checks include:

- year coverage;
- all 50 states plus DC in every year;
- state aggregates reconciling exactly to national totals;
- public, private nonprofit, and private for-profit aggregates reconciling exactly to national totals;
- undergraduate + graduate values reconciling to total enrollment;
- published shares recalculating from counts;
- latest-year institution output sorted correctly;
- findings reconciling to source tables;
- state change summary coverage and 2019 recovery classification;
- institution endpoint accounting reconciling continuing institutions and universe entry/exit to national change;
- QA and external benchmark checks all passing;
- public download files exactly matching the generated source outputs;
- local site assets existing and HTML IDs remaining unique.

The current suite contains **14 tests**.

## One-command validation

Run:

```bash
python scripts/validate_project.py
```

This rebuilds and validates the entire offline product in dependency order. A successful run ends with `VALIDATION PASS`.

## Browser publication smoke test

`scripts/browser_smoke.py` is a separate publication-QA lane because it requires Playwright and an installed Chromium runtime. It is intentionally not part of the offline data-validation command.

The browser test starts a local server on an ephemeral port and checks both desktop and 390px mobile viewports for:

- successful site/data loading;
- no page exceptions or console errors;
- rendered headline metrics matching `site_data.json`;
- all 51 state/DC selector options;
- expected institution and benchmark table row counts;
- rendered SVG charts, including the institution-dynamics chart;
- working public CSV downloads; and
- no unintended page-level horizontal overflow.

Run it after `python scripts/validate_project.py` and before deployment.

## Publication checks

The static brief exposes:

- source and release notes;
- the population definition;
- provisional status for 2024;
- chart-level source notes;
- methodology and limitations;
- downloadable national, state, institution, institution-change, source-manifest, schema-audit, benchmark-audit, and external-reference files.
