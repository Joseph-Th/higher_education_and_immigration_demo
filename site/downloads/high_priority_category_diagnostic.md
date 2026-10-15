# High-Priority IPEDS Category Countermovement Diagnostic

This diagnostic adds an internal source-data check to the 27-record high-priority 2023-2024 QA queue. For each continuing institution it reconciles the all-student IPEDS total to the mutually exclusive race/ethnicity categories, then measures how much of the other-category movement runs opposite the U.S. nonresident change.

**Interpretation boundary:** countermovement is a review signal only. It can reflect real demographic turnover, reporting practice, classification changes, or a mixture of those mechanisms. It does not prove miscoding, does not correct IPEDS, and does not change the evidence-backed publication class by itself.

## Summary

- **25** continuing high-priority rows have a two-year category comparison.
- **8** have gross opposite-category movement at least as large as the absolute U.S. nonresident change.
- **3** have opposite-category movement between 50% and 100% of the U.S. nonresident change.
- **14** have opposite-category movement below 50% of the U.S. nonresident change.
- **2** analytic-universe exits are retained in the 27-row coverage but are not given a two-year category comparison.

## Strongest internal countermovement signals

| Institution | NR change | Total change | Opposite-category movement | Ratio to NR change | Largest opposite category | Publication gate |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Polk State College | +288 | +2,355 | 1,950 | 677.1% | White (-1,192) | hold_for_confirmation |
| Anderson University | -176 | +385 | 588 | 334.1% | Race / ethnicity unknown (+365) | hold_for_confirmation |
| Colorado State University Global | +183 | +750 | 377 | 206.0% | Race / ethnicity unknown (-279) | hold_for_confirmation |
| University of the Cumberlands | +4,616 | +1,793 | 7,086 | 153.5% | Asian (-3,593) | hold_for_confirmation |
| Louisiana Tech University | +342 | +446 | 441 | 128.9% | Race / ethnicity unknown (-329) | safe_with_context |
| Oakwood University | -192 | -93 | 245 | 127.6% | Race / ethnicity unknown (+227) | safe_with_context |
| Community College of Rhode Island | +1,176 | -243 | 1,428 | 121.4% | Hispanic / Latino (-733) | hold_for_confirmation |
| Norfolk State University | +278 | +8 | 280 | 100.7% | Black / African American (-221) | safe_with_context |
| Grambling State University | +264 | +36 | 241 | 91.3% | Black / African American (-204) | safe_with_context |
| Sofia University | +930 | +108 | 847 | 91.1% | Asian (-776) | hold_for_confirmation |

## Complete diagnostic

| Institution | Status | NR change | Other-category net change | Countermovement ratio | Signal | Publication gate |
| --- | --- | ---: | ---: | ---: | --- | --- |
| University of the Cumberlands | Continuing | +4,616 | -2,823 | 153.5% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| Collin County Community College District | Continuing | +2,256 | -480 | 46.0% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Broward College | Continuing | +2,005 | -417 | 45.6% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Miami Dade College | Continuing | +1,458 | +18,344 | 0.1% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Trine University-Regional/Non-Traditional Campuses | Continuing | +1,441 | +197 | 0.8% | Countermovement below half of the nonresident change | safe_with_context |
| Campbellsville University | Continuing | -1,358 | -257 | 41.4% | Countermovement below half of the nonresident change | safe_with_context |
| The University of Texas at Dallas | Continuing | -1,225 | +226 | 48.8% | Countermovement below half of the nonresident change | hold_for_confirmation |
| St. Francis College | Continuing | +1,220 | -205 | 17.9% | Countermovement below half of the nonresident change | safe_with_context |
| Community College of Rhode Island | Continuing | +1,176 | -1,419 | 121.4% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| University of North Texas | Continuing | -1,052 | +409 | 86.0% | Countermovement at least half as large as the nonresident change | safe_with_context |
| Webster University | Continuing | +1,020 | -366 | 40.8% | Countermovement below half of the nonresident change | safe_with_context |
| Sofia University | Continuing | +930 | -822 | 91.1% | Countermovement at least half as large as the nonresident change | hold_for_confirmation |
| Avila University | Continuing | +850 | +185 | 1.3% | Countermovement below half of the nonresident change | safe_with_context |
| Southeastern University | Continuing | +706 | +404 | 0.0% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Belhaven University | Continuing | +470 | +127 | 1.1% | Countermovement below half of the nonresident change | safe_with_context |
| Louisiana Tech University | Continuing | +342 | +104 | 128.9% | Countermovement at least as large as the nonresident change | safe_with_context |
| Cumberland University | Continuing | +306 | +79 | 44.1% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Oakton College | Continuing | +299 | +998 | 0.0% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Polk State College | Continuing | +288 | +2,067 | 677.1% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| Norfolk State University | Continuing | +278 | -270 | 100.7% | Countermovement at least as large as the nonresident change | safe_with_context |
| Grambling State University | Continuing | +264 | -228 | 91.3% | Countermovement at least half as large as the nonresident change | safe_with_context |
| Oakwood University | Continuing | -192 | +99 | 127.6% | Countermovement at least as large as the nonresident change | safe_with_context |
| Colorado State University Global | Continuing | +183 | +567 | 206.0% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| California Institute of Advanced Management | Continuing | +179 | +2 | 0.0% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Anderson University | Continuing | -176 | +561 | 334.1% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| Reformed University | Left analytic universe | -130 | — | — | Analytic-universe change; category comparison not used | safe_with_context |
| The College of Saint Rose | Left analytic universe | -115 | — | — | Analytic-universe change; category comparison not used | safe_with_context |

## Accounting rule

For each continuing institution, the 2023 and 2024 all-student IPEDS rows are checked separately so that `EFTOTLT` equals the sum of American Indian/Alaska Native, Asian, Black/African American, Hispanic/Latino, Native Hawaiian/Pacific Islander, White, Two or more races, Race/ethnicity unknown, and `EFNRALT`. The change identity must then satisfy `total change = nonresident change + net change across all other categories`.

Gross countermovement sums only category changes that move opposite the sign of the U.S. nonresident change. Because ordinary enrollment turnover can also create countermovement, the ratio is intentionally diagnostic rather than dispositive.
