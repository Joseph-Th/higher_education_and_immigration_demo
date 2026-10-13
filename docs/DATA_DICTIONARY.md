# Data Dictionary

This document describes the generated, tracked data products intended for analysis, review, and publication. Raw NCES files are documented separately in `docs/DATA_SOURCES.md` and are not committed to Git.

## Common conventions

- `year` is the IPEDS fall enrollment year.
- Enrollment counts are students, not thousands.
- Percent fields ending in `_pct` are percentages on a 0–100 scale.
- The public analytic universe is degree-granting institutions in the IPEDS First Look/Digest Title IV universe (`DEGGRANT=1`, `PSET4FLG` in `1,3`) in the 50 states and District of Columbia.
- `nonresident` refers only to the IPEDS U.S. nonresident reporting category described in the methodology.

## `data/processed/national_year.csv`

One row per year.

| Field | Definition |
| --- | --- |
| `year` | Fall enrollment year |
| `institution_count` | Institutions in the analytic universe |
| `total_enrollment` | Total fall enrollment |
| `nonresident_enrollment` | U.S. nonresident fall enrollment |
| `nonresident_share_pct` | U.S. nonresident enrollment / total enrollment × 100 |
| `yoy_nonresident_pct` | Percentage change in U.S. nonresident enrollment from prior year; blank for first year |
| `undergraduate_total` | Undergraduate fall enrollment |
| `undergraduate_nonresident` | Undergraduate U.S. nonresident enrollment |
| `graduate_total` | Graduate/postbaccalaureate fall enrollment |
| `graduate_nonresident` | Graduate/postbaccalaureate U.S. nonresident enrollment |

`undergraduate_total + graduate_total` reconciles exactly to `total_enrollment` for every year. The same reconciliation applies to the U.S. nonresident fields.

## `data/processed/state_year.csv`

One row per state/DC per year, 51 rows per year.

Fields mirror the national series with two additions:

| Field | Definition |
| --- | --- |
| `state` | Two-letter institution-location abbreviation; includes `DC` |
| `institution_count` | Institutions in the analytic universe located in that geography |

State rows sum exactly to the national series for all count fields.

## `data/processed/state_change_summary.csv`

One row for each of the 50 states plus DC. This is a reviewer-friendly comparison table rather than a new source of authority.

| Field | Definition |
| --- | --- |
| `state` | State/DC abbreviation |
| `nonresident_2015` | U.S. nonresident enrollment in 2015 |
| `nonresident_2019` | Pre-pandemic baseline enrollment |
| `nonresident_2024` | Latest enrollment |
| `change_2015_2024` | Absolute 2015→2024 change |
| `change_pct_2015_2024` | Percentage 2015→2024 change |
| `change_2019_2024` | Absolute change from pre-pandemic baseline |
| `change_pct_2019_2024` | Percentage change from pre-pandemic baseline |
| `recovery_status` | `At or above 2019` or `Below 2019` |
| `nonresident_share_pct_2024` | Latest U.S. nonresident share of total state fall enrollment |

## `data/processed/state_profile_index.csv`

One row per state/DC used to inventory the 51 generated state publication products.

| Field | Definition |
| --- | --- |
| `state` / `state_name` | Geography code and display name |
| `start_year` / `baseline_year` / `latest_year` | Long-run start, recovery baseline, and current release year |
| `latest_nonresident` | Latest-year U.S. nonresident enrollment |
| `latest_share_pct` | Latest U.S. nonresident share of total enrollment |
| `change_since_start` / `change_pct_since_start` | Long-run absolute/percentage change |
| `change_since_baseline` / `change_pct_since_baseline` | Change from the pre-pandemic baseline |
| `recovery_status` | At/above or below 2019 |
| `year_over_year_change` / `year_over_year_pct` | Latest annual movement |
| `graduate_share_pct` | Graduate share of latest U.S. nonresident enrollment |
| `top_institution` / `top_institution_nonresident` | Largest latest-year institution by U.S. nonresident count |
| `profile_file` | Generated Markdown profile filename |

The sum of `latest_nonresident` across all 51 rows reconciles exactly to the latest national total.

## `data/processed/control_year.csv`

Three rows per year, one for each institutional-control category.

