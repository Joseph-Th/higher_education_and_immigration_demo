# Variable Mapping

This document records the minimal cross-year IPEDS variables required for the first analysis. The mapping is verified programmatically by `scripts/audit_ipeds_schema.py` against the official data dictionaries for every year from 2015 through 2024.

## Fall Enrollment (`EFyyyyA`)

| Analytic concept | IPEDS variable | Intended use |
| --- | --- | --- |
| Institution identifier | `UNITID` | Join enrollment to institutional directory data |
| Aggregation/student level | `EFALEVEL` | Select non-overlapping total, undergraduate, and graduate rows |
| Total fall enrollment | `EFTOTLT` | Denominator and total-enrollment trend |
| U.S. nonresident enrollment | `EFNRALT` | Primary population count |

### `EFALEVEL` rows used

| Code | Label | Use |
| ---: | --- | --- |
| `1` | All students total | Institution-level total used for the main trend and share calculations |
| `2` | All students, Undergraduate total | Undergraduate comparison |
| `12` | All students, Graduate | Graduate comparison |

These rows are mutually useful views of the same institution's enrollment. They must not be summed together. The main institution total uses code `1`; codes `2` and `12` are used only for the level-specific breakdown.

## Institutional Directory (`HDyyyy`)

| Analytic concept | IPEDS variable | Intended use |
| --- | --- | --- |
| Institution identifier | `UNITID` | Join key |
| Institution name | `INSTNM` | Human-readable institution label and QA |
| State/jurisdiction | `STABBR` | State-level aggregation |
| Institutional control | `CONTROL` | Public / private nonprofit / private for-profit analysis |
| Degree-granting status | `DEGGRANT` | Restrict analytic universe to degree-granting institutions (`1`) |
| First Look/Digest universe | `PSET4FLG` | Restrict analytic universe to NCES First Look/Digest Title IV selection (`1` or `3`) |

Additional institutional characteristics will be added only if a research question requires them and their cross-year definitions are reviewed first.

## Terminology change

The variable name `EFNRALT` is stable across the period, but its displayed title changes. The 2015 dictionary labels it **Nonresident alien total**, while the 2024 dictionary labels it **U.S. Nonresident total**.

The project will use the current term **U.S. nonresident** in narrative text while documenting the historical title difference. A stable variable name does not by itself prove conceptual comparability, so survey instructions and definitions remain part of the methodology review.

## Revised files

Historical NCES ZIP archives can contain both an original CSV and a revised `_rv.csv` file. When a revised file is present, the analysis pipeline will prefer the revised version. The schema audit records the exact preferred CSV for each year.

Fall 2024 currently contains only the base `ef2024a.csv` file in the downloaded archive and is treated as provisional in this project.

## Audit output

`data/schema_audit.csv` records, for each year:

- whether all required variables are present;
- the selected enrollment and directory CSV filenames;
- the title used for `EFNRALT` in that year's dictionary;
- labels for `EFALEVEL` codes 1, 2, and 12; and
- any schema exception requiring review.

