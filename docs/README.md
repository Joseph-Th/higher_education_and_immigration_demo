# Documentation Index

**Document role:** Navigation for every maintained document under `docs/`. Each page owns one
question; the root [README](../README.md) routes the short review path and the live publication.

## Method and data authorities

| Document | Owns |
| --- | --- |
| [METHODOLOGY.md](METHODOLOGY.md) | Analytical definitions, coverage, and interpretation boundaries. |
| [POPULATION_CROSSWALK.md](POPULATION_CROSSWALK.md) | Which population measures are and are not interchangeable. |
| [DATA_SOURCES.md](DATA_SOURCES.md) | Official source files, retrieval, and lineage. |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Field definitions and normalized schema. |
| [DATA_CALENDAR.md](DATA_CALENDAR.md) | Release timing and which vintage is current. |
| [DATA_GOVERNANCE.md](DATA_GOVERNANCE.md) | Public-release allowlist and data minimization. |
| [VARIABLE_MAPPING.md](VARIABLE_MAPPING.md) | Source-to-analysis variable mapping. |
| [PRODUCTION_CYCLE.md](PRODUCTION_CYCLE.md) | How validated outputs are rebuilt and published. |
| [UPDATE_PLAYBOOK.md](UPDATE_PLAYBOOK.md) | Annual source update and candidate-year procedure. |
| [SOURCE_UPDATE_TRIAGE.md](SOURCE_UPDATE_TRIAGE.md) | How a new source package is assessed before adoption. |
| [FRESHNESS_MONITOR.md](FRESHNESS_MONITOR.md) | Freshness signals and stale-source routing. |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Publication deployment steps. |
| [VALIDATION.md](VALIDATION.md) | Verification contract and evidence limits. |
| [STATE_RECOVERY_ANALYSIS.md](STATE_RECOVERY_ANALYSIS.md) | Recovery analysis for state-level series disruptions. |
| [UNDOCUMENTED_PIPELINE_CONTEXT.md](UNDOCUMENTED_PIPELINE_CONTEXT.md) | Pipeline context that is not obvious from scripts. |

## Findings and research

| Document | Owns |
| --- | --- |
| [FINDINGS.md](FINDINGS.md) | Current analytical findings and exact supporting figures. |
| [RESEARCH_MEMO.md](RESEARCH_MEMO.md) | Public research memo. |
| [RESEARCH_LIBRARY.md](RESEARCH_LIBRARY.md) | Source library and reading list. |
| [RESEARCH_AGENDA.md](RESEARCH_AGENDA.md) | Open research questions. |
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Project brief and reviewable scope. |
| [BRIEFING_NOTE.md](BRIEFING_NOTE.md) | Leadership briefing note. |
| [PLANNING_SCENARIOS.md](PLANNING_SCENARIOS.md) | Bounded planning interpretations. |
| [POPULATION_TREND_COMPARISON.md](POPULATION_TREND_COMPARISON.md) | Separate population series shown only for scale context. |
| [PRIVATE_NONPROFIT_GROWTH.md](PRIVATE_NONPROFIT_GROWTH.md) | Private nonprofit enrollment context. |
| [UNDERGRADUATE_SHIFT_BASELINE.md](UNDERGRADUATE_SHIFT_BASELINE.md) | Undergraduate mix baseline. |
| [AD_HOC_ANALYSIS.md](AD_HOC_ANALYSIS.md) | Simulated bounded analyst requests and responses. |

## QA and release judgment

| Document | Owns |
| --- | --- |
| [QA_RESOLUTION_LOG.md](QA_RESOLUTION_LOG.md) | High-priority institution QA decisions. |
| [MEDIUM_QA_RESOLUTION_LOG.md](MEDIUM_QA_RESOLUTION_LOG.md) | Medium-priority institution QA decisions. |
| [MEDIUM_PRIORITY_REVIEW.md](MEDIUM_PRIORITY_REVIEW.md) | Reason-coded routing of the medium-priority queue. |
| [MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md](MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md) | Category countermovement check for medium-priority rows. |
| [HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md](HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md) | Category countermovement check for high-priority rows. |
| [CANDIDATE_DIRECTORY_PREFLIGHT.md](CANDIDATE_DIRECTORY_PREFLIGHT.md) | Candidate-year directory preflight. |
| [CANDIDATE_DIRECTORY_CHANGE_REVIEW.md](CANDIDATE_DIRECTORY_CHANGE_REVIEW.md) | Candidate-year directory change review. |
| [CANDIDATE_YEAR_QA_WATCHLIST.md](CANDIDATE_YEAR_QA_WATCHLIST.md) | Carry-forward watchlist for the next full-package QA pass. |
| [LATEST_UPDATE_REVIEW.md](LATEST_UPDATE_REVIEW.md) | Generated latest-release triage review. |
| [RECURRING_REPORT_REGISTER.md](RECURRING_REPORT_REGISTER.md) | Register of generated recurring reports. |
| [RELEASE_READINESS.md](RELEASE_READINESS.md) | Current-publication readiness. |

## Generated state profiles

`state_profiles/<ST>.md` holds one generated publication profile per state and territory. [`../scripts/build_state_profiles.py`](../scripts/build_state_profiles.py) owns generation; [`DATA_GOVERNANCE.md`](DATA_GOVERNANCE.md) owns the publication allowlist, and `../site/state.html` plus `../data/state_profiles.json` are the reader-facing index. Do not hand-edit a profile; change its validated inputs and rebuild.

## Reviewer and communication artifacts

| Document | Owns |
| --- | --- |
| [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) | Compact reviewer path and role-to-evidence map. |
| [SQL_ANALYSIS.md](SQL_ANALYSIS.md) | Read-only SQL queries and independent reconciliations. |
| [EXCEL_WORKBOOK.md](EXCEL_WORKBOOK.md) | Workbook structure, formulas, and authority boundary. |
| [POWERPOINT_DECK.md](POWERPOINT_DECK.md) | Management briefing deck structure. |
| [PUBLICATION_HANDOFF.md](PUBLICATION_HANDOFF.md) | Publication handoff state. |
