# Data Governance and Public Release Controls

This portfolio project uses public administrative data and publishes only artifacts explicitly listed in `data/public_release_register.csv`. The current release contains no person-level records and no observed student immigration-status field.

**Registered artifact families:** 64
**Expanded public download files:** 114
**Current person-level public artifacts:** 0
**Current person-level immigration-status artifacts:** 0

## Release rules

1. Raw source archives are never placed in the public download tree.
2. Every public download must appear in the structured release register and be copied byte-for-byte from its canonical project source.
3. `site/downloads/` and `site/data/` are exact allowlisted trees; an unregistered file fails the build.
4. Institution-level IPEDS records are public entity data, not student records; QA flags are triage and are never represented as corrections or person-level findings.
5. If future partner work introduces person-level records, direct identifiers, or observed immigration-status data, those inputs are restricted by default and must not be added to this PUBLIC register. Only reviewed aggregate outputs may be considered for publication.

## Registered public artifacts

| ID | Public path | Class | Unit | Release basis |
| --- | --- | --- | --- | --- |
| PR01 | `site/downloads/national_year.csv` | Aggregate analytic data | National-year | Derived entirely from public IPEDS administrative data |
| PR02 | `site/downloads/state_year.csv` | Aggregate analytic data | State-year | Derived entirely from public IPEDS administrative data |
| PR03 | `site/downloads/state_change_summary.csv` | Aggregate analytic data | State | Derived entirely from public IPEDS administrative data |
| PR04 | `site/downloads/control_year.csv` | Aggregate analytic data | Institutional-control-year | Derived entirely from public IPEDS administrative data |
| PR05 | `site/downloads/institution_change_summary.csv` | Institution-level public data | Institution endpoint | Derived from public IPEDS institution records |
| PR06 | `site/downloads/latest_release_institution_review.csv` | QA / audit | Institution-year comparison | Derived from public IPEDS institution records |
| PR07 | `site/downloads/institutions_2024.csv` | Institution-level public data | Institution | Derived from public IPEDS institution records |
| PR08 | `site/downloads/schema_audit.csv` | QA / audit | Source year | Project-generated metadata over public source dictionaries |
| PR09 | `site/downloads/source_manifest.csv` | Source provenance | Source archive | Project-generated provenance for public NCES downloads |
| PR10 | `site/downloads/benchmark_audit.csv` | QA / audit | Metric-year | Project-generated comparison to a public NCES benchmark |
| PR11 | `site/downloads/nces_digest_2025_306_10.csv` | External benchmark | Metric-year | Compact transcription of a public NCES table used only for validation |
| PR12 | `site/downloads/latest_update_review.md` | Publication | Research update memo | Generated from validated public administrative data |
| PR13 | `site/downloads/qa_resolution_log.csv` | QA / audit | Institution review | Analyst review of public institution-level records and public evidence links |
| PR14 | `site/downloads/qa_resolution_log.md` | Publication | Institution review memo | Generated from the QA resolution register |
| PR15 | `site/downloads/research_library.csv` | Research governance | Source resource | Metadata describing public sources and research products |
| PR16 | `site/downloads/research_library.md` | Publication | Source guide | Generated from the structured Research Library |
| PR17 | `site/downloads/research_agenda.csv` | Research governance | Research question | Project planning metadata with no participant or respondent records |
| PR18 | `site/downloads/research_agenda.md` | Publication | Research agenda | Generated from the structured research agenda |
| PR19 | `site/downloads/publication_handoff.csv` | Research governance | Public claim/control | Generated from validated project outputs |
| PR20 | `site/downloads/publication_handoff.md` | Publication | Publication handoff memo | Generated from the structured publication handoff |
| PR21 | `site/downloads/population_crosswalk.csv` | Research governance | Population/source definition | Methodology metadata over public population definitions and sources |
| PR22 | `site/downloads/population_crosswalk.md` | Publication | Methodology crosswalk | Generated from the population/source crosswalk |
| PR23 | `site/downloads/recurring_report_register.csv` | Research governance | Recurring research product | Portfolio operations metadata grounded in public product information |
| PR24 | `site/downloads/recurring_report_register.md` | Publication | Recurring report operations memo | Generated from the recurring-report register |
| PR25 | `site/downloads/briefing_note.md` | Publication | Stakeholder briefing | Generated from validated aggregate findings and QA status |
| PR26 | `site/downloads/research_memo.md` | Publication | Research memo | Generated from validated aggregate findings and public institution evidence |
| PR27 | `site/downloads/ipeds_portfolio_analysis.xlsx` | Publication | Analysis workbook | Workbook built from public administrative data and validated project outputs |
| PR28 | `site/downloads/research_brief.pdf` | Publication | Research brief | PDF generated from the validated public research memo |
| PR29 | `site/downloads/state_profile_index.csv` | Aggregate analytic data | State | Derived entirely from public IPEDS administrative data |
| PR30 | `site/downloads/state_profiles/*.md` | State publication | State profile | Generated from public state and institution-level IPEDS outputs |
| PR31 | `site/downloads/public_release_register.csv` | Research governance | Public artifact control | Project release-control metadata |
| PR32 | `site/downloads/data_governance.md` | Publication | Data governance note | Generated from the public release register and project handling rules |
| PR33 | `site/downloads/production_cycle_register.csv` | Research governance | Production stage control | Portfolio coordination metadata with no partner-confidential or person-level records |
| PR34 | `site/downloads/production_cycle.md` | Publication | Production-cycle coordination note | Generated from the stage register and public recurring-product operations metadata |
| PR35 | `site/downloads/production_cycle_log_template.csv` | Research governance | Blank live-cycle coordination log template | Empty portfolio template containing field names only |
| PR36 | `site/downloads/portfolio_queries.sql` | Analysis code | SQL query pack | Read-only SQL over validated public aggregate and institution-level outputs |
| PR37 | `site/downloads/sql_analysis_audit.csv` | QA / audit | SQL query | Generated reconciliation metadata comparing SQL results with canonical CSV outputs |
| PR38 | `site/downloads/sql_analysis.md` | Publication | SQL analysis note | Generated from the public read-only query pack and validated SQL audit |
| PR39 | `site/downloads/management_briefing_deck.pptx` | Publication | Management briefing deck | PowerPoint generated from validated aggregate findings and QA outputs |
| PR40 | `site/downloads/ad_hoc_analysis_results.csv` | Analysis output | Ad hoc analysis case results | Generated aggregate answers for three explicitly simulated management questions |
| PR41 | `site/downloads/ad_hoc_analysis.md` | Publication | Ad hoc analysis casebook | Generated from validated aggregate outputs with no real requester or SLA metadata |
| PR42 | `site/downloads/planning_scenarios.csv` | Analysis output | Planning scenario and variance table | Generated national-level backtest and forward planning scenarios from validated historical aggregates |
| PR43 | `site/downloads/planning_scenarios.md` | Publication | Planning scenarios note | Generated from the validated national series with transparent historical growth assumptions |
| PR44 | `site/downloads/release_monitor_snapshot.json` | Monitoring evidence | NCES release-availability snapshot | Dated public HTTP availability observations for the four next-year IPEDS package assets |
| PR45 | `site/downloads/freshness_monitor.csv` | Monitoring / operations | Release and source monitoring register | Generated from the captured NCES release snapshot plus maintained public source-review and recurring-product metadata |
| PR46 | `site/downloads/freshness_monitor.md` | Publication | Release and freshness monitoring note | Generated from the validated monitoring register and dated NCES release snapshot |
| PR47 | `site/downloads/state_recovery_analysis.csv` | Analysis output | State recovery decomposition | Generated from validated public state and institution-level IPEDS outputs |
| PR48 | `site/downloads/state_recovery_analysis.md` | Publication | State recovery analysis note | Generated from the validated state recovery decomposition |
| PR49 | `site/downloads/private_nonprofit_growth.csv` | Analysis output | Private nonprofit institution contribution | Generated from validated public control and institution-level IPEDS outputs plus the current institution QA gate |
| PR50 | `site/downloads/private_nonprofit_growth.md` | Publication | Private nonprofit growth concentration note | Generated from the validated private-nonprofit institution contribution analysis |
| PR51 | `site/downloads/population_trend_comparison.csv` | Analysis output | Population-year aggregate comparison row | Generated from the canonical IPEDS national series plus curated public aggregate reference observations for immigrant-origin and undocumented students |
| PR52 | `site/downloads/population_trend_comparison.md` | Publication | Bounded national population trend comparison note | Generated from validated separate population series with explicit definition and vintage boundaries |
| PR53 | `site/downloads/source_update_triage.csv` | Research governance | Maintained source routing record | Portfolio source-monitoring metadata joined one-for-one to the public Research Library |
| PR54 | `site/downloads/source_update_triage.md` | Publication | Source-update routing note | Generated from the validated source-update triage register and Research Library |
| PR55 | `site/downloads/undocumented_pipeline_comparison.csv` | Analysis output | Undocumented 2023 state pipeline context | Generated from curated public same-year aggregate reference values and validated Research Library authorities |
| PR56 | `site/downloads/undocumented_pipeline_context.md` | Publication | Undocumented pipeline context note | Generated from the validated 2023 ecological state comparison |
| PR57 | `site/downloads/release_readiness.csv` | Research governance | Release-control gate | Generated from validated analytical QA benchmark institution-review handoff governance artifact-freshness source-routing and release-monitor authorities |
| PR58 | `site/downloads/release_readiness.md` | Publication | Release-readiness control note | Generated from the consolidated release-readiness matrix |
| PR59 | `site/downloads/undergraduate_shift_baseline.csv` | Analysis output | R01 undergraduate-shift state baseline | Generated from validated public national state control and institution-level IPEDS outputs |
| PR60 | `site/downloads/undergraduate_shift_baseline.md` | Publication | R01 undergraduate-shift baseline note | Generated from the validated fixed 2023-2024 undergraduate-shift baseline |
| PR61 | `site/downloads/candidate_directory_preflight.json` | Monitoring evidence | Candidate directory structural snapshot | Dated structural review of the available public candidate-year IPEDS directory and dictionary |
| PR62 | `site/downloads/candidate_directory_preflight.md` | Publication | Candidate directory preflight note | Generated from the validated candidate directory structural snapshot |
| PR63 | `site/downloads/candidate_directory_change_review.csv` | Monitoring evidence | Candidate directory institution-change review row | Generated from the public candidate-year directory compared with the current public directory and canonical current-year institution analysis |
| PR64 | `site/downloads/candidate_directory_change_review.md` | Publication | Candidate directory institution-change review note | Generated from the hashed candidate directory change-review CSV and validated preflight snapshot |

## Handling boundary

This register governs the portfolio's public release tree. It is not a claim about the Presidents' Alliance's internal systems, partner agreements, or data-retention policies. Any real partner dataset would require its own authorization, access, retention, disclosure, and destruction rules before analysis begins.