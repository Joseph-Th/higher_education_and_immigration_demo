# Annual Update Playbook

This project is designed to behave like a recurring higher-education data product. The update process is explicit so a new IPEDS release can be incorporated without silently changing definitions or rewriting prior results.

## 1. Confirm the new release

Before changing code, verify on the NCES/IPEDS Complete Data Files page that both of these files are available for the new fall year:

- `EFyyyyA`: Fall Enrollment by race/ethnicity, gender, attendance status, and level of student.
- `HDyyyy`: institutional directory information.

For a quick endpoint check, run `python scripts/check_for_new_release.py`. When refreshing the reviewer-visible monitoring record, run `python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json`, then `python scripts/build_freshness_monitor.py`. Treat the captured result as a release-detection aid, then confirm status and documentation on NCES before updating the analysis.

Do not advance the year when only part of the candidate-year package is present. The freshness monitor must remain `HOLD YEAR ADVANCE` until Fall Enrollment data/dictionary and directory data/dictionary are all available; package availability then triggers schema review rather than automatic publication.

Record whether NCES identifies the release as provisional or final/revised.

## 2. Advance the project year

Edit only `scripts/project_config.py`:

- set `END_YEAR` to the new fall year;
- set `LATEST_DATA_STATUS` to the documented release status.

The collection, schema audit, analysis, findings, site-data build, and tests all use these shared constants.

## 3. Retrieve sources and preserve provenance

Run:

```bash
python scripts/fetch_ipeds.py
```

Review `data/source_manifest.csv` before continuing. Confirm:

- four new records exist for the new year: enrollment data, enrollment dictionary, directory data, and directory dictionary;
- URLs point to NCES;
- retrieval timestamps are current;
- SHA-256 hashes are populated;
- the expected CSV/XLSX files were extracted.

Do not overwrite an unexplained source change. If NCES replaces a file at the same URL, the changed hash is evidence of a new source vintage and should be documented.

If the new release changes a source URL, resource title, update pattern, or status note, update `data/research_library.csv` and its `last_checked` date. The normal validation lane regenerates `docs/RESEARCH_LIBRARY.md` and checks the structured metadata.

Then review the matching row in `data/source_update_triage.csv`. A URL/date-only change normally updates metadata without changing analysis; a method-equivalent new vintage can follow the routine refresh path; a definition, denominator, model, schema, geography, timing, privacy, or material-conclusion change must follow the applicable escalation route. Run `python scripts/build_source_update_triage.py` after library or routing changes. The triage register is a portfolio control and must not be used to infer partner deadlines from public release dates.

## 4. Run the schema audit before analysis

Run:

```bash
python scripts/audit_ipeds_schema.py
```

Review the new row in `data/schema_audit.csv`. Specifically verify:

- `EFNRALT`, `EFTOTLT`, and `EFALEVEL` still exist;
- `EFALEVEL` codes 1, 2, and 12 retain their expected meanings;
- `CONTROL`, `DEGGRANT`, `PSET4FLG`, and state fields remain available;
- terminology or definition changes are reflected in `docs/VARIABLE_MAPPING.md` and `docs/METHODOLOGY.md`.

If a variable or label changes, stop. Do not make the new year fit the old schema by assumption.

If the candidate institutional directory and dictionary arrive before Fall Enrollment, run a bounded directory-side preflight rather than either ignoring the files or prematurely advancing the project year:

```bash
python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json
python scripts/check_candidate_directory.py --write-snapshot data/candidate_directory_preflight.json
python scripts/build_candidate_directory_preflight.py
python scripts/build_candidate_directory_change_review.py
python scripts/build_update_review.py
python scripts/build_medium_priority_review.py
python scripts/build_qa_resolution_log.py
python scripts/build_candidate_year_qa_watchlist.py
python scripts/build_freshness_monitor.py
```