| Field | Definition |
| --- | --- |
| `year` | Fall enrollment year |
| `control` | `Public`, `Private nonprofit`, or `Private for-profit` |
| `institution_count` | Institutions in that control category |
| `total_enrollment` | Total fall enrollment |
| `nonresident_enrollment` | U.S. nonresident enrollment |
| `nonresident_share_pct` | U.S. nonresident share of total enrollment within that control category |
| `undergraduate_nonresident` | Undergraduate U.S. nonresident enrollment |
| `graduate_nonresident` | Graduate U.S. nonresident enrollment |

The three control rows reconcile exactly to the national totals for every year.

## `data/processed/institutions_2024.csv`

One row per institution in the latest analytic universe, sorted descending by U.S. nonresident enrollment.

Key fields:

| Field | Definition |
| --- | --- |
| `unitid` | Stable IPEDS institution identifier |
| `institution` | Institution name from the same-year directory |
| `state` | Institution location |
| `control` | Institutional control category |
| `total_enrollment` | Total fall enrollment |
| `nonresident_enrollment` | U.S. nonresident fall enrollment |
| `nonresident_share_pct` | Institution-level U.S. nonresident share |
| `undergraduate_*` / `graduate_*` | Level-specific counts |
| `*_imputation_flag` | IPEDS imputation/status code for the selected all-student row |
| `source_*_csv` | Exact raw source filenames used for the row |

## `data/processed/institution_change_summary.csv`

One row for every institution appearing in either the 2015 or 2024 analytic universe. The table is an accounting bridge between endpoint institution membership and the national change.

| Field | Definition |
| --- | --- |
| `unitid` | IPEDS institution identifier used for endpoint matching |
| `institution` | Latest available endpoint name |
| `state` | Latest available endpoint institution location |
| `status` | Continuing-growth/decline/unchanged, entered universe, or left universe |
| `control_2015` | 2015 institutional control; blank if absent from 2015 universe |
| `control_2024` | 2024 institutional control; blank if absent from 2024 universe |
| `nonresident_2015` | 2015 U.S. nonresident enrollment; blank for universe entrants |
| `nonresident_2024` | 2024 U.S. nonresident enrollment; blank for universe exits |
| `absolute_change` | Endpoint contribution to national change; entrants contribute their 2024 count and exits contribute the negative of their 2015 count |

The sum of `absolute_change` reconciles exactly to the national 2015→2024 change. Universe entry/exit should not be interpreted automatically as institutional opening/closure.

## `data/processed/latest_release_institution_review.csv`

One row for every institution appearing in either endpoint of the latest annual comparison. The current file compares 2023 with 2024 and is generated by `scripts/build_update_review.py`.

Key fields:

| Field | Definition |
| --- | --- |
| `status` | Continuing, entered analytic universe, or left analytic universe |
| `nonresident_2023` / `nonresident_2024` | Endpoint U.S. nonresident enrollment; blank when absent from that endpoint universe |
| `absolute_change` | Institution contribution to the latest national change |
| `pct_change` | Percentage change when a prior-year denominator exists |
| `flag_2023` / `flag_2024` | IPEDS imputation/status codes for the selected all-student U.S. nonresident value |
| `recent_historical_max` | Maximum U.S. nonresident count during the three years preceding the prior-year endpoint when available |
| `review_priority` | `high`, `medium`, `low`, or `none` under the documented deterministic triage rules |
| `review_reasons` | All threshold/review reasons that applied to the row |

The file is a review queue, not a list of source-data errors.

## `data/qa_resolution_log.csv`

One row per manually reviewed institution selected from the current high-priority annual QA queue. This is an analyst-decision record, not a corrected-data table.

| Field | Definition |
| --- | --- |
| `unitid` | IPEDS institution identifier; must remain present in the current high-priority review queue |
| `institution` | Institution name, checked against the current queue to catch identity/name drift |
| `reviewed_on` | ISO date of the analyst evidence review |
| `disposition` | Short analytical conclusion such as `corroborated_direction`, `expected_structural_change`, `external_scope_mismatch`, or `unresolved_discontinuity` |
| `publication_class` | `safe_with_context` or `hold_for_confirmation` |
| `evidence_label` | Human-readable description of the outside evidence source |
| `evidence_url` | HTTPS source used during manual review |
| `analyst_note` | Explanation of what the evidence does and does not establish, including population-scope caveats |

