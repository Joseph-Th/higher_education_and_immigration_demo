# Candidate 2025 Directory Change Review

This review expands the candidate-directory preflight from aggregate counts to the affected public institution records. It remains **directory-side readiness evidence only**. A change in directory eligibility, institutional control, state, or name is not evidence of a campus opening/closure or a candidate-year enrollment change.

- **Captured preflight:** `2026-10-17T15:13:02+00:00`
- **Current analysis year:** 2024
- **Candidate year:** 2025
- **Affected UNITIDs:** 154
- **Directory-eligible entry / exit:** 52 / 56
- **Shared eligible records with changed attributes:** 46
- **Year advance:** not authorized; snapshot decision remains `HOLD_YEAR_ADVANCE`

## Frame turnover

The candidate directory has 52 UNITIDs entering the directory-side eligible set and 56 leaving it, a net change of -4. Reason counts can overlap when one record changes more than one eligibility field.

### Entry reasons

| Structural reason | UNITIDs |
| --- | ---: |
| New directory record | 35 |
| Degree-granting status became eligible | 11 |
| Title IV / First Look status became eligible | 6 |

### Exit reasons

| Structural reason | UNITIDs |
| --- | ---: |
| Title IV / First Look status became ineligible | 38 |
| Directory record absent in candidate file | 15 |
| Degree-granting status became ineligible | 3 |

## Current-year exposure among candidate-frame leavers

Of the 56 directory-side leavers, 54 appear in the current 2024 canonical institution analysis. Together those rows contain **612 U.S. nonresident students** and **17,593 total students** in 2024. These are current-year exposure measures only; they are not projected 2025 losses and do not imply that absent directory records represent institutional closures.

| UNITID | Institution | State | Exit reason | Current nonresident | Current total |
| ---: | --- | --- | --- | ---: | ---: |
| 114354 | FIDM-Fashion Institute of Design & Merchandising | CA | Title IV / First Look status became ineligible | 128 | 564 |
| 214564 | Salus University | PA | Title IV / First Look status became ineligible | 106 | 1,106 |
| 218238 | Limestone University | SC | Directory record absent in candidate file | 89 | 1,807 |
| 108852 | American Academy of Dramatic Arts-Los Angeles | CA | Title IV / First Look status became ineligible | 39 | 112 |
| 148876 | St. Augustine College | IL | Title IV / First Look status became ineligible | 30 | 810 |
| 421841 | New York Conservatory for Dramatic Arts | NY | Title IV / First Look status became ineligible | 29 | 251 |
| 199698 | St. Andrews University | NC | Directory record absent in candidate file | 29 | 676 |
| 477039 | West Coast University-Texas | TX | Title IV / First Look status became ineligible | 29 | 1,887 |
| 216463 | Trinity Anglican Seminary | PA | Title IV / First Look status became ineligible | 23 | 169 |
| 239512 | Northland College | WI | Directory record absent in candidate file | 21 | 286 |

## Control changes

Six shared directory-eligible UNITIDs change institutional control. Their current 2024 U.S. nonresident enrollment totals **1,069**. This is a control-comparability flag for the next release, not a national enrollment change.

| UNITID | Institution | State | Current control | Candidate control | Current nonresident |
| ---: | --- | --- | --- | --- | ---: |
| 104717 | Grand Canyon University | AZ | Private for-profit | Private nonprofit | 967 |
| 154022 | The University of Arizona Global Campus | CA | Private for-profit | Public | 96 |
| 154518 | Waldorf University | IA | Private for-profit | Private nonprofit | 6 |
| 377652 | Valley College-Beckley | WV | Private for-profit | Private nonprofit | 0 |
| 494250 | Valley College-Cleveland | OH | Private for-profit | Private nonprofit | 0 |
| 377661 | Valley College-Martinsburg | WV | Private for-profit | Private nonprofit | 0 |

## State changes

Three shared directory-eligible UNITIDs change state codes and carry **193** current-year U.S. nonresident students. Recheck state attribution after the complete candidate-year package is available; do not treat the directory move by itself as student migration.

| UNITID | Institution | Current state | Candidate state | Current nonresident |
| ---: | --- | --- | --- | ---: |
| 154022 | The University of Arizona Global Campus | CA | AZ | 96 |
| 167792 | Simon's Rock at Bard College | MA | NY | 91 |
| 443331 | West Coast University-Texas | CA | TX | 6 |

## Name continuity

Forty-one shared eligible UNITIDs change institution-name strings. Those records represent **10,184** current-year U.S. nonresident students. UNITID, not the displayed name string, remains the continuity key. The table shows the ten largest current-year exposures; the governed CSV contains all affected records.

| UNITID | Current name | Candidate name | Current nonresident |
| ---: | --- | --- | ---: |
| 225423 | Houston Community College | Houston City College | 4,670 |
| 157216 | Lindsey Wilson College | Lindsey Wilson University | 2,027 |
| 166656 | MCPHS University | Massachusetts College of Pharmacy and Health Sciences | 866 |
| 236610 | Shoreline Community College | Shoreline College | 615 |
| 134495 | Hillsborough Community College | Hillsborough College | 409 |
| 213020 | Indiana University of Pennsylvania-Main Campus | Indiana University of Pennsylvania | 373 |
| 115773 | Humphreys University-Stockton and Modesto Campuses | Humphreys University | 288 |
| 176053 | Mississippi College | Mississippi Christian University | 160 |
| 225502 | University of Houston-Victoria | Texas A&M University-Victoria | 145 |
| 195474 | Siena College | Siena University | 122 |

## Interpretation and next-release rule

The change review is a pre-analysis QA queue. When Fall Enrollment arrives, rebuild the full analytic join and determine which directory-side entries/exits actually enter the candidate enrollment universe. Reconcile state and control changes before interpreting subgroup movement, retain UNITID continuity across name changes, and investigate material discontinuities before institution-specific narrative. The directory review must never substitute current-year exposure for an unobserved candidate-year value.