The preflight may validate required directory fields, full data/dictionary field parity, dictionary titles, 50-states-plus-DC coverage, UNITID uniqueness, current directory-side eligibility, control/state/name continuity, archive hashes, and schema additions/removals. The live capture also writes `data/candidate_directory_change_review.csv`, which classifies every directory-side entry/exit and every shared eligible attribute change, attaches only canonical current-year enrollment exposure, and is SHA-256-bound to the preflight snapshot. Review that queue before the enrollment package arrives so control/state/name continuity issues are already known. Then build `data/candidate_year_qa_watchlist.csv`: it unions every current high/medium annual-review signal with every candidate-directory structural change and deduplicates by UNITID. Existing high-priority publication dispositions are retained only as historical/current-release context. They must be revalidated against the next complete release and must never be inherited as standing approval. Current-year exposure is a prioritization device, not a candidate-year estimate. Directory absence does not prove closure, directory entry does not prove a new institution, and state/control/name changes do not by themselves establish student movement. The preflight and watchlist must not add candidate archives to `data/source_manifest.csv`, call the directory-side frame the final analytic universe, calculate candidate-year enrollment, resolve R01, or change `END_YEAR`. Those actions remain blocked until the Fall Enrollment data and dictionary are available and the complete annual package enters the normal collection/schema/QA workflow.

## 5. Rebuild and inspect changes

Run the complete offline validation:

```bash
python scripts/validate_project.py
```

Then review the newly generated:

- `data/processed/national_year.csv`;
- `data/processed/state_year.csv`;
- latest institution detail file;
- `data/qa_report.json`;
- `data/findings.json`.
- `data/processed/latest_release_institution_review.csv`;
- `docs/LATEST_UPDATE_REVIEW.md`.
- `data/qa_resolution_log.csv` and `docs/QA_RESOLUTION_LOG.md`;
- `data/high_priority_category_diagnostic.csv`, `docs/HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md`, and `site/high-priority-category-diagnostic.html`;
- `data/medium_priority_review.csv`, `docs/MEDIUM_PRIORITY_REVIEW.md`, and `site/medium-priority-review.html`;
- `data/medium_qa_resolution_log.csv`, `docs/MEDIUM_QA_RESOLUTION_LOG.md`, and `site/medium-qa-review.html`;
- `data/medium_priority_category_diagnostic.csv`, `docs/MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md`, and `site/medium-priority-category-diagnostic.html`;
- `data/candidate_year_qa_watchlist.csv`, `docs/CANDIDATE_YEAR_QA_WATCHLIST.md`, and `site/candidate-year-watchlist.html`;
- `docs/BRIEFING_NOTE.md`.
- `docs/RESEARCH_MEMO.md` and `site/research-memo.html`.
- `docs/POPULATION_CROSSWALK.md` and `site/methodology-crosswalk.html` when source definitions or companion-source vintages changed.
- `data/undergraduate_shift_baseline.csv`, `docs/UNDERGRADUATE_SHIFT_BASELINE.md`, and `site/undergraduate-shift.html` as the fixed R01 comparison baseline.
- `data/publication_handoff.csv`, `docs/PUBLICATION_HANDOFF.md`, and `site/publication-handoff.html`.
- `data/release_readiness.csv`, `docs/RELEASE_READINESS.md`, and `site/release-readiness.html`.
- `data/public_release_register.csv`, `docs/DATA_GOVERNANCE.md`, and `site/data-governance.html`.

Investigate the reason-coded high- and medium-priority review queue before updating the narrative. A queue item is not automatically an error. Determine whether the movement is plausible, concentrated in a few institutions, associated with an imputation/status change, related to analytic-universe membership, or a source discontinuity that needs further review.

Run `python scripts/build_medium_priority_review.py` after the annual review build. Its four routes come directly from the reasons that already produced the medium priority: structural/reporting context, absolute plus percentage movement, absolute movement, or percentage movement. Treat the route as an evidence task, not a new severity score. A candidate-directory overlap means the structural and enrollment signals should be reviewed together; it does not upgrade the row, correct the source, or grant publication clearance.

For institution-level claims, update both `data/qa_resolution_log.csv` and `data/medium_qa_resolution_log.csv` for the current high- and medium-priority queues. Use official institutional, system, regulator, or primary-source documentation when possible. Outside counts must not be treated as exact IPEDS benchmarks unless their population, reference date, geography, and inclusion rules are demonstrably comparable. Classify reviewed records as `safe_with_context` only when the evidence supports the direction, count scale, or structural interpretation with explicit limitations; otherwise use `hold_for_confirmation`. Never edit the IPEDS value merely to make it agree with an outside source, and never carry a current disposition into the next release without revalidation.

