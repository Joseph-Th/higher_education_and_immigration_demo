# QA Resolution Log

The automated annual review queue is deliberately conservative: it flags large or unusual changes for analyst attention. This log records the evidence-backed publication decision for every record in the current high-priority queue. The review layer does not change IPEDS values; it determines whether an institution-specific interpretation is supportable.

A disposition never overwrites IPEDS. `safe_with_context` means outside evidence is strong enough to discuss the direction or structural event with appropriate caveats. `hold_for_confirmation` means the official IPEDS value remains in aggregate calculations but should not drive an institution-specific claim until a directly comparable source is obtained.

## Review summary

- **27/27** high-priority records manually reviewed (**100% coverage**).
- **6** are safe to discuss with explicit context.
- **21** remain held for institution-specific interpretation.
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
| Webster University | MO | +1,020 | corroborated_external_count | safe_with_context | [Webster University November 2024 international-enrollment report](https://news.webster.edu/2024/webster_ranked_for_international_students_2024.php) |
| Sofia University | CA | +930 | unresolved_discontinuity | hold_for_confirmation | [Sofia University F-1 International Students](https://www.sofia.edu/admissions/international-students-2/) |
| Avila University | MO | +850 | corroborated_direction | safe_with_context | [Avila University reflection on Fall 2024 international recruitment](https://www.avila.edu/2025/07/29/three-years-at-avila-reflections-on-leadership-and-transformation-3/) |
| Southeastern University | FL | +706 | context_support_only | hold_for_confirmation | [Southeastern University Fall 2024 record-enrollment announcement](https://seu.edu/news/admission/a-record-breaking-year-in-university-enrollment/) |
| Belhaven University | MS | +470 | context_support_only | hold_for_confirmation | [Belhaven University international programs](https://www.belhaven.edu/international/) |
| Louisiana Tech University | LA | +342 | context_support_only | hold_for_confirmation | [Louisiana Tech international undergraduate admissions](https://www.latech.edu/student-life/international-affairs/undergaduate-admissions.php) |
| Cumberland University | TN | +306 | context_support_only | hold_for_confirmation | [Cumberland University International Student Services](https://admissions.cumberland.edu/portal/international-student) |
| Oakton College | IL | +299 | unresolved_discontinuity | hold_for_confirmation | [Oakton College international student admissions](https://www.oakton.edu/admissions/apply-to-oakton/international-student/) |
| Polk State College | FL | +288 | context_support_only | hold_for_confirmation | [Polk State College international and visa students](https://www.polk.edu/admission-aid/international-students/) |
| Norfolk State University | VA | +278 | context_support_only | hold_for_confirmation | [Norfolk State University international student services](https://www.nsu.edu/international) |
| Grambling State University | LA | +264 | corroborated_external_count | safe_with_context | [Grambling State University campus overview and enrollment snapshot](https://www.gram.edu/aboutus/campusoverview.php) |
| Oakwood University | AL | -192 | unresolved_status_change | hold_for_confirmation | [Oakwood University international applicant policy](https://catalog.oakwood.edu/admission-of-international-applicants) |
| Colorado State University Global | CO | +183 | external_scope_mismatch | hold_for_confirmation | [CSU Global international admissions definition](https://csuglobal.edu/admissions/international-students) |
| California Institute of Advanced Management | CA | +179 | context_support_only | hold_for_confirmation | [California Institute of Advanced Management international students](https://ciam.edu/international-students/) |
| Anderson University | SC | -176 | unresolved_discontinuity | hold_for_confirmation | [Anderson University South Carolina international student services](https://andersonuniversity.edu/academics/center-for-global-engagement/international-students/) |
| Reformed University | GA | -130 | confirmed_classification_change | safe_with_context | [Reformed University accreditation and authorization](https://www.runiv.edu/aboutru/main/accreditation) |
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

### Webster University (UNITID 179894)

**Automated trigger:** absolute change is at least 1,000 students; percentage change is at least 25% from a baseline of 100+.

IPEDS rises from 2,611 to 3,631 U.S. nonresident students, with most of the increase at the graduate level. Webster reported 3,542 students from 65 other countries across its three U.S. locations in November 2024 and said it had broken international-enrollment records for two consecutive years. The institutional count uses a different reference date and population definition, but it independently corroborates the direction and approximate scale of the IPEDS movement.

**Decision:** `safe_with_context` · **Disposition:** `corroborated_external_count` · **Reviewed:** 2026-10-13.

### Sofia University (UNITID 110778)

**Automated trigger:** absolute change is at least 500 students; zero/nonzero discontinuity conflicts with recent history.

IPEDS reports 1,330 U.S. nonresident students in 2020, zero in 2021-2023, and 930 in 2024, while total enrollment remains above 900 throughout. Sofia's official international-student page confirms authorization to enroll F-1 students, but it does not provide annual counts that explain the reported zeros or the 2024 return. Preserve the source series in aggregates and hold institution-specific interpretation pending a directly comparable institutional or revised IPEDS source.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_discontinuity` · **Reviewed:** 2026-10-13.

### Avila University (UNITID 176628)

**Automated trigger:** absolute change is at least 500 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 202 to 1,052 U.S. nonresident students from 2023 to 2024, almost entirely at the graduate level. Avila's president later described an 18-month international recruitment expansion leading into Fall 2024, including more than 4,000 I-20s issued to prospective international students and expectations that several hundred would enroll. That evidence supports a substantive international-growth direction, though it does not numerically reconcile the IPEDS count and should be cited with scope caveats.

**Decision:** `safe_with_context` · **Disposition:** `corroborated_direction` · **Reviewed:** 2026-10-13.

### Southeastern University (UNITID 137564)

**Automated trigger:** absolute change is at least 500 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 204 to 910 U.S. nonresident students while total fall enrollment increases from 10,400 to 11,510. Southeastern independently reported record Fall 2024 enrollment and an 11.7% overall increase, which supports a broad growth context, but the announcement does not provide a directly comparable U.S. nonresident count. Retain the IPEDS value in aggregates and avoid attributing the increase specifically to international recruitment without a matching institutional series.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Belhaven University (UNITID 175421)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 258 to 728 U.S. nonresident students, with graduate enrollment accounting for nearly all of the increase. Belhaven publicly describes international on-campus, hybrid graduate, and online programs and dedicated international support, making a growing international presence plausible, but the reviewed page does not provide a comparable Fall 2024 headcount. Keep the source value in aggregates and hold the exact institution-level movement for confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Louisiana Tech University (UNITID 159647)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 209 to 551 U.S. nonresident students, with undergraduate enrollment increasing from 124 to 351. Louisiana Tech maintains a dedicated Office of International Affairs and international admissions pathway, but the reviewed institutional material does not provide a Fall 2024 population matching the IPEDS definition. The direction is plausible context only; the exact change remains held for institution-specific publication.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Cumberland University (UNITID 219949)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 285 to 591 U.S. nonresident students, driven primarily by graduate enrollment increasing from 169 to 447. Cumberland operates dedicated F-1 international-student services, but the public service page does not report a directly comparable annual headcount. Preserve the official value and withhold an institution-specific growth claim pending a matching source.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Oakton College (UNITID 147800)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS reports zero U.S. nonresident students in 2020-2022, then 167 in 2023 and 466 in 2024. Oakton's official materials document an established F-1 international-admissions process, but they do not explain the earlier zeros or quantify the reported increase. The pattern is consistent with a possible reporting or classification discontinuity, so the official values remain in aggregates while institution-specific interpretation is held.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_discontinuity` · **Reviewed:** 2026-10-13.

### Polk State College (UNITID 136516)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 110 to 398 U.S. nonresident students in one year. Polk State documents authorization to enroll F-1, M-1, and other nonimmigrant students, confirming a relevant international-student population, but the page does not provide an annual count that reconciles the 2024 movement. Keep the source data in aggregates and hold the institution-level interpretation for direct confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Norfolk State University (UNITID 232937)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 127 to 405 U.S. nonresident students, almost entirely at the undergraduate level. Norfolk State documents dedicated international-student services and university-wide international initiatives, but the reviewed page provides no comparable annual headcount. The source value remains valid for aggregate accounting while the institution-specific increase stays held for confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Grambling State University (UNITID 159009)

**Automated trigger:** absolute change is at least 250 students; percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 105 to 369 U.S. nonresident students in 2024, primarily among undergraduates. Grambling's official Fall 2025 campus snapshot reports 360 international students, closely matching the scale of the 2024 IPEDS level one year later. The institutional measure uses a different year and may use a broader residency definition, so it corroborates scale and persistence rather than serving as an exact reconciliation.

**Decision:** `safe_with_context` · **Disposition:** `corroborated_external_count` · **Reviewed:** 2026-10-13.

### Oakwood University (UNITID 101912)

**Automated trigger:** percentage change is at least 100% from a baseline of 100+.

IPEDS falls from 192 U.S. nonresident students in 2023 to zero in 2024 while the source-status flag changes from reported (`R`) to zero (`Z`). Oakwood's current catalog continues to document authorization and procedures for nonimmigrant students. Because the external evidence does not support interpreting the 2024 zero as a verified disappearance of the international population, retain the aggregate source value but hold institution-specific narrative pending confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_status_change` · **Reviewed:** 2026-10-13.

### Colorado State University Global (UNITID 476975)

**Automated trigger:** percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 130 to 313 U.S. nonresident students. CSU Global defines international applicants in part by prior foreign education or native language and explicitly states that it is fully online and not SEVP-certified, so its public 'international student' concept is not a direct proxy for IPEDS U.S. nonresident status. The institutional page is useful for scope interpretation but cannot validate the numeric movement.

**Decision:** `hold_for_confirmation` · **Disposition:** `external_scope_mismatch` · **Reviewed:** 2026-10-13.

### California Institute of Advanced Management (UNITID 487649)

**Automated trigger:** percentage change is at least 100% from a baseline of 100+.

IPEDS rises from 159 to 338 U.S. nonresident graduate students while total enrollment rises from 163 to 344. CIAM states that it is approved by SEVP to enroll nonimmigrant students in its MBA program, making a very high international share plausible, but the public page does not provide a comparable Fall 2024 count. Retain the source values and hold the exact annual increase for confirmation.

**Decision:** `hold_for_confirmation` · **Disposition:** `context_support_only` · **Reviewed:** 2026-10-13.

### Anderson University (UNITID 217633)

**Automated trigger:** percentage change is at least 100% from a baseline of 100+.

IPEDS reports zero U.S. nonresident students in 2022, 176 in 2023, and zero again in 2024, with the 2023 and 2024 values both marked reported. Anderson University maintains active international undergraduate and graduate support, so the alternating zero/nonzero pattern cannot be treated as a straightforward disappearance of international students. Preserve the official series in aggregates and hold institution-specific interpretation pending a directly comparable source.

**Decision:** `hold_for_confirmation` · **Disposition:** `unresolved_discontinuity` · **Reviewed:** 2026-10-13.

### Reformed University (UNITID 490230)

**Automated trigger:** analytic-universe membership changed; universe entry/exit involves at least 100 students; percentage change is at least 100% from a baseline of 100+.

Reformed University reports 130 U.S. nonresident students in 2023 and then leaves the project's 2024 analytic universe. The official IPEDS directory record remains active and degree-granting in 2024 (`CYACTIVE=1`, `DEGGRANT=1`) but changes `PSET4FLG` from 1 to 2, which places it outside the project's First Look/Digest universe rule. Reformed University's current accreditation page independently confirms that the institution remains active and authorized to enroll international students. The exit is therefore a confirmed analytic-classification change, not a campus closure.

**Decision:** `safe_with_context` · **Disposition:** `confirmed_classification_change` · **Reviewed:** 2026-10-13.

### The College of Saint Rose (UNITID 195234)

**Automated trigger:** analytic-universe membership changed; universe entry/exit involves at least 100 students; percentage change is at least 100% from a baseline of 100+.

The institution leaves the 2024 analytic universe after reporting 115 U.S. nonresident students in 2023. New York State Education Department records The College of Saint Rose as closed on December 31, 2024, with academic instruction ending earlier in 2024. The universe exit is therefore an expected structural event rather than an unexplained data disappearance.

**Decision:** `safe_with_context` · **Disposition:** `expected_structural_change` · **Reviewed:** 2026-10-13.

## Review rule

External institutional counts are not assumed to equal IPEDS `EFNRALT`. Terms such as *international student*, *international student and scholar*, F-1 headcount, SEVIS active record, and students from other countries can use different populations, reference dates, or inclusion rules. Outside sources therefore corroborate context or direction only when their scope supports that use.
