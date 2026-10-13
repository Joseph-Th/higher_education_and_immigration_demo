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
- latest-release review reconciling national, student-level, state, and institution-accounting changes and reproducing its priority counts;
- QA resolution entries remaining tied to current high-priority queue records, using unique UNITIDs, HTTPS evidence, valid review dates, explicit publication classes, and matching generated documentation;
- the QA resolution sample covering the ten highest-impact rows in the current deterministic high-priority queue so the core reviewed sample cannot be silently cherry-picked;
- the generated research memo reproducing validated headline/latest-release values and the three featured analyst case studies in both Markdown and HTML;
- the population/source crosswalk containing exactly the six required research concepts, HTTPS sources, an explicit undocumented-student exclusion in the IPEDS row, and matching generated Markdown/HTML;
- the recurring-report register containing exactly the three target-role products, valid foreign keys into the Research Library and population crosswalk, partner-confirmed scheduling language, and matching Markdown/HTML;
- structured Research Library metadata having unique IDs, HTTPS URLs, current review dates, and matching generated documentation;
- Research Library population/topic and workflow-stage metadata remaining nonblank and the searchable public interface exposing the expected filters;
- publication-handoff claims remaining unique, linked to valid Research Library IDs, tied to current headline/latest-release/QA values, and rendered consistently in Markdown/HTML;
- the public-release register containing only approved non-person-level/non-immigration-status artifacts, expanding to the complete governed download set, and matching every published file byte-for-byte;
- a negative release-control test that deliberately injects an unregistered file into `site/downloads/`, verifies that validation rejects it, removes it, and verifies the tree returns to a clean state;
- `site/data/` containing exactly the two approved machine-readable site payloads and no unregistered extras;
- stakeholder briefing note reproducing validated headline/latest-release values and interpretation boundaries;
- Excel workbook ZIP integrity, required six-sheet structure, formula presence, and current headline value;
- PDF research brief structure, exact three-page count, exact public-copy equality, and SHA-256 freshness against the current generated research memo;
- 51 state/DC profiles covering exactly the analytic geographies, reconciling their latest counts to the national total, publishing byte-identical Markdown copies, and matching the machine-readable state-profile dataset;
- structured research agenda with unique IDs, valid priorities, both current-data and external-data questions, and matching generated documentation;
- QA and external benchmark checks all passing;
- public download files exactly matching the generated source outputs;
- local site assets existing and HTML IDs remaining unique.

The current suite contains **28 tests**.

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
- rendered SVG charts, including the institution-dynamics and latest-release review charts;
- the latest-release high-priority review count matching `site_data.json`;
- working public CSV downloads;
- working public Research Library and Research Agenda CSV/Markdown, QA resolution CSV/Markdown, research memo, stakeholder briefing-note, Excel-workbook, state-profile index, and state-profile downloads;
- working public population-crosswalk CSV/Markdown, recurring-report register CSV/Markdown, and PDF research-brief downloads;
- searchable Research Library behavior, including text, resource-type, and population/topic filtering;
- publication-handoff rendering with 11 claim/control cards, five release gates, current headline value, download, portfolio boundary, and responsive layout;
- data-governance rendering with 32 registered artifact families, 82 expanded public files, five release controls, restricted-data boundary, governed downloads, and responsive layout;
- anchored sections clearing the sticky header; and
- a shareable California state-profile page rendering the correct query-selected state, ten-year series, five institution rows, profile-note link, and responsive layout; and
- a standalone research memo rendering the validated headline and all three analyst case studies at desktop and mobile widths; and
- a population/source crosswalk rendering all six required definitions at desktop and mobile widths; and
- a recurring-research-operations page rendering all three products, seven lifecycle controls, the portfolio/non-affiliation boundary, and responsive layout; and
- no unintended page-level horizontal overflow.

Run it after `python scripts/validate_project.py` and before deployment.

`scripts/check_qa_evidence.py` is a separate online evidence-health lane. It checks every external URL referenced by the manual QA resolution log, distinguishes HTTP 401/403 access restrictions from broken resources, and fails on broken URLs or network-level uncertainty. It remains outside the offline validation command so publication reproducibility does not depend on third-party web availability.

`scripts/check_population_crosswalk.py` applies the same online-health principle to the six methodology sources referenced by `data/population_crosswalk.csv`. HTTP 401/403 responses are recorded as script-access restrictions that require manual browser review; actual broken URLs and network uncertainty fail the check. The crosswalk itself remains fully reproducible offline.

## PDF publication freshness

`scripts/build_pdf_brief.py` renders `site/research-memo.html` to the canonical `deliverables/research_brief.pdf` and publishes an exact copy under `site/downloads/`. The builder writes `deliverables/research_brief_manifest.json` with the memo SHA-256, PDF SHA-256, and byte size.

The repository tests recalculate both hashes. This prevents a data or memo update from leaving an older PDF beside newer web content. PDF generation requires Playwright/Chromium, but freshness verification is offline once the PDF has been built.

## Publication checks

The static brief exposes:

- source and release notes;
- the population definition;
- provisional status for 2024;
- chart-level source notes;
- methodology and limitations;
- downloadable PDF research brief, Excel analysis workbook, national, state, institution, institution-change, latest-release QA queue/memo, analyst QA resolution log, research memo, population/source crosswalk, recurring-report operations register, publication handoff, data-governance note and public-release register, stakeholder briefing note, structured/searchable Research Library, source-manifest, schema-audit, benchmark-audit, and external-reference files.