`safe_with_context` does not mean the external source exactly reproduces IPEDS. It means the reviewed evidence supports discussing the direction or structural event with explicit limitations. `hold_for_confirmation` preserves the official IPEDS value in aggregate analysis while preventing an unresolved institution-level movement from being promoted into narrative as though it had been independently verified.

The build script requires every reviewed UNITID to remain a current high-priority row. A new annual release therefore forces stale dispositions to be revisited rather than silently carrying them forward.

## `data/schema_audit.csv`

One row per source year recording whether required variables and aggregation labels pass cross-year schema review, plus the selected raw filenames and historical terminology used for `EFNRALT`.

## `data/benchmark_audit.csv`

One row per Digest metric-year comparison.

| Field | Definition |
| --- | --- |
| `year` | Comparison year |
| `metric` | Project measure being checked |
| `current_ipeds_value` | Independently derived project value in students |
| `digest_published_thousands` | Digest value as published, in thousands |
| `digest_approx_students` | Published value multiplied by 1,000 for comparison |
| `difference_students` | Current value minus approximate Digest value |
| `difference_pct` | Difference as percent of approximate Digest value |
| `consistency_threshold_pct` | Maximum absolute percentage difference accepted by the audit |
| `status` | `PASS` or `FAIL` |
| `digest_release_status` | Final/provisional status recorded for that Digest year |

The Digest reference is not used to alter project results.

## `data/source_manifest.csv`

One row per downloaded NCES ZIP archive. Fields record source year/table/type, exact URL, UTC retrieval time, archive byte size, SHA-256 digest, and extracted filenames.

## `data/research_library.csv`

One row per external source or reference resource maintained by the project.

| Field | Definition |
| --- | --- |
| `resource_id` | Stable project identifier for the resource |
| `title` | Human-readable source title |
| `publisher` | Publishing organization |
| `resource_type` | Data access, release schedule, methodology, benchmark table, or raw data archive |
| `population_tags` | Semicolon-delimited population/topic tags used by the public Research Library filter |
| `workflow_stage` | Research lifecycle role such as source collection, methodology, validation, publication context, or recurring research |
| `scope` | What the resource covers |
| `update_pattern` | Expected update/release pattern |
| `project_role` | How the project uses the resource |
| `url` | HTTPS source URL |
| `last_checked` | ISO date of the most recent recorded source review |
| `status_note` | Current release or interpretation note |

`scripts/build_research_library.py` validates required fields, unique IDs, HTTPS URLs, and ISO dates before generating the human-readable Research Library.

## `data/publication_handoff.csv`

One row per public claim or publication control in the final pre-publication handoff demonstration.

| Field | Definition |
| --- | --- |
| `claim_id` | Stable handoff identifier |
| `surface` | Public product or section where the claim appears |
| `claim_type` | Headline, calculated share, decomposition, methodology boundary, benchmark, or publication-gate category |
| `public_copy` | Exact reviewer-facing statement approved by the generated handoff |
| `authority` | Canonical project table/file used to calculate or govern the claim |
| `source_locator` | Row/field/filter description for tracing the value inside the authority |
| `research_library_id` | Foreign key to the maintained Research Library source supporting the claim's data/methodology/benchmark role |
| `qa_gate` | Reconciliation or validation condition that must hold before publication |
| `release_disclosure` | Population, geography, release-vintage, interpretation, or uncertainty text that must accompany the claim |
| `publication_status` | `READY`, `READY WITH CONTEXT`, or `READY WITH CLAIM-LEVEL HOLDS` |

`scripts/build_publication_handoff.py` generates this register only after the state package, benchmark checks, population crosswalk, and QA-resolution layer are internally consistent. It also generates `docs/PUBLICATION_HANDOFF.md` and the reviewer-facing `site/publication-handoff.html` page.

## `data/public_release_register.csv`

One row per approved public artifact family. This register is the authority for files copied into `site/downloads/`.

| Field | Definition |
| --- | --- |
| `artifact_id` | Stable public-release identifier |
| `source_path` | Canonical project source path; one `*` wildcard is permitted for a governed file family such as state profiles |
| `public_path` | Intended path under `site/downloads/` |
| `data_class` | Aggregate analytic data, institution-level public data, QA/audit, publication, governance, or other release class |
| `unit_of_record` | Unit represented by one row/document/file |
| `person_level_data` | Must be `No` for the current PUBLIC register |
| `immigration_status_data` | Must be `No` for the current PUBLIC register |
| `release_basis` | Why the artifact is eligible for public release |
| `release_rule` | QA, interpretation, or handling condition required before release |
| `release_decision` | Must be `PUBLIC` for entries in this register |

