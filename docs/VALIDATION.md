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
- the QA resolution layer covering all 27 current high-priority rows, with exact 100% queue coverage, 21 `safe_with_context` decisions, 6 `hold_for_confirmation` decisions, and a generated public review page so high-impact records cannot be silently cherry-picked;
- the high-priority category diagnostic covering all 27 current records, reconciling both endpoint race/ethnicity identities for all 25 continuing institutions, requiring R/Z endpoint statuses before calculating a ratio, exposing source-status pairs such as Oakwood University's `R→Z`, preserving two universe-change rows as structurally non-comparable, and reproducing the 8 strong / 3 material / 14 limited distribution without changing publication decisions;
- the medium-priority category diagnostic covering all 50 routed records in order, reconciling both endpoint race/ethnicity identities for all 49 continuing institutions, calculating ratios for 47 R/Z-comparable rows, explicitly withholding the two `P` carry-forward-imputed City College rows, preserving the one universe entry as structurally non-comparable, reproducing the 18 strong / 9 material / 20 limited / 2 status-withheld / 1 structural distribution, and retaining routing and evidence decisions as separate controls;
- the generated research memo reproducing validated headline/latest-release values and the three featured analyst case studies in both Markdown and HTML;
- the population/source crosswalk containing exactly the six required research concepts, HTTPS sources, an explicit undocumented-student exclusion in the IPEDS row, and matching generated Markdown/HTML;
- the population-trend comparison containing six canonical IPEDS observations plus six external aggregate observations, exact 2023 same-year scale values, source-linked Research Library foreign keys, a source-reported +107% immigrant-origin change, separate undocumented 2019-2021 and 2023-2024 trend segments, and explicit non-addability/state-geography boundaries in generated CSV/Markdown/HTML;
- the R06 undocumented pipeline reference containing exactly one national row plus ten 2023 state rows, source URLs matching maintained Research Library authorities, and a generated comparison reconciling to 53,000 annual high-school graduates, 358,836 higher-education students, 70.7%/70.4% national concentration, and explicit stock/flow-not-a-rate, ecological, and non-causal boundaries;
- the recurring-report register containing exactly the three target-role products, valid foreign keys into the Research Library and population crosswalk, partner-confirmed scheduling language, and matching Markdown/HTML;
- the production-cycle register containing exactly seven ordered stage gates with explicit entry, blocker, exit, next-stage, and retained-evidence controls, plus generated Markdown/HTML covering all three recurring products without inferred internal deadlines;
- the blank production-cycle log template retaining the exact 16-field schema and the validator rejecting unknown report/stage IDs, invalid statuses, and terminal records without closure dates;
- the SQL query pack containing exactly six ordered read-only queries, using joins/CTEs/window functions, rejecting mutation/DDL statements, and passing six independent reconciliation checks against canonical CSV outputs;
- the ad hoc casebook containing exactly three ordered simulated management questions, all case-level checks passing, expected recovery/latest-mover/control-driver figures, and an explicit no-client/no-SLA/no-employment-history boundary in generated Markdown/HTML;
- the state-recovery analysis containing all 50 states plus DC, preserving the 33/18 recovery split, reconciling undergraduate-plus-graduate, public-plus-private-control, and continuing-plus-entry-minus-exit accounting independently for every state, bounding concentration shares, and matching generated Markdown/HTML;
- the fixed R01 undergraduate-shift baseline containing all 50 states plus DC, reconciling +31,592 undergraduate / -2,053 graduate / +29,539 total change, preserving 45 states/DC with undergraduate growth and 6 declines, reconciling institutional-control and institution-continuity accounting for every geography, enforcing the 33,778/2,186 gross state movement and 53.53% top-five state share, and retaining explicit baseline-not-persistence language in generated Markdown/HTML;
- the private-nonprofit growth analysis containing the 1,831 UNITIDs present at either endpoint sector universe, reconciling 2015/2024 totals and undergraduate/graduate components to the private-nonprofit control series, reconciling gross positive minus gross negative movement to +82,825, enforcing deterministic positive ranks and the 34.53% top-10 share, and preserving current latest-release institution QA publication gates in the generated CSV/Markdown/HTML;
- the planning-scenario table containing one reconciled 2024 backtest and three ordered 2025 planning cases, expected baseline/actual/variance values, an ascending scenario range, blank future actual/variance fields, and explicit non-predictive boundaries in Markdown/HTML;
- the captured release-monitor snapshot containing exactly four candidate-2025 NCES assets, preserving the observed 404/404/200/200 state, and deriving `HOLD_YEAR_ADVANCE` until the complete package is available;
- the captured candidate-directory preflight preserving both candidate archive hashes, all six required directory fields, 70/70 full data/dictionary field parity, 51-state/DC coverage, zero duplicate UNITIDs, 3,864 directory-eligible rows, 3,812 shared UNITIDs, 52 entering / 56 leaving eligible UNITIDs, a -4 net frame change, the 72-to-70 field delta, and explicit no-year-advance/no-2025-enrollment boundaries;
- the hashed candidate-directory institution-change review containing exactly 154 unique affected UNITIDs, 52 directory-eligible entries, 56 exits, 46 shared attribute-change rows, deterministic reason-coded ordering, current-year leaver exposure of 612 U.S. nonresident / 17,593 total students, six shared control changes with 1,069 current nonresident students, three shared state changes with 193, 41 shared name changes with 10,184, an explicit prohibition on inferring opening/closure or candidate-year enrollment movement, and a negative corruption test proving that a CSV byte change fails the captured SHA-256 gate;
- the candidate-year QA carry-forward watchlist containing exactly 226 unique UNITIDs, reconciling 27 current high-priority rows + 50 medium-priority rows + 154 candidate-directory structural changes - 5 medium/directory overlaps, preserving zero current high-priority/directory overlaps, retaining the 25 safe-with-context / 2 held high-priority publication classes only as current-release context, and enforcing no-new-risk-score/no-disposition-inheritance/no-candidate-year-enrollment boundaries;
- the medium-priority QA routing table containing exactly 50 current medium rows, assigning every row to exactly one existing-trigger route (28 percentage movement, 11 absolute movement, 8 combined absolute/percentage, 3 structural/reporting), reconciling 25 gains / 23 declines / 2 zero-change rows to +7,806 / -9,241 / -1,435 net and 17,047 gross absolute movement, preserving the exact five candidate-directory overlaps with 2,443 current-year nonresident students, and enforcing no-new-risk-score/no-source-correction/no-publication-clearance boundaries;
- the generated freshness monitor containing exactly eleven ordered monitoring rows covering the four NCES assets, one candidate-directory structural preflight, one year-advance gate, two source-review controls, and three recurring-product triggers without inferred deadlines;
- the consolidated release-readiness matrix containing exactly `A01`-`A07` plus `Y01`, preserving non-HOLD current-release controls, `PASS_WITH_CLAIM_HOLDS` for institution-specific review/handoff, a 2/4 candidate-package `HOLD`, and separate `READY_WITH_CLAIM_LEVEL_HOLDS` versus `HOLD_YEAR_ADVANCE` decisions;
- the R07 source-update triage register covering all 17 Research Library resources exactly once, preserving 8 routine-refresh baselines, 3 methodology-review baselines, two research-question reviews, one governance review, one monitor-only source, two archival references, and explicit escalation conditions with zero inferred internal deadlines;
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

