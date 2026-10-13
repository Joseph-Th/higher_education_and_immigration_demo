# QA Resolution Log

The automated annual review queue is deliberately conservative: it flags large or unusual changes for analyst attention. This log records a manually reviewed sample of the current high-priority queue and the publication decision that follows from the evidence review. The required sample covers the ten highest-impact high-priority records in the current deterministic queue; additional cases may be included when they demonstrate a distinct structural issue.

A disposition never overwrites IPEDS. `safe_with_context` means outside evidence is strong enough to discuss the direction or structural event with appropriate caveats. `hold_for_confirmation` means the official IPEDS value remains in aggregate calculations but should not drive an institution-specific claim until a directly comparable source is obtained.

## Review summary

- **11** high-priority records manually reviewed.
- **2** are safe to discuss with explicit context.
- **9** remain held for institution-specific interpretation.
- Three representative cases are promoted into the public research memo: an unresolved anomaly, a corroborated movement, and a confirmed structural change.
- Latest review date: **2026-10-13**.

## Dispositions

| Institution | State | Change | Disposition | Publication decision | Evidence |
| --- | --- | ---: | --- | --- | --- |
| University of the Cumberlands | KY | +4,616 | unresolved_discontinuity | hold_for_confirmation | [University of the Cumberlands international-student information](https://www.ucumberlands.edu/admissions/international-students) |
| Collin County Community College District | TX | +2,256 | unresolved_large_change | hold_for_confirmation | [Collin College International Student Office](https://www.collin.edu/international-student/) |
| Broward College | FL | +2,005 | context_support_only | hold_for_confirmation | [Broward College international-student services](https://www.broward.edu/international/students/) |
| Miami Dade College | FL | +1,458 | context_support_only | hold_for_confirmation | [Miami Dade College International Students](https://www.mdc.edu/internationalstudents/) |
| Trine University-Regional/Non-Traditional Campuses | IN | +1,441 | corroborated_direction | safe_with_context | [Trine University fall 2024 record-enrollment announcement](https://www.trine.edu/news/2024/record-enrollment.aspx) |
| Campbellsville University | KY | -1,358 | corroborated_baseline | hold_for_confirmation | [Campbellsville University President's Report 2024](https://www.campbellsville.edu/alumni/alumni-media/CU%20Presidents%20Report%202024_webfile.pdf) |
| The University of Texas at Dallas | TX | -1,225 | external_scope_mismatch | hold_for_confirmation | [UT Dallas international recruitment report](https://news.utdallas.edu/campus-community/new-office-in-india-2023/) |
| St. Francis College | NY | +1,220 | context_support_only | hold_for_confirmation | [St. Francis College history and mission](https://www.sfc.edu/why-sfc/history-and-mission) |
| Community College of Rhode Island | RI | +1,176 | unresolved_discontinuity | hold_for_confirmation | [Community College of Rhode Island 2024 international-student information](https://www.ccri.edu/onestop/admissions/international/inappak.pdf) |
| University of North Texas | TX | -1,052 | external_scope_mismatch | hold_for_confirmation | [University of North Texas International Student Services](https://international.unt.edu/international-students/) |
| The College of Saint Rose | NY | -115 | expected_structural_change | safe_with_context | [New York State Education Department closure record](https://www.nysed.gov/college-university-evaluation/closures-degree-granting-institutions) |

## Analyst notes

### University of the Cumberlands (UNITID 156541)

**Automated trigger:** absolute change is at least 1,000 students; zero/nonzero discontinuity conflicts with recent history.

IPEDS reports 4,226 U.S. nonresident students in 2022, zero in 2023, and 4,616 in 2024, with all three values marked reported. The institution's own materials show an active international-student program, but they do not provide a directly comparable 2023 count. Retain the official IPEDS value in aggregates, flag the discontinuity, and do not use the 2023 zero in institution-specific narrative without direct source confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_discontinuity` · **Reviewed:** 2026-10-13.

### Collin County Community College District (UNITID 247834)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 433 to 2,689 U.S. nonresident students in one year. Collin College clearly operates an F-1/international-student program, but the reviewed public page does not provide a directly comparable annual headcount. Preserve the source value and hold institution-specific interpretation pending confirmation from a fact book, institutional research office, or revised IPEDS release.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_large_change` · **Reviewed:** 2026-10-13.

### Broward College (UNITID 132709)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 50% from a baseline of 100+.

IPEDS rises from 3,369 to 5,374 U.S. nonresident students. Broward reports serving students from more than 150 countries and maintains a substantial F-1 program, which makes a large international population plausible, but the reviewed page does not independently reconcile the 2024 count. Retain the value in aggregates and avoid attributing the Florida increase to Broward specifically without a comparable annual source.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Miami Dade College (UNITID 135717)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 25% from a baseline of 100+.

IPEDS rises from 2,947 to 4,405 U.S. nonresident students while total fall enrollment also changes sharply. MDC maintains college-wide international admissions and advising, but the reviewed public materials do not provide an annual population matching the IPEDS definition. Keep the source value in aggregates and treat the institution-level movement as unresolved for narrative purposes.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Trine University-Regional/Non-Traditional Campuses (UNITID 414878)

**Automated trigger:** absolute change is at least 1,000 students.

IPEDS reports 7,772 to 9,213 U.S. nonresident students and 8,230 to 9,868 total fall enrollment. Trine independently reported that fall 2024 enrollment across its locations and platforms was expected to rise about 18% from fall 2023, with substantial growth in graduate/hybrid programs. This corroborates the direction and scale of growth, though the institution-wide announcement is not an exact IPEDS U.S. nonresident reconciliation.

**Decision:** `safe_with_context` · **Disposition:** `corroborated_direction` · **Reviewed:** 2026-10-13.

### Campbellsville University (UNITID 156365)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 25% from a baseline of 100+.

IPEDS reports 4,408 U.S. nonresident students in fall 2023 and 3,050 in fall 2024. Campbellsville's 2023 institutional materials report 13,049 total students and 34.5% international, broadly consistent with a large international population near the IPEDS baseline. No reviewed institutional source directly reconciles the 2024 decline, so retain the source data but do not infer a cause.

**Decision:** `hold_for_confirmation` · **Disposition:** `corroborated_baseline` · **Reviewed:** 2026-10-13.

### The University of Texas at Dallas (UNITID 228787)

**Automated trigger:** absolute change is at least 1,000 students.

IPEDS falls from 6,828 to 5,603 U.S. nonresident students. UT Dallas has published larger 'international student' counts that use different timing and/or scope, including students in other statuses and programs. Those figures are useful context but are not a valid numerical benchmark for EFNRALT. Retain the IPEDS series and avoid treating broader institutional international counts as an exact validation source.

**Decision:** `hold_for_confirmation` · **Disposition:** `external_scope_mismatch` · **Reviewed:** 2026-10-13.

### St. Francis College (UNITID 195173)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 50% from a baseline of 100+.

IPEDS rises from 1,791 to 3,011 U.S. nonresident students, almost entirely at the graduate level. St. Francis documents its 2022 campus relocation as part of a repositioning for future success and growth and describes a current student body representing more than 70 countries. That supports a broader growth/international context but does not provide a directly comparable annual IPEDS count, so the exact increase remains an analyst-review item.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Community College of Rhode Island (UNITID 217475)

**Automated trigger:** absolute change is at least 1,000 students.

IPEDS jumps from 12 to 1,188 U.S. nonresident students after years of values between 12 and 18. CCRI's 2024 international-student materials confirm an active F-1 admissions pathway but do not support an increase of this magnitude. Because the 2024 source value is marked reported rather than imputed, preserve it in the official series while withholding institution-specific interpretation pending direct confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_discontinuity` · **Reviewed:** 2026-10-13.

### University of North Texas (UNITID 227216)

**Automated trigger:** absolute change is at least 1,000 students.

IPEDS declines from 8,827 to 7,775 U.S. nonresident students. UNT public pages cite international-student and scholar populations using broader operational definitions, and current pages report figures that are not directly comparable to the IPEDS fall EFNRALT universe. The decline is retained as reported, but outside headcounts should not be used to reconcile it without a definitions crosswalk.

**Decision:** `hold_for_confirmation` · **Disposition:** `external_scope_mismatch` · **Reviewed:** 2026-10-13.

### The College of Saint Rose (UNITID 195234)

**Automated trigger:** analytic-universe membership changed; universe entry/exit involves at least 100 students; percentage change is at least 100% from a baseline of 100+.

The institution leaves the 2024 analytic universe after reporting 115 U.S. nonresident students in 2023. New York State Education Department records The College of Saint Rose as closed on December 31, 2024, with academic instruction ending earlier in 2024. The universe exit is therefore an expected structural event rather than an unexplained data disappearance.

**Decision:** `safe_with_context` · **Disposition:** `expected_structural_change` · **Reviewed:** 2026-10-13.

## Review rule

External institutional counts are not assumed to equal IPEDS `EFNRALT`. Terms such as *international student*, *international student and scholar*, F-1 headcount, SEVIS active record, and students from other countries can use different populations, reference dates, or inclusion rules. Outside sources therefore corroborate context or direction only when their scope supports that use.
