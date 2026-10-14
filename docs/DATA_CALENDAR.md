# Data Calendar

This project treats data currency as an operational responsibility rather than a one-time collection task.

## Current published coverage

| Component | Latest year used | Current project treatment |
| --- | ---: | --- |
| Fall Enrollment (`EFyyyyA`) | 2024 | Provisional |
| Institutional directory (`HDyyyy`) | 2024 | Same-year join for published analysis |
| NCES Digest external benchmark | 2024 | Provisional year in Digest 2025 Table 306.10 |

The current source archives were retrieved on October 13, 2026. Exact timestamps and hashes are in `data/source_manifest.csv`.

## Next-release check

Run:

```bash
python scripts/check_for_new_release.py
```

To preserve the observation used by the public freshness monitor, run:

```bash
python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json
python scripts/check_candidate_directory.py --write-snapshot data/candidate_directory_preflight.json
python scripts/build_candidate_directory_preflight.py
python scripts/build_candidate_directory_change_review.py
python scripts/build_freshness_monitor.py
```

The script checks the NCES Complete Data Files endpoint for the next year's:

- Fall Enrollment data;
- Fall Enrollment dictionary;
- institutional directory data; and
- institutional directory dictionary.

**Last checked October 14, 2026:** the 2025 institutional directory and dictionary are available, while `EF2025A.zip` and `EF2025A_Dict.zip` are not yet available at the Complete Data Files endpoint. `data/release_monitor_snapshot.json` preserves that four-file observation at `2026-10-14T17:13:49+00:00`, and `data/freshness_monitor.csv` records the resulting `HOLD YEAR ADVANCE` decision. The project therefore remains correctly pinned to Fall 2024.

Because the directory pair is already available, `scripts/check_candidate_directory.py` performs a bounded preflight without collecting it into the canonical 2015-2024 source manifest. The capture at `2026-10-14T17:13:53+00:00` shows all six required directory fields in both the data and dictionary, exact 70/70 full-field parity between the candidate CSV and dictionary, 5,985 directory rows, all 51 states/DC, zero duplicate UNITIDs, and 3,864 directory-eligible institutions under the current geography/degree-granting/Title-IV filters. Relative to the current 2024 directory-side frame, 3,812 UNITIDs are shared, 52 enter, 56 leave, and the net eligible-frame change is -4. The candidate schema has 70 fields versus 72 in 2024; `DFRCGID` and `DFRCUSCG` are absent, but neither is required by the current analysis.

The same live capture writes `data/candidate_directory_change_review.csv` and binds it to the preflight snapshot by SHA-256. The current review contains 154 affected UNITIDs: 52 directory-side entries, 56 exits, and 46 shared eligible records with a changed name, state, institutional control, or eligible Title-IV indicator. Thirty-five entries are new directory records; 11 gain degree-granting eligibility and 6 gain the eligible Title-IV/First-Look status. Among exits, 38 lose the eligible Title-IV/First-Look status, 15 are absent from the candidate directory, and 3 lose degree-granting eligibility. Fifty-four of the 56 frame leavers appear in the current 2024 canonical institution analysis, representing 612 current-year U.S. nonresident students and 17,593 total students. These are **review-priority exposure measures only**, not projected 2025 losses, and directory absence is not treated as proof of institutional closure. The review also flags six shared control changes (1,069 current nonresident students), three shared state changes (193), and 41 shared name changes (10,184) for later full-package reconciliation. These checks reduce directory-side uncertainty only. They do not establish the final 2025 analytic universe or answer R01 because Fall Enrollment is still unavailable.

The live check is deliberately **not** part of `scripts/validate_project.py` because reproducibility of the current release should not depend on network availability or the state of a future NCES release. The offline validation lane consumes the last explicitly captured snapshot and verifies that the derived monitoring register/page agree with it.

## Research Library health check

Run:

```bash
python scripts/check_research_library.py
```

This separate online lane checks every URL in `data/research_library.csv`, follows redirects, and reports HTTP/network failures. HTTP 401/403 responses are reported separately as **scripted-access restrictions**, not silently treated as either success or a broken link; those resources require manual browser review. The command fails on network errors and other broken HTTP responses such as 404/5xx. It does not modify the recorded `last_checked` metadata automatically; a human source review is still required before changing that field. Keeping this check outside `scripts/validate_project.py` prevents temporary external-site outages from breaking the offline research build.

The Research Library also records population/topic tags and research workflow stage. Those fields are publication metadata, not inferred population equivalences: when a methodology changes, review the tag and workflow role deliberately rather than allowing the public filter taxonomy to imply comparability.

## Source-change triage

`data/source_update_triage.csv` is the R07 routing layer for the maintained Research Library. Run `python scripts/build_source_update_triage.py` after changing the library or when a source update is being assessed. The build requires every maintained `resource_id` to appear exactly once and separates the expected next action from escalation conditions.

The decision order is deliberate: metadata-only changes update the catalog; same-method new values can enter routine refresh controls; definition/model/denominator/schema/geography/timing changes require methodology review; new coverage or material same-method conclusion shifts can trigger a research-question review; privacy/handling/release-rule changes go to governance review. A public publication date is a signal to review, not evidence of an internal deadline or permission to change a public conclusion.

Do not advance `END_YEAR` merely because a directory file exists. The recurring analysis is ready to advance only when the Fall Enrollment data and its dictionary are available and pass the schema review.

## Recurring research-product operations

`data/recurring_report_register.csv` is the portfolio tracking layer for the three recurring products named in the target role. It records the latest public product/date and current publicly documented source vintage, but it intentionally does **not** infer the Presidents' Alliance's internal next deadline from those dates.

The production trigger is a confirmed partner kickoff or refreshed data/methodology package. At that point, the analyst should confirm partner roles, milestones, data vintage, delivery format, review windows, and sign-off ownership before treating the report as scheduled work. The generated `docs/RECURRING_REPORT_REGISTER.md` then provides the intake, method-change, QA, publication, and handoff checklist for each product.

`data/production_cycle_register.csv` separately governs the shared stage sequence. Its seven stages require an entry condition, evidence record, blocking rule, exit condition, next-stage handoff, and retained record. It intentionally contains no named staff or inferred internal dates; those belong only in a real production-cycle record after kickoff.

At confirmed kickoff, copy the blank `data/production_cycle_log_template.csv` into the approved working location and populate the live coordination record there. `scripts/validate_production_cycle_log.py` enforces report/stage foreign keys, controlled statuses/materiality, and closure rules. A completed partner log is operational evidence, not an automatically public artifact.

This separation between a **public publication date** and a **confirmed internal production schedule** is deliberate. A recurring title does not prove that the next cycle uses the same dates, partners, methodology, or deliverables.

## Update trigger

When the next Fall Enrollment archive becomes available:

1. confirm the release status on NCES;
2. follow `docs/UPDATE_PLAYBOOK.md`;
3. preserve the prior source lineage through manifest hashes;
4. rerun the schema audit before interpreting new values; and
5. re-review every public finding after the data rebuild.

This separation between **release detection**, **source collection**, **schema validation**, and **publication** is intentional. A newly posted file is a trigger for review, not automatic permission to publish.

The final publication stage is represented by `data/publication_handoff.csv`. Its claim-level authorities, QA gates, required disclosures, and hold/context decisions should be regenerated and reviewed after every annual data refresh before the public site is deployed.