`scripts/build_data_governance.py` validates the schema and handling flags, rejects raw-source paths, generates `docs/DATA_GOVERNANCE.md` and `site/data-governance.html`, copies the registered sources into the public tree, and rejects any unregistered file under `site/downloads/` or `site/data/`.

## `data/research_agenda.csv`

One row per maintained research or data-needs question.

| Field | Definition |
| --- | --- |
| `research_id` | Stable agenda identifier |
| `priority` | `High`, `Medium`, or `Low` |
| `question` | Research question stated for review/planning |
| `evidence_trigger` | Finding, QA observation, source limitation, or recurring product need motivating the question |
| `current_ipeds_fit` | Whether the current IPEDS pipeline can answer the question directly (`High`), cannot answer it (`None`), or can only support the workflow (`Support`) |
| `additional_data_needed` | Additional release, partner dataset, population-specific source, or contextual documentation required |
| `proposed_method` | Planned analytical approach |
| `proposed_output` | Intended research product |
| `decision_rule` | Evidence rule governing escalation/publication/interpretation |
| `status` | Current readiness or monitoring status |

`scripts/build_research_agenda.py` validates nonblank fields, unique IDs, and priority values before generating `docs/RESEARCH_AGENDA.md`.

## `data/population_crosswalk.csv`

One row per population/source concept governed by the project's comparability rules.

| Field | Definition |
| --- | --- |
| `population_id` | Stable project identifier for the population/source concept |
| `population_label` | Human-readable population label |
| `measure_type` | Administrative count, survey estimate, modeled estimate, or other measurement approach |
| `primary_source` | Organization/dataset that defines the current measure |
| `current_vintage` | Release or data vintage represented by the current source |
| `unit_of_analysis` | Unit represented by the measure |
| `inclusion_rule` | Population included by the source definition |
| `explicit_exclusions` | Important groups excluded or not separately identified |
| `geography` | Geographic meaning/coverage of the measure |
| `best_use` | Research question the measure is suited to answer |
| `comparison_warning` | Rule preventing an invalid direct comparison or substitution |
| `project_status` | How the current portfolio analysis uses the source |
| `source_url` | HTTPS methodology/research source |
| `last_checked` | ISO date of the recorded source review |

`scripts/build_population_crosswalk.py` validates exact concept coverage, unique IDs, nonblank metadata, HTTPS URLs, ISO dates, and the explicit IPEDS undocumented-student exclusion before generating `docs/POPULATION_CROSSWALK.md` and `site/methodology-crosswalk.html`.

## `data/recurring_report_register.csv`

One row per recurring research product represented in the target-role operations demonstration.

| Field | Definition |
| --- | --- |
| `report_id` | Stable project identifier for the recurring product |
| `report_title` | Public product name |
| `population_id` | Foreign key to `data/population_crosswalk.csv` |
| `research_library_id` | Foreign key to `data/research_library.csv` |
| `partner_context` | Publicly grounded partner context plus instruction to reconfirm roles at kickoff |
| `latest_publication_date` | ISO date of the current public product |
| `latest_data_vintage` | Current source/data vintage known from public methodology |
| `schedule_status` | Guarded scheduling rule that requires confirmation with the partner rather than inferred deadlines |
| `portfolio_stage` | Current state of this portfolio operations model |
| `monitoring_trigger` | Event that begins the next production-cycle review |
| `intake_requirements` | Versioned files and documentation required from the partner/source package |
| `method_change_check` | Definitions, assumptions, vintages, weights/models, or geography that must be compared with the prior product |
| `qa_gate` | Reproduction/reconciliation work required before publication |
| `publication_outputs` | Expected report/Portal/archive products after approval |
| `next_action` | Partner-confirmed kickoff action required before the next production cycle |
| `last_reviewed` | ISO date of the portfolio review |

`scripts/build_recurring_report_register.py` validates exact product coverage, foreign keys into both source authorities, ISO dates, nonblank fields, and schedule language before generating the human-readable operations register and public workflow page.

## `data/production_cycle_register.csv`

One row per shared production stage used by the recurring partner-research coordination model.