The current suite contains **50 tests**.

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
- working public population-crosswalk CSV/Markdown, population-trend comparison CSV/Markdown, undocumented-pipeline CSV/Markdown, source-update triage CSV/Markdown, recurring-report register CSV/Markdown, production-cycle CSV/Markdown, blank production-cycle log template, SQL query/audit/Markdown downloads, ad hoc case CSV/Markdown downloads, state-recovery CSV/Markdown downloads, undergraduate-shift baseline CSV/Markdown downloads, private-nonprofit growth CSV/Markdown downloads, planning-scenario CSV/Markdown downloads, release-monitor snapshot, candidate-directory preflight JSON/Markdown, candidate-directory change-review CSV/Markdown, candidate-year QA watchlist CSV/Markdown, medium-priority QA routing CSV/Markdown, medium-priority evidence-resolution CSV/Markdown, freshness-monitor CSV/Markdown downloads, release-readiness CSV/Markdown downloads, and PDF research-brief downloads;
- searchable Research Library behavior, including text, resource-type, and population/topic filtering;
- publication-handoff rendering with 17 claim/control cards, five release gates, current headline value, the R01 fixed-baseline control, R04 non-addability/vintage control, R06 stock/flow context control, R07 source-routing control, R08 candidate-year QA carry-forward control, R09 medium-priority evidence-review control, download, portfolio boundary, and responsive layout;
- undergraduate-shift rendering with +31,592 undergraduate change, 45/51 state breadth, three consecutive annual undergraduate gains, 20.6% top-ten institution concentration, nine annual intervals, ten largest state gains, six state declines, explicit baseline-not-persistence language, governed downloads, and responsive layout;
- release-readiness rendering with eight scoped gates, `READY_WITH_CLAIM_LEVEL_HOLDS` for the current 2024 publication, `HOLD_YEAR_ADVANCE` for candidate 2025, 13 retained institution-specific claim holds across high and medium review layers, the 2/4 candidate-package observation, governed downloads, portfolio boundary, and responsive layout;
- data-governance rendering with 74 registered artifact families, 124 expanded public files, five release controls, restricted-data boundary, governed downloads, and responsive layout;
- production-cycle rendering with seven ordered stage controls, three recurring-product packets, zero inferred internal deadlines, the blank live-cycle log download, governed downloads, and responsive layout;
- SQL-analysis rendering with six query cards, six passing reconciliation rows, public query/audit downloads, the ephemeral-database authority boundary, and responsive layout;
- ad-hoc-analysis rendering with three simulated request cards, three passing checks, explicit no-real-requester/no-deadline boundary, governed downloads, and responsive layout;
- state-recovery rendering with the 33/18 recovery split, 2019-2024 national reconciliation, student-level and institutional-control drivers, largest-gain/shortfall tables, explicit accounting-not-causality boundary, governed downloads, and responsive layout;
- private-nonprofit growth rendering with the +82,825 sector change, +83,792 graduate contribution, 729 positive contributors, 34.5% top-10 gross-positive share, current institution QA holds, governed downloads, and responsive layout;
- complete institution-QA rendering with 27/27 high-priority records, 25 context-cleared decisions, 2 holds, evidence links for every record, the flag-not-error boundary, the companion category-diagnostic link, governed downloads, and responsive layout;
- high-priority category-diagnostic rendering with 25 R/Z source-status-comparable continuing records, the exact 8 strong / 3 material / 14 limited countermovement distribution, visible endpoint status pairs, two structurally non-comparable universe exits, 25 table rows, governed CSV/Markdown downloads, explicit non-miscoding/non-reclassification language, and responsive layout;
- medium-priority-QA rendering with all 50 current medium rows routed to the exact 28/11/8/3 existing-trigger taxonomy, 25 gain / 23 decline / 2 zero-change accounting, +7,806 / -9,241 / -1,435 / 17,047 movement totals, three structural/reporting rows, five named candidate-directory overlaps representing 2,443 current-year nonresident students, governed CSV/Markdown downloads, no-new-score/no-clearance language, and responsive layout;
- medium-priority evidence-review rendering with 50/50 coverage, 39 safe-with-context decisions, 11 holds, one evidence link per row, governed CSV/Markdown downloads, source-value/no-standing-approval boundaries, and responsive layout;
- medium-priority category-diagnostic rendering with 49 continuing records but only 47 R/Z source-status-comparable ratios, the exact 18 strong / 9 material / 20 limited distribution, a separate two-row carry-forward-imputation table, one structurally non-comparable universe entry, visible `R→P` and `Z→R` status transitions, governed CSV/Markdown downloads, explicit no-second-risk-score/no-diagnosis language, and responsive layout;
- population-trend rendering with the +7.3% IPEDS 2019-2024 change, source-reported +107% immigrant-origin 2000-2023 change, +2.9% undocumented 2023-2024 change, 2023 same-year scale context, explicit `NOT ADDABLE` boundary, undocumented-vintage break, governed downloads, and responsive layout;
- undocumented-pipeline rendering with ten same-year 2023 state rows, 70.7%/70.4% national concentration, explicit `NOT A RATE` stock/flow boundary, non-causal/ecological interpretation gates, governed downloads, and responsive layout;
- source-update triage rendering with 17/17 Research Library coverage, 8 routine-refresh baselines, 3 methodology-review baselines, six special routes, five decision gates, zero inferred deadlines, governed downloads, and responsive layout;
- planning-scenarios rendering with the -4.0% backtest variance, all three forward planning values, explicit non-predictive boundary, governed downloads, and responsive layout;
- freshness-monitor rendering with the 2/4 candidate-file state, HOLD year-advance gate, four release cards, candidate-directory PASS evidence, 226-row carry-forward QA queue with five medium/directory overlaps, three recurring-product trigger cards, dated/not-continuously-live boundary, governed downloads, and responsive layout;
- candidate-directory-preflight rendering with PASS, 6/6 required fields, 70/70 full field parity, 3,864 directory-eligible rows, 3,812 shared UNITIDs, 52 entering / 56 leaving rows, -4 net change, 154-row linked institution review queue, 72-to-70 schema delta, missing-Fall-Enrollment boundary, governed downloads, and responsive layout;
- candidate-directory-change-review rendering with 154 affected UNITIDs, 52/56 frame entry/exit, 612 current-year nonresident exposure at leavers, structural reason counts, six control changes, three state changes, 41 name changes, governed CSV/Markdown downloads, explicit current-exposure-not-future-loss and opening/closure boundaries, and responsive layout;
- candidate-year-QA-watchlist rendering with 226 unique UNITIDs, the exact 27 + 50 + 154 - 5 union, five named medium/directory overlaps representing 2,443 current-year nonresident students, current 25/2 high and 39/11 medium disposition splits retained only as context, ten current high-priority carry-forwards, ten candidate-only largest-exposure rows, governed CSV/Markdown downloads, revalidation-not-inheritance language, and responsive layout;
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
- downloadable PDF research brief, Excel analysis workbook, PowerPoint management briefing, SQL query pack/audit/notes, ad hoc analysis results/casebook, state-recovery analysis/notes, undergraduate-shift baseline/notes, private-nonprofit growth analysis/notes, high- and medium-priority category diagnostics/notes, population-trend comparison/notes, source-update triage register/notes, planning-scenario table/notes, release-monitor snapshot and freshness-monitor register/notes, release-readiness matrix/notes, national, state, institution, institution-change, latest-release QA queue/memo, analyst QA resolution logs, research memo, population/source crosswalk, recurring-report operations register, stage-gated production-cycle register/notes, blank validated production-cycle log template, publication handoff, data-governance note and public-release register, stakeholder briefing note, structured/searchable Research Library, source-manifest, schema-audit, benchmark-audit, and external-reference files.
