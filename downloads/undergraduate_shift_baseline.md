# R01 Undergraduate Shift Baseline

This note establishes the fixed 2023-2024 baseline for R01 before the next IPEDS Fall Enrollment release arrives. It does **not** answer whether the shift persists; that requires a complete next-year package, schema review, and the same decomposition on the new release.

## Baseline finding

- Undergraduate U.S. nonresident enrollment changed **+31,592** from 2023 to 2024; graduate enrollment changed **-2,053**, for a national net change of **+29,539**.
- Undergraduate enrollment increased in **45 of 51 states/DC** and declined in **6**. This is the widest state breadth of undergraduate growth in the 2015-2024 annual series.
- The 2023-2024 undergraduate increase is the **largest positive annual undergraduate change** in the series and the **third consecutive annual undergraduate increase**.
- By institutional control, undergraduate change was **Public +28,580**, **Private nonprofit +3,193**, and **Private for-profit -181**.
- Continuing institutions contributed **+31,932**; institutions entering the analytic universe contributed **+68** and exiting institutions had **408** undergraduate U.S. nonresident students in 2023. The entry/exit net is **-340**.
- State gross positive undergraduate movement was **33,778** against **2,186** of offsetting state declines; the top five positive states contributed **53.5%** of gross positive state movement.
- At the institution level, gross positive undergraduate movement was **49,570** against **17,978** of offsetting declines; the ten largest positive institution contributions accounted for **20.6%** of gross positive institution movement.

The breadth result and the institution-concentration result answer different questions. Forty-five states had undergraduate growth, while the top ten institutions accounted for only about one-fifth of gross positive institution movement. The state-level top-five share is higher because large states contain many institutions.

## Annual context

| Period | Undergraduate change | Graduate change | Net change | States/DC with undergraduate growth |
| --- | ---: | ---: | ---: | ---: |
| 2015-2016 | +4,946 | +10,700 | +15,646 | 24/51 |
| 2016-2017 | +4,129 | -2,041 | +2,088 | 27/51 |
| 2017-2018 | -8,750 | -1,233 | -9,983 | 15/51 |
| 2018-2019 | -16,852 | +1,422 | -15,430 | 13/51 |
| 2019-2020 | -79,674 | -46,304 | -125,978 | 2/51 |
| 2020-2021 | -18,591 | +53,507 | +34,916 | 23/51 |
| 2021-2022 | +1,082 | +80,663 | +81,745 | 31/51 |
| 2022-2023 | +6,753 | +44,104 | +50,857 | 33/51 |
| 2023-2024 | +31,592 | -2,053 | +29,539 | 45/51 |

## Largest current-state undergraduate increases

| State | Undergraduate change | Graduate change | Net change | Public | Private nonprofit | Private for-profit | Top-three institution share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Florida (FL) | +6,418 | -211 | +6,207 | +5,798 | +542 | +78 | 58.6% |
| Texas (TX) | +6,316 | -3,953 | +2,363 | +5,991 | +295 | +30 | 48.5% |
| Ohio (OH) | +2,110 | -1,297 | +813 | +1,801 | +140 | +169 | 37.8% |
| New Jersey (NJ) | +1,623 | -749 | +874 | +1,361 | +257 | +5 | 31.3% |
| Illinois (IL) | +1,613 | +533 | +2,146 | +1,127 | +534 | -48 | 36.3% |
| Rhode Island (RI) | +1,215 | +198 | +1,413 | +1,181 | +34 | 0 | 98.1% |
| Virginia (VA) | +1,067 | -15 | +1,052 | +850 | +146 | +71 | 44.2% |
| North Carolina (NC) | +1,012 | -374 | +638 | +885 | +127 | 0 | 30.2% |
| Louisiana (LA) | +940 | +407 | +1,347 | +940 | +1 | -1 | 58.9% |
| Indiana (IN) | +930 | +1,492 | +2,422 | +499 | +430 | +1 | 52.3% |

## States with undergraduate declines

| State | Undergraduate change | Graduate change | Net change | Top-three institution share |
| --- | ---: | ---: | ---: | ---: |
| California (CA) | -1,490 | +376 | -1,114 | 36.2% |
| District of Columbia (DC) | -257 | -128 | -385 | 77.4% |
| Pennsylvania (PA) | -185 | -482 | -667 | 35.9% |
| Oregon (OR) | -114 | -63 | -177 | 67.3% |
| Delaware (DE) | -95 | -222 | -317 | 100.0% |
| Alaska (AK) | -45 | +2 | -43 | 100.0% |

## Interpretation boundary

This analysis establishes the 2024 comparison point for the next-release persistence test. It does not call the current shift durable. R01 remains open until the next complete Fall Enrollment and directory package passes schema review and the national/state decomposition is repeated.

The control and institution-continuity decompositions are descriptive accounting rather than causal attribution. State identifies institution location, not student residence. Entry/exit can reflect eligibility, reporting, merger/reorganization, identifier, or location changes and should not automatically be interpreted as campus openings or closures.

## Reproduction

```bash
python scripts/build_undergraduate_shift_baseline.py
```

Canonical authorities are `data/processed/national_year.csv`, `data/processed/state_year.csv`, `data/processed/control_year.csv`, and `data/processed/institution_year.csv`.