| Field | Definition |
| --- | --- |
| `stage_order` | Required sequence number from 1 through 7 |
| `stage_id` | Stable machine-readable stage identifier |
| `stage_label` | Reviewer-facing stage name |
| `coordination_role` | Generic role or role pairing responsible for coordinating the stage; never a claimed internal staff assignment |
| `entry_condition` | Evidence/state required before the stage begins |
| `required_record` | Record/package that must be created or preserved during the stage |
| `blocking_condition` | Condition that prevents advancement |
| `exit_condition` | Evidence required to complete the stage |
| `next_stage_id` | Required next stage, or `COMPLETE` after archival handoff |
| `retained_evidence` | Record carried into the next stage and next production cycle |

`scripts/build_production_cycle.py` validates exact seven-stage order and handoff continuity, verifies that the three recurring products retain partner-confirmed scheduling language, and generates `docs/PRODUCTION_CYCLE.md` plus `site/production-cycle.html`. The register is a portfolio coordination template, not an internal Presidents' Alliance schedule or approval chain.

## `data/production_cycle_log_template.csv`

Blank schema for a live recurring-report coordination log. The tracked file contains no operational records; a populated copy belongs in the approved working environment and is nonpublic by default.

| Field | Definition |
| --- | --- |
| `cycle_id` | Identifier for one confirmed production cycle |
| `report_id` | Foreign key to `data/recurring_report_register.csv` |
| `stage_id` | Foreign key to `data/production_cycle_register.csv` |
| `record_id` | Unique record identifier within a cycle |
| `record_type` | `stage_evidence`, `question`, `discrepancy`, `decision`, `approval`, or `archive` |
| `owner_role` | Responsible role; use the live organization's approved working record for any named contact |
| `opened_date` | ISO date the record was opened |
| `materiality` | `not_applicable`, `low`, `medium`, or `high` |
| `issue_or_question` | Coordination question, discrepancy, or issue being tracked |
| `evidence_requested` | Evidence or response needed to advance/resolve the record |
| `evidence_received` | Evidence actually received or reviewed |
| `decision` | Documented decision, especially for approval/hold records |
| `disclosure_requirement` | Publication/context disclosure created by the record, if any |
| `status` | `OPEN`, `BLOCKED`, `RESOLVED`, `APPROVED`, `HELD`, or `CLOSED` |
| `closed_date` | ISO date required for terminal statuses and prohibited for active statuses |
| `notes` | Additional handoff context |

`scripts/validate_production_cycle_log.py` enforces exact row shape, report/stage foreign keys, one report per cycle, controlled values, date ordering, unique record IDs within a cycle, discrepancy materiality, terminal/active closure rules, closure evidence, and decision text for closed discrepancies plus approval/hold records. The public template must remain empty.

## JSON products

`data/qa_report.json` contains structural checks, yearly source/flag distributions, row counts, and explicit exclusions.

`data/findings.json` contains the derived findings used by the public static site: headline metrics, level decomposition, state recovery, concentration, institutional control, institution-universe dynamics, rankings, and national series.

`data/latest_update_review.json` contains the latest annual national change, student-level decomposition, institution-universe accounting, largest state changes, priority counts, top review items, and imputation/status transitions used by the public release-review section.

`data/qa_resolution_summary.json` contains the reviewed sample size, counts by publication class and disposition, reviewed UNITIDs, latest manual review date, and three deterministic featured case studies. The featured cases represent an unresolved anomaly, a corroborated movement, and a documented structural change; each carries the current queue change, evidence URL, analyst note, and publication class used by the public brief and research memo. The summary is generated from `qa_resolution_log.csv` only after reconciliation to the current annual QA queue.

`data/state_profiles.json` contains the shareable state-profile payload used by `site/state.html`: coverage metadata plus 51 keyed profiles with latest metrics, change windows, top institutions, annual series, and corresponding Markdown filename. It is generated from `state_year.csv`, `state_change_summary.csv`, and the latest institution table rather than maintained independently.

## Publication manifest

`deliverables/research_brief_manifest.json` is the freshness record for the reviewer-facing PDF. It stores the source path (`site/research-memo.html`), source SHA-256, PDF SHA-256, PDF byte size, and expected three-page count. It is generated by `scripts/build_pdf_brief.py` and is validated against the current source and committed PDF before publication.

