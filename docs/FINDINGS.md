# Findings Memo

This memo records the current analytical takeaways behind the public brief. It is intentionally concise enough to use when explaining the project in an interview while preserving the exact quantitative basis for each claim.

## 1. Enrollment recovered above the pre-pandemic peak

The analytic universe contains **1,044,137 U.S. nonresident students in fall 2024**, equal to **5.31%** of total fall enrollment.

That is **63,400 students (+6.5%) above 2015**. The largest one-year decline occurred in 2020 (**-12.9%**), followed by recovery, including a **+9.3%** increase in 2022.

## 2. The decade-level increase came entirely from graduate enrollment

From 2015 to 2024:

- graduate U.S. nonresident enrollment increased by **138,765 students (+33.3%)**;
- undergraduate U.S. nonresident enrollment decreased by **75,365 students (-13.4%)**;
- the two movements net to the national increase of **63,400 students**.

Graduate enrollment overtook undergraduate enrollment in 2022. In 2024, graduate students represented **53.2%** of U.S. nonresident enrollment.

This is stronger than saying the recovery was merely “graduate-heavy”: the graduate increase more than accounted for the entire net national gain and offset a substantial undergraduate decline.

## 3. State recovery is broad but incomplete

Using fall 2019 as the pre-pandemic baseline, **33 of the 50 states plus DC** were at or above their 2019 U.S. nonresident enrollment by 2024. **18** remained below.

Largest absolute gains from 2019 to 2024 include:

| State | Change |
| --- | ---: |
| Illinois | +14,464 |
| Texas | +14,279 |
| Indiana | +12,853 |
| Florida | +11,980 |
| Missouri | +11,148 |

Largest shortfalls include:

| State | Change |
| --- | ---: |
| California | -33,282 |
| Oregon | -4,265 |
| Kansas | -3,842 |
| Washington | -3,834 |
| Idaho | -3,648 |

The national recovery therefore does not imply that every major destination returned to its prior trajectory.

## 4. Enrollment is concentrated, but the two largest states lost some share

In 2024:

- the 10 institutions with the largest U.S. nonresident enrollments account for **12.0%** of the national total;
- the top 100 institutions account for **50.4%**;
- the top five states account for **41.6%**.

New York and California together accounted for **22.0%** of the 2024 total, down from **24.7%** in 2015. The top-five state share also declined modestly from **42.5%** to **41.6%**.

## 5. Growth shifted toward private nonprofit institutions

The 2015-to-2024 national increase was not evenly distributed by institutional control:

| Control | 2015 | 2024 | Change |
| --- | ---: | ---: | ---: |
| Public | 626,119 | 610,032 | -16,087 |
| Private nonprofit | 330,778 | 413,603 | +82,825 |
| Private for-profit | 23,840 | 20,502 | -3,338 |

Private nonprofits increased from **33.7% to 39.6%** of national U.S. nonresident enrollment. Their graduate U.S. nonresident enrollment increased by **83,792 students (+48.2%)**, while their undergraduate count was almost flat (**-967**).

Public institutions still enroll the majority of U.S. nonresident students, but their share fell from **63.8% to 58.4%**. Their graduate enrollment grew while undergraduate enrollment fell substantially, producing a net decline of **16,087**.

## 6. The national increase is not an artifact of a larger institution universe

Matching institutions by IPEDS `UNITID` between 2015 and 2024 separates change at continuing institutions from changes in analytic-universe membership.

- **3,470** institutions appear in both endpoint years.
- Those continuing institutions added **66,981** U.S. nonresident students.
- **327** institutions entered the analytic universe and account for **10,666** students in 2024.
- **1,092** institutions left the analytic universe and had **14,247** students in 2015.
- Entry and exit therefore net to **-3,581**, while the full national change is **+63,400**.

Among continuing institutions, **1,479 grew**, **1,411 declined**, and **580 were unchanged**. Gross gains at continuing institutions totaled **+257,836**, offset by **-190,855** in gross declines. The national increase is therefore the net result of substantial institution-level reallocation, not uniform growth.

The same accounting holds for the post-pandemic comparison: continuing institutions account for **+75,632** of the **+71,079** national increase from 2019 to 2024, while entry and exit net negative.

“Entered” and “left” refer only to membership in the defined IPEDS analytic universe. These statuses can reflect mergers, UNITID restructuring, eligibility or classification changes, and actual openings or closures.

## Latest release note: 2024 growth shifted back toward undergraduate enrollment

The decade-level growth story is graduate-driven, but the newest annual movement is different. From 2023 to 2024:

- total U.S. nonresident enrollment increased by **29,539 students (+2.9%)**;
- undergraduate U.S. nonresident enrollment increased by **31,592**;
- graduate U.S. nonresident enrollment decreased by **2,053**.

The two student-level components reconcile exactly to the national increase. At the institution level, **3,781 continuing institutions** contribute **+29,968**, while institutions entering and leaving the analytic universe net to **-429**. Florida contributes the largest state increase (**+6,207**), followed by Kentucky (**+4,615**).

The latest-release QA packet contains **27 high-priority**, **50 medium-priority**, and **213 low-priority** institution records under explicit review thresholds. These are triage records, not presumed errors. University of the Cumberlands, for example, reports 4,226 U.S. nonresident students in 2022, 0 in 2023, and 4,616 in 2024; the 2023 value is marked reported (`R`). The pipeline retains that official value, while ICE SEVP's official 2023 Top 500 F-1 Schools table separately records 8,551 active F-1 SEVIS records for the university. Because SEVIS active records and IPEDS fall-census U.S. nonresident enrollment use different timing and population frames, the figures are not substituted or numerically reconciled. The federal evidence instead supports a bounded conclusion that the IPEDS zero reflects a reporting/scope discontinuity rather than a literal absence of international students.

## 7. Release vintage matters even when the universe is correct

NCES Digest 2025 Table 306.10 was prepared in March 2026. This project uses IPEDS complete-data files retrieved in October 2026.

For 2024, the current pipeline produces total fall enrollment of **19,659,633**, while the Digest reports **19,659.6 thousand**, effectively the same universe after published rounding.

The U.S. nonresident subgroup differs slightly: **1,044,137** in the current file versus approximately **1,047,100** in the March 2026 Digest, a **-0.28%** difference. Undergraduate nonresident enrollment differs by **-0.54%** and graduate enrollment by **-0.04%**.

Those differences are retained and reported. The project does not modify current-source data to reproduce an older provisional publication.

## What this analysis does not establish

The IPEDS U.S. nonresident category is not synonymous with all international students, immigrant-origin students, undocumented students, DACA recipients, or foreign-born students. State totals identify the location of the reporting institution, not the student's legal residence or country of origin. The data are fall snapshots rather than annual unduplicated counts.

