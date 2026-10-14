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

One row per institution in the current high-priority annual QA queue. This is an analyst-decision record, not a corrected-data table.

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

The build script requires the log to cover every current high-priority UNITID in the same deterministic queue order and rejects extra or missing records. A new annual release therefore forces stale dispositions to be revisited rather than silently carrying them forward.

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

## `data/sql_analysis_audit.csv`

One row per query executed from `sql/portfolio_queries.sql` against the transient SQLite analysis layer.

| Field | Definition |
| --- | --- |
| `query_id` | Stable ordered query identifier (`Q01`-`Q06`) |
| `title` | Reviewer-facing purpose of the query |
| `skills` | SQL constructs demonstrated by the query |
| `row_count` | Number of rows returned by the SQL query |
| `check_name` | Independent reconciliation condition applied to the query result |
| `expected_value` | Value calculated directly from canonical processed CSVs |
| `observed_value` | Value produced by the SQL query result |
| `status` | `PASS` only when expected and observed values are identical |
| `notes` | Short explanation of the reconciliation |

`scripts/build_sql_analysis.py` creates an in-memory SQLite database from the national, state, control, latest-institution, and institution-change CSV outputs, executes exactly six SELECT/WITH queries, rejects SQL mutation/DDL/attachment/PRAGMA statements, writes this audit, and generates `docs/SQL_ANALYSIS.md` plus `site/sql-analysis.html`. The SQLite database is ephemeral and is never an analytical authority or public artifact.

## `data/ad_hoc_analysis_results.csv`

One row per explicitly simulated ad hoc management question.

| Field | Definition |
| --- | --- |
| `case_id` | Stable ordered case identifier (`A01`-`A03`) |
| `business_question` | Constructed management question used to demonstrate bounded analysis |
| `decision_use` | Generic explanation of how the answer could guide follow-up analysis or communication; not a claim about a real stakeholder |
| `primary_answer` | Concise answer produced from validated analytical outputs |
| `response_detail` | Small amount of supporting context needed to interpret the answer |
| `source_authority` | Canonical processed CSV path(s) used for the calculation |
| `qa_check` | Reconciliation or accounting identity used to validate the result |
| `status` | `PASS` only when the case calculation and required reconciliation succeed |

`scripts/build_ad_hoc_analysis.py` regenerates all three cases from the validated state, control, and national outputs and writes the CSV, `docs/AD_HOC_ANALYSIS.md`, and `site/ad-hoc-analysis.html`. The generated products must retain the explicit portfolio-simulation boundary and must not introduce real or invented requester identities, deadlines, SLAs, or employment-history claims.

## `data/state_recovery_analysis.csv`

One row per state/DC explaining the 2019-2024 recovery result with three exact decompositions plus an institution-concentration measure.

| Field | Definition |
| --- | --- |
| `state` / `state_name` | State/DC code and display name |
| `recovery_status` | Existing state-summary classification: `At or above 2019` or `Below 2019` |
| `nonresident_2019` / `nonresident_2024` | Baseline and endpoint U.S. nonresident enrollment |
| `change_2019_2024` | 2024 minus 2019 U.S. nonresident enrollment |
| `undergraduate_change` / `graduate_change` | Student-level components that must sum exactly to the state net change |
| `level_driver` | Undergraduate- or graduate-led label for the component aligned most strongly with the state's net direction |
| `public_change` / `private_nonprofit_change` / `private_forprofit_change` | Endpoint change by institutional control; the three components must sum exactly to the state net change |
| `control_driver` | Institutional-control component aligned most strongly with the state's net direction |
| `continuing_change` | Net change among UNITIDs present in the state's analytic universe in both endpoint years |
| `entered_enrollment` | 2024 enrollment at UNITIDs not present in that state's 2019 analytic universe |
| `exited_enrollment` | 2019 enrollment at UNITIDs not present in that state's 2024 analytic universe |
| `institution_accounting_net` | `continuing_change + entered_enrollment - exited_enrollment`; must equal the state net change |
| `directional_movement` | Gross absolute institution movement aligned with the state's net direction |
| `offsetting_movement` | Gross absolute institution movement opposite the state's net direction |
| `top3_directional_contribution` / `top3_directional_share_pct` | Contribution and share of aligned gross movement from the three largest institution contributors |
| `top1_institution` / `top1_contribution` | Largest institution contributor in the state's net direction |
| `top3_institutions` | Reviewer-readable names and changes for the three largest directional contributors |

