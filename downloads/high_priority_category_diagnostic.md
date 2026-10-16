# High-Priority IPEDS Category Countermovement Diagnostic

This diagnostic adds an internal source-data check to the 27-record high-priority 2023-2024 QA queue. For each continuing institution it reconciles the all-student IPEDS total to the mutually exclusive race/ethnicity categories, then measures how much of the other-category movement runs opposite the U.S. nonresident change.

**Interpretation boundary:** countermovement is a review signal only. It can reflect real demographic turnover, reporting practice, classification changes, or a mixture of those mechanisms. It does not prove miscoding, does not correct IPEDS, and does not change the evidence-backed publication class by itself.

## Summary

- **25** continuing high-priority rows have a two-year category comparison.
- **8** have gross opposite-category movement at least as large as the absolute U.S. nonresident change.
- **3** have opposite-category movement between 50% and 100% of the U.S. nonresident change.
- **14** have opposite-category movement below 50% of the U.S. nonresident change.
- **0** continuing rows are withheld from the ratio because endpoint status codes fall outside the diagnostic R/Z rule.
- **2** analytic-universe exits are retained in the 27-row coverage but are not given a two-year category comparison.

## Strongest internal countermovement signals

| Institution | NR change | NR status | Total change | Opposite-category movement | Ratio to NR change | Largest opposite category | Category status | Publication gate |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| Polk State College | +288 | R→R | +2,355 | 1,950 | 677.1% | White (-1,192) | R→R | hold_for_confirmation |
| Anderson University | -176 | R→R | +385 | 588 | 334.1% | Race / ethnicity unknown (+365) | R→R | safe_with_context |
| Colorado State University Global | +183 | R→R | +750 | 377 | 206.0% | Race / ethnicity unknown (-279) | R→R | hold_for_confirmation |
| University of the Cumberlands | +4,616 | R→R | +1,793 | 7,086 | 153.5% | Asian (-3,593) | R→R | safe_with_context |
| Louisiana Tech University | +342 | R→R | +446 | 441 | 128.9% | Race / ethnicity unknown (-329) | R→R | safe_with_context |
| Oakwood University | -192 | R→Z | -93 | 245 | 127.6% | Race / ethnicity unknown (+227) | R→R | safe_with_context |
| Community College of Rhode Island | +1,176 | R→R | -243 | 1,428 | 121.4% | Hispanic / Latino (-733) | R→R | hold_for_confirmation |
| Norfolk State University | +278 | R→R | +8 | 280 | 100.7% | Black / African American (-221) | R→R | safe_with_context |
| Grambling State University | +264 | R→R | +36 | 241 | 91.3% | Black / African American (-204) | R→R | safe_with_context |
| Sofia University | +930 | R→R | +108 | 847 | 91.1% | Asian (-776) | R→R | safe_with_context |

## Complete diagnostic

| Institution | Status | NR change | NR status | Other-category net change | Countermovement ratio | Signal | Publication gate |
| --- | --- | ---: | --- | ---: | ---: | --- | --- |
| University of the Cumberlands | Continuing | +4,616 | R→R | -2,823 | 153.5% | Countermovement at least as large as the nonresident change | safe_with_context |
| Collin County Community College District | Continuing | +2,256 | R→R | -480 | 46.0% | Countermovement below half of the nonresident change | safe_with_context |
| Broward College | Continuing | +2,005 | R→R | -417 | 45.6% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Miami Dade College | Continuing | +1,458 | R→R | +18,344 | 0.1% | Countermovement below half of the nonresident change | hold_for_confirmation |
| Trine University-Regional/Non-Traditional Campuses | Continuing | +1,441 | R→R | +197 | 0.8% | Countermovement below half of the nonresident change | safe_with_context |
| Campbellsville University | Continuing | -1,358 | R→R | -257 | 41.4% | Countermovement below half of the nonresident change | safe_with_context |
| The University of Texas at Dallas | Continuing | -1,225 | R→R | +226 | 48.8% | Countermovement below half of the nonresident change | safe_with_context |
| St. Francis College | Continuing | +1,220 | R→R | -205 | 17.9% | Countermovement below half of the nonresident change | safe_with_context |
| Community College of Rhode Island | Continuing | +1,176 | R→R | -1,419 | 121.4% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| University of North Texas | Continuing | -1,052 | R→R | +409 | 86.0% | Countermovement at least half as large as the nonresident change | safe_with_context |
| Webster University | Continuing | +1,020 | R→R | -366 | 40.8% | Countermovement below half of the nonresident change | safe_with_context |
| Sofia University | Continuing | +930 | R→R | -822 | 91.1% | Countermovement at least half as large as the nonresident change | safe_with_context |
| Avila University | Continuing | +850 | R→R | +185 | 1.3% | Countermovement below half of the nonresident change | safe_with_context |
| Southeastern University | Continuing | +706 | R→R | +404 | 0.0% | Countermovement below half of the nonresident change | safe_with_context |
| Belhaven University | Continuing | +470 | R→R | +127 | 1.1% | Countermovement below half of the nonresident change | safe_with_context |
| Louisiana Tech University | Continuing | +342 | R→R | +104 | 128.9% | Countermovement at least as large as the nonresident change | safe_with_context |
| Cumberland University | Continuing | +306 | R→R | +79 | 44.1% | Countermovement below half of the nonresident change | safe_with_context |
| Oakton College | Continuing | +299 | R→R | +998 | 0.0% | Countermovement below half of the nonresident change | safe_with_context |
| Polk State College | Continuing | +288 | R→R | +2,067 | 677.1% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| Norfolk State University | Continuing | +278 | R→R | -270 | 100.7% | Countermovement at least as large as the nonresident change | safe_with_context |
| Grambling State University | Continuing | +264 | R→R | -228 | 91.3% | Countermovement at least half as large as the nonresident change | safe_with_context |
| Oakwood University | Continuing | -192 | R→Z | +99 | 127.6% | Countermovement at least as large as the nonresident change | safe_with_context |
| Colorado State University Global | Continuing | +183 | R→R | +567 | 206.0% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| California Institute of Advanced Management | Continuing | +179 | R→R | +2 | 0.0% | Countermovement below half of the nonresident change | safe_with_context |
| Anderson University | Continuing | -176 | R→R | +561 | 334.1% | Countermovement at least as large as the nonresident change | safe_with_context |
| Reformed University | Left analytic universe | -130 | — | — | — | Analytic-universe change; category comparison not used | safe_with_context |
| The College of Saint Rose | Left analytic universe | -115 | — | — | — | Analytic-universe change; category comparison not used | safe_with_context |

## Accounting rule

For each continuing institution, the 2023 and 2024 all-student IPEDS rows are checked separately so that `EFTOTLT` equals the sum of American Indian/Alaska Native, Asian, Black/African American, Hispanic/Latino, Native Hawaiian/Pacific Islander, White, Two or more races, Race/ethnicity unknown, and `EFNRALT`. The change identity must then satisfy `total change = nonresident change + net change across all other categories`. A countermovement ratio is calculated only when every endpoint total/category status code is `R` (Reported) or `Z` (Implied zero); other official status-coded values remain visible but are withheld from ratio comparison.

Gross countermovement sums only category changes that move opposite the sign of the U.S. nonresident change. Because ordinary enrollment turnover can also create countermovement, the ratio is intentionally diagnostic rather than dispositive.