Run `python scripts/build_qa_resolution_log.py` after editing the log. The build will fail if a reviewed UNITID is no longer in the current high-priority queue, which is intentional: manual dispositions belong to a specific release and must be reconsidered when the queue changes.

Then run `python scripts/build_high_priority_category_diagnostic.py`. The diagnostic must rebuild from the new release rather than carrying prior ratios forward. For each continuing high-priority institution it reconciles the all-student race/ethnicity categories to total enrollment in both years, verifies the total-change identity, and checks the endpoint `X...` status fields. Calculate opposite-category countermovement only when every endpoint total/category status is `R` (Reported) or `Z` (Implied zero); retain other official status-coded rows but withhold the ratio. Use the ratio to prioritize source review only. A large ratio, an implied zero, or an imputation flag is not proof of miscoding, reclassification, or source error and must never override the evidence-backed `safe_with_context` / `hold_for_confirmation` decision.

After `python scripts/build_medium_qa_resolution_log.py`, run `python scripts/build_medium_priority_category_diagnostic.py`. It applies the same category identity and R/Z endpoint-status rule to the medium queue while retaining `review_route` and the evidence-backed publication class as separate fields. Rebuild both status assessment and ratio from the new source rows on every release. Rows with non-R/Z endpoints remain in the diagnostic for arithmetic and review context but receive no countermovement ratio. Do not use a large ratio or a source-status flag to upgrade severity, rewrite the source, or bypass the evidence decision; analytic-universe changes also remain structurally non-comparable.

The QA resolution log must cover every current high-priority row in queue order. The build fails when a high-priority record lacks a disposition, when a reviewed record is no longer high priority, or when the evidence record is structurally invalid. Run `python scripts/check_qa_evidence.py` before publication to catch broken evidence links. HTTP 401/403 results require manual browser verification rather than automatic removal of the evidence record.

The candidate-year watchlist is deliberately broader than the current high-priority publication review. It carries forward all current high and medium signals plus all candidate-directory structural changes so the next full-package institution QA pass has an explicit starting set. Do not convert watchlist membership into a claim that an institution will gain, lose, open, close, or remain publication-safe in the candidate year. Re-run the annual review rules and evidence checks after the full candidate-year Fall Enrollment join is built.

## 6. Refresh the external benchmark

When a new Digest Table 306.10 becomes available, add its selected-year values to `data/reference/nces_digest_2025_306_10.csv` or replace that reference with the newer Digest edition and update its provenance note.

The benchmark is an independent consistency check, not an input to the analysis. Never alter current IPEDS values merely to make them reproduce an older publication vintage.

If current files and the Digest disagree:

1. quantify the difference;
2. check whether the publications use different source vintages or release statuses;
3. verify the analytic universe;
4. document the difference; and
5. retain the current-source result unless there is evidence the pipeline is wrong.

## 7. Update public interpretation

Re-read every public claim after the rebuild. A chart may update correctly while its title or prose becomes false.

At minimum, re-check:

- whether the latest year is still the series peak;
- the largest annual decline/growth year;
- undergraduate versus graduate composition;
- the number of states above the pre-pandemic baseline;
- the leading state gains/shortfalls;
- institution and state concentration metrics;
- institutional-control findings;
- institution-universe entry/exit accounting;
- the latest-release undergraduate/graduate decomposition and QA queue;
- manual QA dispositions and whether previously reviewed institution-level claims remain publishable;
- provisional/final language.

The public page contains intentionally editorial year labels and latest-year download links in `site/index.html`; update those after the data rebuild rather than assuming configuration alone rewrites the prose.

Refresh `deliverables/ipeds_portfolio_analysis.xlsx` from the validated current outputs after the analytical narrative is settled. The workbook is a downstream presentation artifact, not an input to the analysis. Recheck its formulas, state lookup, reconciliation columns, benchmark sheet, source metadata, and chart before publication.

Regenerate `deliverables/management_briefing_deck.pptx` with `python scripts/build_management_deck.py` after the validated outputs and management narrative are current. Review all six slides for clipping, readability, chart/bar scaling, current KPI values, and population/vintage guardrails. Confirm `deliverables/management_briefing_manifest.json` hashes the current deck builder and every analytical source used by the deck. The PPTX is a downstream presentation artifact and must not become a second analytical authority.

