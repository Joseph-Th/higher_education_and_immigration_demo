# Publication Handoff Register

This is a portfolio demonstration of the final QA/QC handoff between validated analysis and a public data-page refresh. It does **not** represent the Presidents' Alliance's internal publication workflow or approval chain.

**Current release:** Fall 2024 (provisional)  
**Claim/register rows:** 11  
**State/DC profiles:** 51  
**External benchmark checks:** 24/24 PASS

## Publication claims

| ID | Surface | Public copy | QA gate | Disclosure | Status |
| --- | --- | --- | --- | --- | --- |
| N01 | National headline | Fall 2024 U.S. nonresident enrollment: 1,044,137 students. | State totals and student-level components reconcile to the national value; NCES benchmark is within threshold. | Fall 2024 is provisional. | READY |
| N02 | National headline | U.S. nonresident students are 5.31% of fall enrollment in the analytic universe. | Published percentage is recalculated from current counts in repository tests. | Share applies only to the documented degree-granting First Look/Digest universe. | READY WITH CONTEXT |
| N03 | Longitudinal finding | U.S. nonresident enrollment is +63,400 (+6.5%) from 2015 to 2024. | Endpoint difference reconciles to student-level and institutional-control decompositions. | The endpoint includes 2024 provisional data. | READY |
| N04 | Student-level finding | Across 2015-2024, graduate U.S. nonresident enrollment changed +138,765 while undergraduate enrollment changed -75,365. | Undergraduate plus graduate counts reconcile exactly to total U.S. nonresident enrollment for every year. | Student-level categories follow IPEDS aggregation codes documented in the methodology. | READY |
| N05 | Latest release update | From 2023 to 2024, enrollment changed +29,539: undergraduate +31,592, graduate -2,053. | Student-level changes reconcile exactly to the national annual change and the institution-accounting bridge. | One annual movement is not treated as evidence of a durable trend change. | READY WITH CONTEXT |
| S01 | State data package | 33 states/DC are at or above 2019 U.S. nonresident enrollment; 18 remain below. | All 51 state/DC profiles are present and their latest counts sum exactly to 1,044,137. | State is institution location, not student residence, nationality, or immigration status. | READY WITH CONTEXT |
| C01 | Institutional-control finding | Private nonprofit institutions changed +82,825 U.S. nonresident students from 2015 to 2024. | Public, private nonprofit, and private for-profit totals reconcile exactly to the national series in every year. | Institutional control comes from each year's IPEDS directory file. | READY |
| I01 | Institution-universe finding | Continuing institutions contributed +66,981 to the 2015-2024 change; universe entry/exit netted -3,581. | All endpoint institution contributions sum exactly to the national change. | Universe entry/exit can reflect mergers, eligibility, or identifier restructuring, not only openings/closures. | READY WITH CONTEXT |
| Q01 | Institution-level QA | 11 high-priority records have manual dispositions: 2 safe with context and 9 held for confirmation. | The required reviewed sample covers the ten highest-impact current high-priority rows; evidence links are separately health-checked. | Automated flags are triage, not corrections; held records remain in official aggregate calculations. | READY WITH CLAIM-LEVEL HOLDS |
| M01 | Definition / methodology | IPEDS U.S. nonresident is not a measure of undocumented, DACA, immigrant-origin, refugee/asylee, or all foreign-born students. | Population crosswalk explicitly records inclusion, exclusion, source vintage, unit, geography, and comparison warning. | Other Portal populations require their own source systems and methods. | READY |
| B01 | External validation | 24/24 NCES Digest consistency checks pass for 2019-2024. | Current IPEDS values stay within documented thresholds without being overwritten to match an older publication vintage. | Digest values are rounded and come from a different release vintage. | READY WITH CONTEXT |

## Handoff rule

A value is not publication-ready merely because the calculation ran. The handoff checks the population definition, release status, arithmetic reconciliation, citation/source role, claim scope, and any unresolved institution-level evidence before the public copy is approved.
