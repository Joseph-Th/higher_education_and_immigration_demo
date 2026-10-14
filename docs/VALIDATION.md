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
- the QA resolution layer covering all 27 current high-priority rows, with exact 100% queue coverage, 6 `safe_with_context` decisions, 21 `hold_for_confirmation` decisions, and a generated public review page so high-impact records cannot be silently cherry-picked;
- the generated research memo reproducing validated headline/latest-release values and the three featured analyst case studies in both Markdown and HTML;
- the population/source crosswalk containing exactly the six required research concepts, HTTPS sources, an explicit undocumented-student exclusion in the IPEDS row, and matching generated Markdown/HTML;
- the recurring-report register containing exactly the three target-role products, valid foreign keys into the Research Library and population crosswalk, partner-confirmed scheduling language, and matching Markdown/HTML;
- the production-cycle register containing exactly seven ordered stage gates with explicit entry, blocker, exit, next-stage, and retained-evidence controls, plus generated Markdown/HTML covering all three recurring products without inferred internal deadlines;
- the blank production-cycle log template retaining the exact 16-field schema and the validator rejecting unknown report/stage IDs, invalid statuses, and terminal records without closure dates;
- the SQL query pack containing exactly six ordered read-only queries, using joins/CTEs/window functions, rejecting mutation/DDL statements, and passing six independent reconciliation checks against canonical CSV outputs;
- the ad hoc casebook containing exactly three ordered simulated management questions, all case-level checks passing, expected recovery/latest-mover/control-driver figures, and an explicit no-client/no-SLA/no-employment-history boundary in generated Markdown/HTML;
- the state-recovery analysis containing all 50 states plus DC, preserving the 33/18 recovery split, reconciling undergraduate-plus-graduate, public-plus-private-control, and continuing-plus-entry-minus-exit accounting independently for every state, bounding concentration shares, and matching generated Markdown/HTML;
- the private-nonprofit growth analysis containing the 1,831 UNITIDs present at either endpoint sector universe, reconciling 2015/2024 totals and undergraduate/graduate components to the private-nonprofit control series, reconciling gross positive minus gross negative movement to +82,825, enforcing deterministic positive ranks and the 34.53% top-10 share, and preserving current latest-release institution QA publication gates in the generated CSV/Markdown/HTML;
- the planning-scenario table containing one reconciled 2024 backtest and three ordered 2025 planning cases, expected baseline/actual/variance values, an ascending scenario range, blank future actual/variance fields, and explicit non-predictive boundaries in Markdown/HTML;
- the captured release-monitor snapshot containing exactly four candidate-2025 NCES assets, preserving the observed 404/404/200/200 state, and deriving `HOLD_YEAR_ADVANCE` until the complete package is available;
- the generated freshness monitor containing exactly ten ordered monitoring rows covering the four NCES assets, one year-advance gate, two source-review controls, and three recurring-product triggers without inferred deadlines;
- structured Research Library metadata having unique IDs, HTTPS URLs, current review dates, and matching generated documentation;
- Research Library population/topic and workflow-stage metadata remaining nonblank and the searchable public interface exposing the expected filters;
- publication-handoff claims remaining unique, linked to valid Research Library IDs, tied to current headline/latest-release/QA values, and rendered consistently in Markdown/HTML;
- the public-release register containing only approved non-person-level/non-immigration-status artifacts, expanding to the complete governed download set, and matching every published file byte-for-byte;
- a negative release-control test that deliberately injects an unregistered file into `site/downloads/`, verifies that validation rejects it, removes it, and verifies the tree returns to a clean state;
- `site/data/` containing exactly the two approved machine-readable site payloads and no unregistered extras;
- stakeholder briefing note reproducing validated headline/latest-release values and interpretation boundaries;
- Excel workbook ZIP integrity, required six-sheet structure, formula presence, and current headline value;
- PowerPoint management deck ZIP integrity, exact six-slide count, expected management-briefing figures/text, exact public-copy equality, and source/builder/PPTX SHA-256 freshness;
- PDF research brief structure, exact three-page count, exact public-copy equality, and SHA-256 freshness against the current generated research memo;
- 51 state/DC profiles covering exactly the analytic geographies, reconciling their latest counts to the national total, publishing byte-identical Markdown copies, and matching the machine-readable state-profile dataset;
- structured research agenda with unique IDs, valid priorities, both current-data and external-data questions, and matching generated documentation;
- QA and external benchmark checks all passing;
- public download files exactly matching the generated source outputs;
- local site assets existing and HTML IDs remaining unique.

