# Release and Freshness Monitor

This is a **dated portfolio monitoring snapshot**, not a continuously live dashboard. The NCES availability observation is captured by the separate online release checker; the offline build preserves and validates that observation without making network access a reproducibility dependency.

- **Captured check:** 2026-10-14T04:16:17+00:00
- **Current analysis end year:** 2024
- **Candidate next year:** 2025
- **Candidate package:** 2/4 required files available
- **Decision:** HOLD YEAR ADVANCE

## Monitoring register

| ID | Area | Subject | Observed | Status | Next action |
| --- | --- | --- | --- | --- | --- |
| R01 | NCES release package | 2025 Fall Enrollment data | 2026-10-14 | NOT AVAILABLE | Continue monitoring; do not substitute a partial next-year package into the analysis. |
| R02 | NCES release package | 2025 Fall Enrollment dictionary | 2026-10-14 | NOT AVAILABLE | Continue monitoring; do not substitute a partial next-year package into the analysis. |
| R03 | NCES release package | 2025 Institutional directory data | 2026-10-14 | AVAILABLE | Preserve the observation and include the file in schema review after the full package is ready. |
| R04 | NCES release package | 2025 Institutional directory dictionary | 2026-10-14 | AVAILABLE | Preserve the observation and include the file in schema review after the full package is ready. |
| G01 | Annual release gate | Advance analysis from 2024 to 2025 | 2026-10-14 | HOLD YEAR ADVANCE | Keep END_YEAR=2024; rerun the live release check later and advance only after the complete package is available. |
| S01 | Source review | Research Library | 2026-10-13 | REVIEW RECORDED | Perform a human source review before changing last_checked metadata; URL health alone does not refresh it. |
| S02 | Source review | Population/source crosswalk | 2026-10-13 | REVIEW RECORDED | Re-review the affected source before using it in a companion comparison or changing public interpretation. |
| P01 | Recurring product | Undocumented Students in U.S. Higher Education | 2026-10-13 | MONITOR TRIGGER | At kickoff, confirm partner timeline, exact ACS vintage, method changes, delivery format, review milestones, and final sign-off owner |
| P02 | Recurring product | Immigrant-Origin Students in Higher Education | 2026-10-13 | MONITOR TRIGGER | At kickoff, confirm partner timeline, CPS vintage, population-definition changes, state outputs, review milestones, and final sign-off owner |
| P03 | Recurring product | Undocumented Students Graduating High School | 2026-10-13 | MONITOR TRIGGER | At kickoff, confirm partner timeline, pooled ACS period, NCES rate vintage, model changes, review milestones, and final sign-off owner |

## Operational rule

The current snapshot does not authorize advancing beyond Fall 2024 unless the complete 2025 package is available. A newly posted file is a review trigger, not automatic permission to publish. Recurring-product dates are not inferred from prior public release dates; kickoff and partner milestones remain confirmation-dependent.

## Refresh the live observation

```bash
python scripts/check_for_new_release.py --write-snapshot data/release_monitor_snapshot.json
python scripts/build_freshness_monitor.py
```
