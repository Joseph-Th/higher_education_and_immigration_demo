# Research Memo: U.S. Nonresident Enrollment in Higher Education, 2015-2024

**Latest data:** Fall 2024 (provisional)  
**Universe:** degree-granting institutions in the IPEDS First Look/Digest Title IV universe, 50 states + DC  
**QA review date:** 2026-10-17

## Bottom line

U.S. nonresident enrollment reached **1,044,137** in Fall 2024, **5.31%** of enrollment in the analytic universe. The national count is **+63,400 (+6.5%)** above 2015, but the composition of that growth changed: the decade-level increase was entirely graduate-driven, while the newest annual increase was undergraduate-led.

From 2023 to 2024, U.S. nonresident enrollment increased **+29,539 (+2.9%)**. Undergraduate enrollment increased **+31,592**, with growth in **45 of 51 states/DC** and **+28,580** contributed by public institutions, while graduate enrollment declined **-2,053**. R01 remains a fixed baseline, not a persistence finding: the next complete release must remain positive nationally and in at least **26 of 51 states/DC** before the project calls the shift broadly persistent.

## Three findings that matter

1. **The recovery is real, but it is structurally different.** Graduate enrollment is **+138,765** above 2015, while undergraduate enrollment is **-75,365** below it. Graduate students now make up the majority of U.S. nonresident enrollment.
2. **Geography remains uneven.** **33** states/DC are at or above their 2019 level, while **18** remain below. FL posted the largest 2023-2024 increase at **+6,207**.
3. **The growth is not an artifact of a larger institution universe.** Continuing institutions contribute **+66,981** over 2015-2024; institution entry and exit net to **-3,581**. In the latest year, continuing institutions likewise contribute **+29,968** of the national change.

## Analyst judgment changes what gets published

The automated queue identified **27 high-priority** latest-release records. The manual review layer now covers **27/27** of them: **26** are safe to discuss with explicit context and **1** remain held for institution-specific interpretation. The examples below show why a flag is a review request rather than an error label.

### Hold the anomaly: Community College of Rhode Island

**Observed change:** +1,176  
**Publication decision:** Hold institution-specific claim  
**Evidence:** [CCRI Institutional Effectiveness enrollment dashboard + NECHE self-study + F-1 definition](https://www.ccri.edu/ie/)

IPEDS jumps from 12 to 1,188 U.S. nonresident students between Fall 2023 and Fall 2024. CCRI's official Institutional Effectiveness enrollment dashboard independently reports total enrollment of 12,518 in Fall 2023 and 12,275 in Fall 2024, exactly matching the project IPEDS totals for both years. The same dashboard's Race/Ethnicity table assigns the full census headcount to ordinary racial/ethnic buckets and does not expose a U.S. Nonresident or Nonresident Alien row; in Fall 2024 those displayed race/ethnicity buckets still sum to all 12,275 students even though IPEDS separately reports 1,188 students in its mutually exclusive U.S. Nonresident category and 11,087 across the remaining federal race/ethnicity categories. CCRI's 2024 NECHE self-study shows the same institutional taxonomy historically: its Fall 2022 race/ethnicity table totals the complete 12,263-student census population without a separate nonresident category. These two institutional sources establish that CCRI's public race/ethnicity taxonomy is not definition-identical to the mutually exclusive IPEDS race/ethnicity identity, so the dashboard category counts cannot be substituted for federal category counts or used to infer which students entered the IPEDS U.S. Nonresident category. CCRI's official international-student admissions page separately defines an international student as a foreign national studying on an F-1 non-immigrant temporary visa and explicitly excludes U.S. citizens, permanent residents, eligible non-immigrant visa holders, refugees, asylees, and temporary protected status populations. That F-1-only admissions construct is narrower than the project IPEDS U.S. nonresident category. The stronger evidence therefore confirms a category-scope mismatch around the exact institutional headcount, but neither public surface exposes a directly comparable 2023/2024 residency or citizenship series that can validate or contradict the 12-to-1,188 status change. Preserve IPEDS in aggregates and keep institution-specific interpretation held pending a directly comparable residency/citizenship measure.

### Corroborate the direction: Collin County Community College District

**Observed change:** +2,256  
**Publication decision:** Publish with context  
**Evidence:** [Collin College FY2025 ACFR Fall Student Profile](https://collin.edu/financials/documents/annual-comprehensive-financial-report-fy-2025.pdf)

IPEDS rises from 433 U.S. nonresident students in Fall 2023 to 2,689 in Fall 2024 (+2,256). Collin's FY2025 ACFR reports Fall headcount of 37,776 in Fall 2023 and 39,552 in Fall 2024, within four of IPEDS totals, and the Foreign category rising from 612 to 2,482. Its 2023-24 CDS reports 604 International (nonresident) students. Institutional labels are not assumed IPEDS-identical and counts are not substituted. Preserve IPEDS as numerical authority and clear only bounded direction-level discussion of the +2,256 movement.

### Explain the structural change: The College of Saint Rose

**Observed change:** -115  
**Publication decision:** Publish with context  
**Evidence:** [New York State Education Department closure record](https://www.nysed.gov/college-university-evaluation/closures-degree-granting-institutions)

The institution leaves the 2024 analytic universe after reporting 115 U.S. nonresident students in 2023. New York State Education Department records The College of Saint Rose as closed on December 31, 2024, with academic instruction ending earlier in 2024. The universe exit is therefore an expected structural event rather than an unexplained data disappearance.

## Interpretation boundary

IPEDS U.S. nonresident status is a federal reporting category, not a complete measure of international, immigrant-origin, undocumented, DACA, or foreign-born students. The analysis supports enrollment monitoring and publication QA, not causal claims about immigration policy. State totals reflect institution location, and institution structures or reporting practices can change over time.

The project maintains `docs/POPULATION_CROSSWALK.md` to document which companion sources are appropriate for immigrant-origin, international, undocumented, high-school-pipeline, and refugee/asylee questions rather than treating those populations as interchangeable.

## Methods and evidence

The series uses official NCES/IPEDS Fall Enrollment and institutional directory files for 2015-2024. Source archives are hashed and logged, required variables and aggregation labels are audited across years, state/control/student-level totals reconcile to the national series, and **24/24** independent NCES Digest consistency checks pass. The newest release also receives institution-level reason-coded triage and evidence-backed manual disposition before institution-specific claims are promoted into narrative.

See `docs/METHODOLOGY.md`, `docs/POPULATION_CROSSWALK.md`, `docs/LATEST_UPDATE_REVIEW.md`, and `docs/QA_RESOLUTION_LOG.md` for full definitions and review detail.