`scripts/build_state_recovery_analysis.py` derives the table from `state_year.csv`, `state_change_summary.csv`, and `institution_year.csv`, rejects any student-level, institutional-control, or institution-continuity decomposition that does not reconcile, and generates `docs/STATE_RECOVERY_ANALYSIS.md` plus `site/state-recovery.html`. The decomposition is accounting rather than causal analysis; institution entry/exit must not be interpreted automatically as campus opening/closure, and endpoint control changes can include institutions changing control category.

## `data/private_nonprofit_growth.csv`

One row per UNITID present in the private-nonprofit analytic universe in 2015 or 2024. The table attributes the sector endpoint change to institutions, separates undergraduate and graduate contributions, measures positive-contribution concentration, and carries the current latest-release QA gate for institution-specific interpretation.

| Field | Definition |
| --- | --- |
| `unitid` / `institution` | Public IPEDS institution identifier and display name |
| `state_2015` / `state_2024` | Endpoint institution location; blank when the UNITID is absent from that endpoint private-nonprofit universe |
| `endpoint_status` | Present as private nonprofit in both endpoints, entered the endpoint universe, or left it |
| `nonresident_2015` / `nonresident_2024` | Endpoint U.S. nonresident enrollment, using zero when the UNITID is absent from that private-nonprofit endpoint |
| `change_2015_2024` | 2024 minus 2015 endpoint contribution |
| `undergraduate_change` / `graduate_change` | Student-level contribution components that must sum to the institution endpoint change |
| `latest_release_review_priority` | Current 2023-2024 automated review priority for the UNITID, or `not_in_latest_endpoint` when no current row exists |
| `latest_release_publication_class` | Analyst publication class from the current QA resolution log when reviewed |
| `narrative_gate` | Institution-specific publication gate inherited from the latest-release QA layer; aggregate inclusion does not clear a held institution-specific claim |
| `positive_rank` | Rank among institutions with positive endpoint contributions; blank for zero/negative contributions |
| `share_of_gross_positive_pct` | Institution positive contribution divided by all positive private-nonprofit endpoint movement |
| `cumulative_positive_share_pct` | Cumulative share of gross positive movement in positive-rank order |
| `concentration_group` | Top 10, positive ranks 11-25, other positive contributors, or nonpositive contribution |

`scripts/build_private_nonprofit_analysis.py` reconciles the 2015 and 2024 institution totals to `control_year.csv`, requires undergraduate plus graduate contributions to match every institution endpoint change, requires gross positive movement minus gross negative movement to match the +82,825 sector net change, and generates `docs/PRIVATE_NONPROFIT_GROWTH.md` plus `site/private-nonprofit-growth.html`. The public decision rule labels the shift concentrated only when the top 10 institutions account for at least 50% of gross positive movement; that threshold is an explicit project rule rather than a universal statistical standard. Endpoint entry/exit can reflect control-category or analytic-universe changes and must not be interpreted automatically as campus opening/closure.

## `data/population_trend_reference.csv`

Six curated public aggregate observations used to bound the R04 comparison: two immigrant-origin observations (2000/2023), two historical undocumented-student observations (2019/2021), and two current undocumented-student observations (2023/2024). This file is a provenance-controlled analytical input, not a person-level dataset and not a merged population series.

Key fields include `reference_id`, `population_id`, `observation_year`, `estimate`, `share_pct`, `source_vintage`, `trend_segment`, `reported_change_pct`, `research_library_id`, `source_url`, and `comparison_note`. The `trend_segment` field is a hard arithmetic boundary: the historical and current undocumented estimates are deliberately assigned to different segments so the build cannot calculate an unsupported 2021-2023 trend.

## `data/population_trend_comparison.csv`

Twelve generated population-year rows combining the six canonical IPEDS national observations for 2019-2024 with the six curated external aggregate observations above. The file preserves each population's measurement system and source vintage instead of normalizing unlike populations into a single total.

| Field | Definition |
| --- | --- |
| `population_id` / `population_label` | Population concept and display label |
| `observation_year` / `estimate` | Published or canonical national observation |
| `share_pct` | Published population share where available; IPEDS share is recalculated from the canonical national series |
| `measurement` / `source_vintage` | Measurement system and exact source period used for the observation |
| `trend_segment` | Method-compatible segment within which change may be calculated |
| `segment_start_year` / `segment_start_value` | First observation in that compatible segment |
| `within_segment_change` / `within_segment_change_pct` | Arithmetic change from the segment start; never calculated across different segments |
| `reported_change_pct` | Source-reported percentage when the published rounded counts do not reproduce it exactly |
| `research_library_id` / `source_url` | Maintained source foreign key and public provenance URL |
| `comparison_class` | Primary IPEDS series or contextual companion series |
| `comparison_note` | Interpretation boundary retained with the row |

