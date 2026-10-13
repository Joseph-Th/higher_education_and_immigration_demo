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

## JSON products

`data/qa_report.json` contains structural checks, yearly source/flag distributions, row counts, and explicit exclusions.

`data/findings.json` contains the derived findings used by the public static site: headline metrics, level decomposition, state recovery, concentration, institutional control, institution-universe dynamics, rankings, and national series.

