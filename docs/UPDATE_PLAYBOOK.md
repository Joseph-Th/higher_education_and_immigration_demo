# Annual Update Playbook

This project is designed to behave like a recurring higher-education data product. The update process is explicit so a new IPEDS release can be incorporated without silently changing definitions or rewriting prior results.

## 1. Confirm the new release

Before changing code, verify on the NCES/IPEDS Complete Data Files page that both of these files are available for the new fall year:

- `EFyyyyA`: Fall Enrollment by race/ethnicity, gender, attendance status, and level of student.
- `HDyyyy`: institutional directory information.

For a quick endpoint check, run `python scripts/check_for_new_release.py`. Treat its result as a release-detection aid, then confirm status and documentation on NCES before updating the analysis.

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
- `docs/BRIEFING_NOTE.md`.

Investigate the reason-coded high- and medium-priority review queue before updating the narrative. A queue item is not automatically an error. Determine whether the movement is plausible, concentrated in a few institutions, associated with an imputation/status change, related to analytic-universe membership, or a source discontinuity that needs further review.

For institution-level claims, update `data/qa_resolution_log.csv` with the evidence review. Use official institutional, system, regulator, or primary-source documentation when possible. Outside counts must not be treated as exact IPEDS benchmarks unless their population, reference date, geography, and inclusion rules are demonstrably comparable. Classify reviewed records as `safe_with_context` only when the evidence supports the direction or structural interpretation; otherwise use `hold_for_confirmation`. Never edit the IPEDS value merely to make it agree with an outside source.

Run `python scripts/build_qa_resolution_log.py` after editing the log. The build will fail if a reviewed UNITID is no longer in the current high-priority queue, which is intentional: manual dispositions belong to a specific release and must be reconsidered when the queue changes.

The required reviewed sample must include the ten highest-impact current high-priority rows in queue order; additional cases can be included for distinct structural scenarios such as confirmed closures. Run `python scripts/check_qa_evidence.py` before publication to catch broken evidence links. HTTP 401/403 results require manual browser verification rather than automatic removal of the evidence record.

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

Regenerate all state profiles with `python scripts/build_state_profiles.py`. Review the profile index for outliers, then spot-check at least one growing state, one declining state, and one small-count state. Confirm the state explorer links to the matching generated profile after browser QA.

Review `data/research_agenda.csv` after the new release. Close, reframe, or reprioritize questions whose evidence trigger has changed; add new questions only when the population, decision need, required data, proposed method, and interpretation boundary can be stated explicitly. Regenerate `docs/RESEARCH_AGENDA.md` through the normal validation lane.

Re-read the generated briefing note as a stakeholder product. Its numbers are derived automatically, but its monitoring questions and interpretation boundaries must still remain appropriate as the evidence changes.

## 8. Visual review and deployment

Run `python scripts/browser_smoke.py`, then inspect desktop and mobile layouts before publication. Confirm charts, tables, links, downloads, and source notes render correctly.

Cloudflare Pages can publish the `site/` directory directly. See `docs/DEPLOYMENT.md`.

## Update completion criteria

An annual update is complete only when:

- provenance is current;
- schema checks pass or documented changes are resolved;
- all automated QA checks pass;
- institution-specific claims derived from flagged rows have an explicit current disposition or remain withheld;
- external benchmark differences are understood and recorded;
- public findings are re-reviewed rather than carried forward automatically;
- the rendered site is inspected; and
- the deployed site serves the same files that passed validation.