`scripts/build_population_trends.py` validates all external observations and Research Library foreign keys, derives IPEDS rows directly from `national_year.csv`, requires separate undocumented 2019-2021 and 2023-2024 segments, and generates `docs/POPULATION_TREND_COMPARISON.md` plus `site/population-trends.html`. Cross-population counts are contextual only and must not be added, subtracted, or treated as mutually exclusive components.

## `data/undocumented_pipeline_reference.csv`

Eleven curated public 2023 aggregate observations used by R06: one national denominator row and ten states with explicit values in both the undocumented high-school-graduate and undocumented higher-education source surfaces. The reference is fixed-vintage provenance, not person-level data. High-school values are annual graduate flows; higher-education values are enrollment stocks.

Key fields include `geography_id`, `coverage_class`, both 2023 estimates, Research Library foreign keys for each measure, exact reviewed source URLs, and a source note. The build requires the two URLs to match their current Research Library authorities and preserves the living Portal state table as captured 2023 evidence rather than allowing a later page update to silently rewrite the comparison.

## `data/undocumented_pipeline_comparison.csv`

Ten generated state rows derived from the fixed R06 reference.

| Field | Definition |
| --- | --- |
| `state` / `state_name` | State code and display name for the overlapping 2023 comparison set |
| `high_school_graduates_annual_2023` | Published rounded annual undocumented high-school graduate flow |
| `higher_ed_enrollment_2023` | Published undocumented higher-education enrollment stock |
| `hs_national_share_pct` / `higher_ed_national_share_pct` | Each state value divided by its separate national denominator: 75,000 annual graduates or 510,000 enrolled students |
| `share_gap_pp` | Higher-education national share minus high-school national share; a geography comparison, not a transition measure |
| `stock_flow_scale_multiple` | Enrollment stock divided by annual graduate flow, retained only as a descriptive scale ratio and explicitly not a rate |
| `hs_rank` | Rank among the ten states by annual high-school graduate estimate, using minimum rank for rounded ties |
| `higher_ed_rank_within_overlap` | Rank among the same ten states by higher-education enrollment |
| `rank_gap` | Higher-education rank minus high-school rank within the bounded comparison set |
| `hs_research_library_id` / `he_research_library_id` | Source authorities for each measure |
| `interpretation_gate` | Row-level reminder that the ecological stock/flow multiple is not a transition rate |

`scripts/build_undocumented_pipeline.py` requires exact 2023 national and state reference values, reconciles the ten-state totals to 53,000 annual graduates and 358,836 higher-education students, validates the 70.7% / 70.4% concentration result, and generates `docs/UNDOCUMENTED_PIPELINE_CONTEXT.md` plus `site/undocumented-pipeline.html`. It does not calculate individual college-going, persistence, completion, or causal policy effects.

## `data/source_update_triage.csv`

One row per maintained Research Library resource. The register implements R07 by classifying the expected next source change while preserving explicit escalation conditions.

| Field | Definition |
| --- | --- |
| `resource_id` | Foreign key to the complete maintained `data/research_library.csv` source set |
| `baseline_route` | Expected first route for the source as currently used: `ROUTINE_REFRESH`, `METHODOLOGY_REVIEW`, `RESEARCH_QUESTION_REVIEW`, `GOVERNANCE_REVIEW`, `MONITOR_ONLY`, or `ARCHIVAL_REFERENCE` |
| `baseline_trigger` | Expected event that starts the baseline route |
| `methodology_escalation` | Definition, denominator, model, schema, geography, timing, or related condition that stops routine use pending methodology review |
| `research_question_escalation` | Coverage or same-method conclusion change that justifies opening or reprioritizing an explicit research question |
| `affected_surface` | Portfolio products or controls that must be reviewed when the source changes |
| `review_boundary` | Source-specific limit that prevents a new date/file from becoming an automatic analytical conclusion |

`scripts/build_source_update_triage.py` requires exact one-for-one coverage of the Research Library, validates the controlled routes, requires R07 to remain linked to the implemented product, and generates `docs/SOURCE_UPDATE_TRIAGE.md` plus `site/source-update-triage.html`. The routing model does not infer internal partner schedules or approval processes.