Rebuild the SQL analysis with `python scripts/build_sql_analysis.py` after the processed CSV outputs are current. Review `sql/portfolio_queries.sql` if a source schema, year coverage, or analytical question changed; all six queries must still execute as read-only SELECT/WITH statements and every row in `data/sql_analysis_audit.csv` must remain `PASS`. The SQLite database is transient and should not be promoted into a separate source-of-truth file.

Regenerate the ad hoc casebook with `python scripts/build_ad_hoc_analysis.py`. Confirm that the three simulated questions still represent useful bounded management requests, every case-level QA check is `PASS`, and the page/notes continue to state that the scenarios are not real client requests, SLAs, or employment-history claims. Update a scenario only when it can still be answered directly from a validated authority and reconciled transparently.

Regenerate the planning/variance artifact with `python scripts/build_planning_scenarios.py`. Confirm the 2024 backtest still reconciles exactly to the current national authority, the three forward planning cases remain ordered from lower to upper, and no future scenario is presented as an observed or statistically predicted IPEDS value. When a new actual year becomes available, convert the prior forward case into an actual-versus-plan variance review before rolling the scenarios forward.

For R01, preserve `data/undergraduate_shift_baseline.csv` as the fixed 2023-2024 comparison rather than rolling its endpoint years forward. The baseline establishes +31,592 national undergraduate change, growth in 45 of 51 states/DC, the institutional-control decomposition, institution-continuity accounting, and concentration measures before the next release is observed. Once a complete new Fall Enrollment and directory package passes schema review, calculate the new latest-year undergraduate change separately and classify the shift as broadly persistent only if national undergraduate change remains positive and at least 26 of 51 states/DC also show undergraduate growth. Report magnitude and concentration separately and do not infer a cause from persistence alone.

Regenerate all state profiles with `python scripts/build_state_profiles.py`. Review the profile index for outliers, then spot-check at least one growing state, one declining state, and one small-count state. Confirm the state explorer links to the matching generated profile after browser QA.

Review `data/research_agenda.csv` after the new release. Close, reframe, or reprioritize questions whose evidence trigger has changed; add new questions only when the population, decision need, required data, proposed method, and interpretation boundary can be stated explicitly. Regenerate `docs/RESEARCH_AGENDA.md` through the normal validation lane.

Use `data/source_update_triage.csv` before opening a new agenda item from an external publication. New population/geography coverage or a material conclusion shift under stable methods can justify a research-question review; publication date, filename, or title changes alone do not.

Review `data/population_crosswalk.csv` before any companion population comparison. If a Portal/MPI/AIC/SEVIS methodology, vintage, inclusion rule, or geography changed, update the structured row and its `last_checked` date, regenerate the crosswalk, and run `python scripts/check_population_crosswalk.py`. A changed label is not enough to assume the underlying population changed; inspect the source methodology.

For R06, regenerate `data/undocumented_pipeline_comparison.csv` with `python scripts/build_undocumented_pipeline.py` only when the reviewed 2023 reference is intentionally corrected or replaced. Do not let a living Portal page silently revise the fixed 2023 state comparison. If a later report offers method-compatible same-year high-school and higher-education state estimates, create a new vintage/segment rather than overwriting the old one, and preserve the rule that annual high-school graduates are a flow while higher-education enrollment is a stock. Any stock/flow multiple remains descriptive and must not be promoted into a college-going or transition rate.

For the three recurring partner products, review `data/recurring_report_register.csv` at actual production kickoff. Confirm current partner roles, milestones, delivery format, source vintage, review windows, and sign-off ownership before replacing the guarded schedule language with any operational dates. Use `data/production_cycle_register.csv` as the shared stage gate: do not advance from kickoff, intake, method review, QA, discrepancy resolution, publication, or archive until that stage's required record exists and its exit condition is documented. Copy `data/production_cycle_log_template.csv` into the approved working location for the live cycle and validate populated records with `python scripts/validate_production_cycle_log.py <path> --require-records`; do not place a completed partner log in the public repository merely because the blank template is public. Compare the delivered methodology package with the linked population-crosswalk and Research Library records before treating the cycle as a routine update. Preserve the source package and discrepancy log so the next cycle inherits documented institutional knowledge rather than oral memory.