The current suite contains **37 tests**.

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
- working public Research Library and Research Agenda CSV/Markdown, QA resolution CSV/Markdown, research memo, stakeholder briefing-note, Excel-workbook, PowerPoint management-deck, state-profile index, and state-profile downloads;
- working public population-crosswalk CSV/Markdown, recurring-report register CSV/Markdown, production-cycle CSV/Markdown, blank production-cycle log template, SQL query/audit/Markdown downloads, ad hoc case CSV/Markdown downloads, state-recovery CSV/Markdown downloads, private-nonprofit growth CSV/Markdown downloads, planning-scenario CSV/Markdown downloads, release-monitor snapshot, freshness-monitor CSV/Markdown downloads, and PDF research-brief downloads;
- searchable Research Library behavior, including text, resource-type, and population/topic filtering;
- publication-handoff rendering with 11 claim/control cards, five release gates, current headline value, download, portfolio boundary, and responsive layout;
- data-governance rendering with 50 registered artifact families, 100 expanded public files, five release controls, restricted-data boundary, governed downloads, and responsive layout;
- production-cycle rendering with seven ordered stage controls, three recurring-product packets, zero inferred internal deadlines, the blank live-cycle log download, governed downloads, and responsive layout;
- SQL-analysis rendering with six query cards, six passing reconciliation rows, public query/audit downloads, the ephemeral-database authority boundary, and responsive layout;
- ad-hoc-analysis rendering with three simulated request cards, three passing checks, explicit no-real-requester/no-deadline boundary, governed downloads, and responsive layout;
- state-recovery rendering with the 33/18 recovery split, 2019-2024 national reconciliation, student-level and institutional-control drivers, largest-gain/shortfall tables, explicit accounting-not-causality boundary, governed downloads, and responsive layout;
- private-nonprofit growth rendering with the +82,825 sector change, +83,792 graduate contribution, 729 positive contributors, 34.5% top-10 gross-positive share, current institution QA holds, governed downloads, and responsive layout;
- complete institution-QA rendering with 27/27 high-priority records, 6 context-cleared decisions, 21 holds, evidence links for every record, the flag-not-error boundary, governed downloads, and responsive layout;
- planning-scenarios rendering with the -4.0% backtest variance, all three forward planning values, explicit non-predictive boundary, governed downloads, and responsive layout;
- freshness-monitor rendering with the 2/4 candidate-file state, HOLD year-advance gate, four release cards, three recurring-product trigger cards, dated/not-continuously-live boundary, governed downloads, and responsive layout;
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

## PowerPoint publication freshness

`scripts/build_management_deck.py` generates the canonical six-slide `deliverables/management_briefing_deck.pptx` directly from validated CSV/JSON outputs and publishes an exact copy under `site/downloads/`. The builder writes `deliverables/management_briefing_manifest.json` with SHA-256 hashes for the deck builder, every analytical source used by the deck, and the generated PPTX plus its byte size and slide count.

The repository tests recalculate those hashes and inspect the PPTX package for six slide XML files plus the expected management figures and interpretation text. This prevents an older deck from remaining beside refreshed data or a changed deck builder. The deck remains a downstream presentation artifact; the validated CSV/JSON outputs remain authoritative.

## Publication checks

The static brief exposes:

- source and release notes;
- the population definition;
- provisional status for 2024;
- chart-level source notes;
- methodology and limitations;
- downloadable PDF research brief, Excel analysis workbook, PowerPoint management briefing, SQL query pack/audit/notes, ad hoc analysis results/casebook, state-recovery analysis/notes, private-nonprofit growth analysis/notes, planning-scenario table/notes, release-monitor snapshot and freshness-monitor register/notes, national, state, institution, institution-change, latest-release QA queue/memo, analyst QA resolution log, research memo, population/source crosswalk, recurring-report operations register, stage-gated production-cycle register/notes, blank validated production-cycle log template, publication handoff, data-governance note and public-release register, stakeholder briefing note, structured/searchable Research Library, source-manifest, schema-audit, benchmark-audit, and external-reference files.