## `data/undergraduate_shift_baseline.csv`

One fixed 2023-2024 R01 baseline row per state/DC. The product is intentionally anchored to those years even after the project later advances, so the next complete Fall Enrollment release can be compared against a pre-specified baseline.

| Field | Definition |
| --- | --- |
| `state` / `state_name` | Two-letter geography code and readable state/DC name |
| `undergraduate_2023` / `undergraduate_2024` | Endpoint undergraduate U.S. nonresident enrollment used by the fixed baseline |
| `undergraduate_change` | 2024 minus 2023 undergraduate enrollment |
| `graduate_change` | 2024 minus 2023 graduate enrollment |
| `total_change` | 2024 minus 2023 total U.S. nonresident enrollment; must equal undergraduate plus graduate change |
| `undergraduate_direction` | `Increase`, `Decline`, or `Flat` based on `undergraduate_change` |
| `public_undergraduate_change` | Undergraduate change at public institutions in the state, using endpoint control classification |
| `private_nonprofit_undergraduate_change` | Undergraduate change at private nonprofit institutions |
| `private_forprofit_undergraduate_change` | Undergraduate change at private for-profit institutions |
| `continuing_undergraduate_change` | Undergraduate change among UNITIDs present in the state's analytic universe in both 2023 and 2024 |
| `entered_undergraduate_enrollment` | 2024 undergraduate enrollment at UNITIDs entering the state's endpoint analytic universe |
| `exited_undergraduate_enrollment` | 2023 undergraduate enrollment at UNITIDs exiting the state's endpoint analytic universe; subtracted in the accounting identity |
| `undergraduate_accounting_net` | `continuing + entered - exited`; must equal `undergraduate_change` |
| `directional_institution_movement` | Gross institution movement in the state's undergraduate net direction |
| `offsetting_institution_movement` | Gross institution movement opposite the state's undergraduate net direction |
| `top3_directional_contribution` | Sum of the three largest institution contributions aligned with the state's net undergraduate direction |
| `top3_directional_share_pct` | Top-three directional contribution divided by gross directional institution movement |
| `positive_state_rank` | Rank among states/DC with positive undergraduate change; blank for nonpositive states |
| `share_of_gross_positive_state_pct` | Positive state's contribution to gross positive state undergraduate movement |
| `cumulative_positive_state_share_pct` | Cumulative gross-positive state share through that positive-state rank |

`scripts/build_undergraduate_shift_baseline.py` validates all 51 geographies, reconciles student level, institutional control, and institution-continuity accounting independently, fixes the 2015-2024 annual comparison history, and generates `docs/UNDERGRADUATE_SHIFT_BASELINE.md` plus `site/undergraduate-shift.html`. The output is a persistence baseline rather than evidence that the shift persisted. The next complete Fall Enrollment release must pass schema review before R01 can be classified under the pre-specified national-direction and majority-of-states rule.

## `data/planning_scenarios.csv`

One backtest row plus three forward planning-scenario rows generated from the validated national series.

| Field | Definition |
| --- | --- |
| `case_id` | Stable identifier (`BT01`, `PS01`-`PS03`) |
| `case_type` | `BACKTEST` or `PLANNING_SCENARIO` |
| `case_label` | Reviewer-facing scenario name |
| `basis_period` | Historical years used to derive the annual rate |
| `method` | Plain-language description of the growth-rate calculation |
| `annual_rate_pct` | Annualized historical rate used by the case |
| `base_year` / `base_value` | Historical actual from which the planned value is calculated |
| `target_year` | Year represented by the planned value |
| `planned_value` | Baseline/scenario value calculated from the stated assumption |
| `actual_value` | Known actual for the backtest; blank for future planning scenarios |
| `variance` / `variance_pct` | Actual minus planned value for the backtest; blank for future scenarios |
| `decision_use` | Generic management-planning purpose, not a claim about a real stakeholder |
| `status` | `PASS` when ordering and reconciliation checks succeed |

`scripts/build_planning_scenarios.py` writes the CSV, `docs/PLANNING_SCENARIOS.md`, and `site/planning-scenarios.html`. The national historical CSV remains authoritative. Forward scenario rows must not be described as observed values or as a predictive model.

## `data/freshness_monitor.csv`

One row per release/freshness monitoring control generated from the captured release snapshot and maintained source-review/recurring-product metadata.