Re-read the generated briefing note as a stakeholder product. Its numbers are derived automatically, but its monitoring questions and interpretation boundaries must still remain appropriate as the evidence changes.

Re-read the generated research memo as a publication product. Confirm that its three featured QA cases still represent an unresolved anomaly, a corroborated movement, and a documented structural change, and that the accompanying evidence still supports the stated publication decision.

Review the generated publication handoff line by line before deployment. Confirm that every public claim still points to the correct authority and Research Library source, that the QA gate is satisfied, that provisional/release-vintage and population/geography disclosures remain accurate, and that any institution-level claims with unresolved evidence remain held. Treat this register as the last analytical review before public copy is promoted, not as a substitute for organizational sign-off.

Rebuild and review `data/release_readiness.csv` after the upstream analytical, QA, handoff, source-routing, and presentation controls are current. The current-publication decision and candidate-year decision are deliberately separate: `PASS_WITH_CLAIM_HOLDS` may coexist with a release-ready aggregate publication, while `HOLD_YEAR_ADVANCE` means the configured `END_YEAR` must remain unchanged until the complete candidate package is available and schema review begins. Do not convert either narrow hold into a broader decision than its blocker scope supports.

Review `data/public_release_register.csv` whenever a filename, output family, source type, or disclosure boundary changes. A prior year's public file list is not automatic authorization for a new release. Confirm that every intended public artifact has an explicit source and release rule, that no raw or restricted partner input is registered, and that year-specific paths such as the latest institution detail file are current. The site build must fail if an unregistered file appears in the public download/data tree.

After the memo and interpretation are final, regenerate the reviewer-facing PDF:

```bash
python scripts/build_pdf_brief.py
```

Then rerun `python scripts/validate_project.py`. The PDF manifest check will fail if the PDF was produced from an older memo source. Render and visually inspect every PDF page before publication; do not rely only on file-generation success.

## 8. Visual review and deployment

Run `python scripts/browser_smoke.py`, then inspect desktop and mobile layouts before publication. Confirm charts, tables, links, downloads, population-crosswalk cards, and source notes render correctly. Also run `python scripts/check_population_crosswalk.py` with the other live-link checks.

The current public deployment uses GitHub Pages from the validated `site/` tree on `gh-pages`; Cloudflare Pages remains an optional alternative. See `docs/DEPLOYMENT.md`.

## Update completion criteria

An annual update is complete only when:

- the release/freshness snapshot reflects the source observation used to begin the update and the year-advance gate agrees with the captured package state;
- provenance is current;
- schema checks pass or documented changes are resolved;
- all automated QA checks pass;
- institution-specific claims derived from flagged rows have an explicit current disposition or remain withheld;
- external benchmark differences are understood and recorded;
- public findings are re-reviewed rather than carried forward automatically;
- the SQL query pack executes against the refreshed processed outputs and every independent reconciliation check is `PASS`;
- the three ad hoc portfolio scenarios have been regenerated from the refreshed outputs, all case-level checks pass, and the simulation boundary remains explicit;
- the planning/variance artifact has been regenerated from the refreshed national series, the backtest reconciles, and forward scenarios remain explicitly non-predictive;
- the fixed 2023-2024 R01 undergraduate baseline still reconciles and, after a later complete release becomes available, the new latest-year result has been evaluated separately against the pre-specified national-direction and majority-of-states persistence rule rather than overwriting the baseline;
- the PowerPoint deck has been regenerated from the refreshed validated outputs, its source/builder/PPTX hashes are current, and all six slides have been visually inspected;
- the population/source crosswalk has been re-reviewed when companion-source definitions or vintages changed;
- the source-update triage register still covers every maintained Research Library resource and the applied route matches the kind of source change observed;
- the release-readiness matrix reports the correct current-publication and year-advance decisions, every current-release blocker remains non-HOLD, and any institution-specific claim holds remain explicit;
- the public-release register has been re-reviewed and the exact allowlisted public tree passes with no unregistered files;
- the PDF source hash matches the current generated research memo and every PDF page has been visually inspected;
- the rendered site is inspected; and
- the deployed site serves the same files that passed validation.