| Field | Definition |
| --- | --- |
| `monitor_id` | Stable ordered monitoring identifier (`R01`-`R04`, `D01`, `G01`, `S01`-`S02`, `P01`-`P03`) |
| `monitor_area` | NCES release package, candidate directory preflight, annual release gate, source review, or recurring product |
| `subject` | File, source-control surface, or recurring product being monitored |
| `observed_date` | Date of the captured availability check or maintained human review |
| `status` | Availability, gate, review-recorded, or monitor-trigger state |
| `evidence` | Current observation retained for the monitoring decision |
| `trigger` | Condition that requires the next review/action |
| `next_action` | Bounded action to take when interpreting the current state |
| `authority` | Source URL or project authority supporting the row |

`scripts/build_freshness_monitor.py` validates `data/release_monitor_snapshot.json`, requires exactly four candidate-year files, validates the captured candidate-directory preflight, derives package readiness from those observations, rejects mismatched decisions, and generates the CSV plus `docs/FRESHNESS_MONITOR.md` and `site/freshness-monitor.html`. `D01` records directory-side readiness without converting the partial package into a year-advance decision. Recurring-product rows preserve event triggers rather than inferring internal deadlines.

## `data/candidate_directory_preflight.json`

Dated structural evidence generated by the separate online `scripts/check_candidate_directory.py` lane when the candidate-year institutional directory and dictionary are available before Fall Enrollment. It is not part of the canonical analytical source manifest and cannot authorize year advancement.

Key blocks record the candidate archive URLs/bytes/SHA-256 hashes and member names, required directory fields and dictionary titles, full data/dictionary field-set parity, directory row/field/state/duplicate counts, directory-side eligible institution/control counts, the current-year directory reference, schema additions/removals, eligible-UNITID continuity, a SHA-256-bound institution-level change-review summary, and the exact release-monitor snapshot/decision against which the preflight was captured. `year_advance_authorized` must remain `false`. `directory-eligible` means only that the current geography plus `DEGGRANT`/`PSET4FLG` filters pass; final analytic-universe membership still requires the candidate Fall Enrollment join and row-level checks.

## `data/candidate_directory_change_review.csv`

One row per UNITID affected by candidate-directory eligible-frame turnover or by a name/state/control/eligible-Title-IV attribute change while remaining directory-eligible. The online checker writes this CSV in deterministic class/UNITID order and stores its SHA-256 in `data/candidate_directory_preflight.json`; the offline builder fails if the file and captured hash diverge.

| Field | Definition |
| --- | --- |
| `unitid` | IPEDS institution identifier used as the continuity key |
| `change_class` | `LEFT_DIRECTORY_ELIGIBLE`, `ENTERED_DIRECTORY_ELIGIBLE`, or `SHARED_ATTRIBUTE_CHANGE` |
| `change_reasons` | Semicolon-delimited structural reason codes for frame entry/exit or shared attribute change |
| `current_directory_present` / `candidate_directory_present` | Whether the UNITID exists in the full current/candidate directory file |
| `current_directory_eligible` / `candidate_directory_eligible` | Whether the UNITID passes the directory-side geography, degree-granting, and Title-IV/First-Look filters |
| `current_institution` / `candidate_institution` | Current/candidate institution name strings; UNITID remains the continuity authority |
| `current_state` / `candidate_state` | Current/candidate state abbreviation |
| `current_control_code` / `candidate_control_code` | Raw IPEDS control code at each directory vintage |
| `current_control` / `candidate_control` | Public/private nonprofit/private for-profit labels corresponding to the control codes |
| `current_deggrant` / `candidate_deggrant` | Degree-granting status values used in directory eligibility |
| `current_pset4flg` / `candidate_pset4flg` | Postsecondary/Title-IV indicator values used in directory eligibility |
| `name_changed` / `state_changed` / `control_changed` | Explicit Yes/No comparison flags when both directory records exist |
| `current_analysis_present` | Whether the UNITID is present in the canonical current-year institution analysis |
| `current_nonresident_enrollment` | Current-year U.S. nonresident enrollment copied from the canonical analysis when present; never a candidate-year estimate |
| `current_total_enrollment` | Current-year total enrollment copied from the canonical analysis when present; never a candidate-year estimate |
| `analytical_review_scope` | Semicolon-delimited future QA domains such as universe, control, state, and label continuity |
| `interpretation_boundary` | Fixed prohibition on inferring institutional opening/closure or candidate-year enrollment movement from directory structure alone |

`scripts/build_candidate_directory_change_review.py` validates the captured hash, row semantics, deterministic ordering, current-year exposure fields against `data/processed/institutions_2024.csv`, and all preflight reconciliation counts before generating `docs/CANDIDATE_DIRECTORY_CHANGE_REVIEW.md` and `site/candidate-directory-changes.html`.

## `data/release_readiness.csv`

Eight generated release-control rows that consolidate the project's independent analytical, publication, governance, artifact-freshness, source-routing, and candidate-year gates while keeping current-publication readiness separate from permission to advance the analysis year.

| Field | Definition |
| --- | --- |
| `gate_id` | Stable ordered control identifier (`A01`-`A07`, `Y01`) |
| `gate_scope` | Decision surface governed by the row: current release or year advance |
| `gate_name` | Human-readable control name |
| `status` | Controlled result: `PASS`, `PASS_WITH_CLAIM_HOLDS`, or `HOLD` |
| `blocks_current_release` | Whether a `HOLD` on this control prevents publication of the current validated release |
| `blocks_year_advance` | Whether a `HOLD` on this control prevents changing the configured analysis year |
| `evidence` | Reconciled current evidence supporting the control result |
| `authority` | Canonical project file or manifest used by the control |
| `next_action` | Bounded action required if the evidence changes or the gate remains held |

`scripts/build_release_readiness.py` requires all core analytical and benchmark checks to pass, complete current high-priority institution-review coverage, the full 15-row publication handoff, one-for-one Research Library routing, valid public-release registration, current PDF/PowerPoint freshness manifests, and a release snapshot that reconciles to the four candidate-year file observations. The current-release summary may be `READY_WITH_CLAIM_LEVEL_HOLDS` while institution-specific explanations remain gated; the independent year-advance summary remains `HOLD_YEAR_ADVANCE` until the complete candidate package is available and schema review can begin. The builder generates `docs/RELEASE_READINESS.md` and `site/release-readiness.html`.

## JSON products

`data/release_monitor_snapshot.json` is a dated online observation rather than an offline analytical input. It records the current/candidate years, UTC check time, Fall Enrollment and directory readiness, complete-package readiness, release decision, and the four candidate-file HTTP observations. It is written only when `scripts/check_for_new_release.py --write-snapshot ...` is run explicitly; normal offline validation consumes but does not refresh it.

`data/qa_report.json` contains structural checks, yearly source/flag distributions, row counts, and explicit exclusions.

`data/findings.json` contains the derived findings used by the public static site: headline metrics, level decomposition, state recovery, concentration, institutional control, institution-universe dynamics, rankings, and national series.

`data/latest_update_review.json` contains the latest annual national change, student-level decomposition, institution-universe accounting, largest state changes, priority counts, top review items, and imputation/status transitions used by the public release-review section.

`data/qa_resolution_summary.json` contains the full high-priority queue size, review coverage percentage, counts by publication class and disposition, reviewed UNITIDs, latest manual review date, and three deterministic featured case studies. The featured cases represent an unresolved anomaly, a corroborated movement, and a documented structural change; each carries the current queue change, evidence URL, analyst note, and publication class used by the public brief and research memo. The summary is generated from `qa_resolution_log.csv` only after every current high-priority queue record has a reconciled disposition.

`data/state_profiles.json` contains the shareable state-profile payload used by `site/state.html`: coverage metadata plus 51 keyed profiles with latest metrics, change windows, top institutions, annual series, and corresponding Markdown filename. It is generated from `state_year.csv`, `state_change_summary.csv`, and the latest institution table rather than maintained independently.

## Publication manifests

`deliverables/research_brief_manifest.json` is the freshness record for the reviewer-facing PDF. It stores the source path (`site/research-memo.html`), source SHA-256, PDF SHA-256, PDF byte size, and expected three-page count. It is generated by `scripts/build_pdf_brief.py` and is validated against the current source and committed PDF before publication.

`deliverables/management_briefing_manifest.json` is the freshness record for the reviewer-facing PowerPoint deck. It stores the deck-builder path and SHA-256, SHA-256 hashes for every validated CSV/JSON source used by the presentation, the PPTX SHA-256 and byte size, the exact six-slide count, and a compact set of key metrics used by repository tests. It is generated by `scripts/build_management_deck.py`; validation fails when the tracked deck or manifest no longer matches the current builder or analytical sources.

