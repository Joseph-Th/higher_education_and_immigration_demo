# Medium-Priority IPEDS Category Countermovement Diagnostic

This diagnostic adds the same internal source-data arithmetic check used for high-priority QA to all **50 current medium-priority 2023-2024 records**. It remains separate from both the reason-derived routing layer and the evidence-backed publication decision.

**Interpretation boundary:** countermovement is a review-prioritization signal only. It is not a second risk score, does not prove miscoding or reclassification, does not correct IPEDS, and cannot clear or hold an institution-specific claim by itself.

## Summary

- **47** continuing medium-priority rows have a two-year category comparison under the diagnostic R/Z endpoint-status rule.
- **18** have opposite-category movement at least as large as the absolute U.S. nonresident change.
- **9** have opposite-category movement between 50% and 100% of the U.S. nonresident change.
- **20** have opposite-category movement below 50% of the U.S. nonresident change.
- **2** continuing rows are retained but receive no countermovement ratio because an endpoint uses a status outside R/Z.
- **1** analytic-universe change is retained for complete queue coverage but not forced into a two-year composition comparison.

## Strongest internal countermovement signals

| Institution | Route | NR change | NR status | Total change | Opposite-category movement | Ratio | Largest opposite category | Category status | Publication gate |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| Ana G. Mendez University | Percentage Movement | -76 | R→R | -4 | 1,290 | 1697.4% | Hispanic / Latino (+1,269) | R→R | hold_for_confirmation |
| Walden University | Percentage Movement | -396 | R→R | +5,218 | 5,630 | 1421.7% | Black / African American (+2,784) | R→R | hold_for_confirmation |
| Barton County Community College | Percentage Movement | -155 | R→R | +699 | 862 | 556.1% | White (+388) | R→R | safe_with_context |
| Chaffey College | Absolute And Percentage | -611 | R→R | +1,828 | 2,494 | 408.2% | Hispanic / Latino (+1,745) | R→R | safe_with_context |
| University of Lynchburg | Percentage Movement | +91 | R→R | -276 | 367 | 403.3% | White (-215) | R→R | safe_with_context |
| Northeastern University | Absolute Movement | -616 | R→R | +1,394 | 2,019 | 327.8% | Asian (+667) | R→R | safe_with_context |
| Boston University | Absolute Movement | -558 | R→R | +1,113 | 1,672 | 299.6% | Race / ethnicity unknown (+551) | R→R | safe_with_context |
| Pikes Peak State College | Percentage Movement | -104 | R→R | +168 | 298 | 286.5% | Hispanic / Latino (+179) | R→R | safe_with_context |
| The University of Texas at Arlington | Absolute Movement | -846 | R→R | +964 | 1,959 | 231.6% | Hispanic / Latino (+823) | R→R | safe_with_context |
| America Evangelical University | Percentage Movement | -92 | R→R | +100 | 210 | 228.3% | Race / ethnicity unknown (+147) | Z→R | hold_for_confirmation |
| Vincennes University | Percentage Movement | +78 | R→R | +1,357 | 170 | 217.9% | Race / ethnicity unknown (-166) | R→R | safe_with_context |
| Fort Hays State University | Percentage Movement | -266 | R→R | +35 | 547 | 205.6% | Hispanic / Latino (+202) | R→R | safe_with_context |
| University of California-Berkeley | Absolute Movement | -546 | R→R | +183 | 733 | 134.2% | Asian (+251) | R→R | safe_with_context |
| New Mexico Highlands University | Percentage Movement | -81 | R→R | -110 | 104 | 128.4% | Race / ethnicity unknown (+92) | R→R | safe_with_context |
| Northeastern University Oakland | Percentage Movement | +80 | R→R | -18 | 100 | 125.0% | Hispanic / Latino (-40) | R→R | hold_for_confirmation |

## Complete medium-priority diagnostic

| Order | Institution | State | Route | NR change | NR status | Countermovement | Ratio | Signal | Publication gate |
| ---: | --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |
| 1 | New Orleans Baptist Theological Seminary | LA | Structural Or Reporting | +129 | — | — | — | Analytic-universe change; category comparison not used | safe_with_context |
| 2 | City College-Hollywood | FL | Structural Or Reporting | +0 | R→P | — | — | Endpoint source status is not comparable for countermovement | safe_with_context |
| 3 | City College-Altamonte Springs | FL | Structural Or Reporting | +0 | R→P | — | — | Endpoint source status is not comparable for countermovement | safe_with_context |
| 4 | Indiana Wesleyan University-National & Global | IN | Absolute And Percentage | +855 | R→R | 48 | 5.6% | Countermovement below half of the nonresident change | safe_with_context |
| 5 | Valencia College | FL | Absolute And Percentage | +692 | R→R | 146 | 21.1% | Countermovement below half of the nonresident change | safe_with_context |
| 6 | Dallas College | TX | Absolute And Percentage | +628 | R→R | 14 | 2.2% | Countermovement below half of the nonresident change | safe_with_context |
| 7 | Chaffey College | CA | Absolute And Percentage | -611 | R→R | 2,494 | 408.2% | Countermovement at least as large as the nonresident change | safe_with_context |
| 8 | Lindsey Wilson College | KY | Absolute And Percentage | +590 | R→R | 491 | 83.2% | Countermovement at least half as large as the nonresident change | hold_for_confirmation |
| 9 | Texas State University | TX | Absolute And Percentage | +558 | R→R | 358 | 64.2% | Countermovement at least half as large as the nonresident change | safe_with_context |
| 10 | Sacred Heart University | CT | Absolute And Percentage | -508 | R→R | 360 | 70.9% | Countermovement at least half as large as the nonresident change | hold_for_confirmation |
| 11 | Indiana University-Indianapolis | IN | Absolute And Percentage | -504 | R→R | 4 | 0.8% | Countermovement below half of the nonresident change | safe_with_context |
| 12 | The University of Texas at Arlington | TX | Absolute Movement | -846 | R→R | 1,959 | 231.6% | Countermovement at least as large as the nonresident change | safe_with_context |
| 13 | Georgia Institute of Technology-Main Campus | GA | Absolute Movement | +835 | R→R | 1 | 0.1% | Countermovement below half of the nonresident change | safe_with_context |
| 14 | University of Illinois Urbana-Champaign | IL | Absolute Movement | +775 | R→R | 4 | 0.5% | Countermovement below half of the nonresident change | safe_with_context |
| 15 | Syracuse University | NY | Absolute Movement | -760 | R→R | 405 | 53.3% | Countermovement at least half as large as the nonresident change | safe_with_context |
| 16 | University of Colorado Boulder | CO | Absolute Movement | -755 | R→R | 32 | 4.2% | Countermovement below half of the nonresident change | safe_with_context |
| 17 | Northeastern University | MA | Absolute Movement | -616 | R→R | 2,019 | 327.8% | Countermovement at least as large as the nonresident change | safe_with_context |
| 18 | Stevens Institute of Technology | NJ | Absolute Movement | -592 | R→R | 350 | 59.1% | Countermovement at least half as large as the nonresident change | safe_with_context |
| 19 | Purdue University-Main Campus | IN | Absolute Movement | +580 | R→R | 0 | 0.0% | Countermovement below half of the nonresident change | safe_with_context |
| 20 | University of New Haven | CT | Absolute Movement | -574 | R→R | 96 | 16.7% | Countermovement below half of the nonresident change | safe_with_context |
| 21 | Boston University | MA | Absolute Movement | -558 | R→R | 1,672 | 299.6% | Countermovement at least as large as the nonresident change | safe_with_context |
| 22 | University of California-Berkeley | CA | Absolute Movement | -546 | R→R | 733 | 134.2% | Countermovement at least as large as the nonresident change | safe_with_context |
| 23 | Midwestern Baptist Theological Seminary | MO | Percentage Movement | -458 | R→R | 564 | 123.1% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 24 | Walden University | MN | Percentage Movement | -396 | R→R | 5,630 | 1421.7% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 25 | Weber State University | UT | Percentage Movement | +373 | R→R | 327 | 87.7% | Countermovement at least half as large as the nonresident change | safe_with_context |
| 26 | Fort Hays State University | KS | Percentage Movement | -266 | R→R | 547 | 205.6% | Countermovement at least as large as the nonresident change | safe_with_context |
| 27 | Marywood University | PA | Percentage Movement | -260 | R→R | 66 | 25.4% | Countermovement below half of the nonresident change | safe_with_context |
| 28 | Dominican University of California | CA | Percentage Movement | -249 | R→R | 263 | 105.6% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 29 | National Louis University | IL | Percentage Movement | +218 | R→R | 18 | 8.3% | Countermovement below half of the nonresident change | hold_for_confirmation |
| 30 | University of Rio Grande | OH | Percentage Movement | +181 | R→R | 154 | 85.1% | Countermovement at least half as large as the nonresident change | hold_for_confirmation |
| 31 | Union Commonwealth University | KY | Percentage Movement | +179 | R→R | 76 | 42.5% | Countermovement below half of the nonresident change | safe_with_context |
| 32 | FIDM-Fashion Institute of Design & Merchandising | CA | Percentage Movement | -166 | R→R | 2 | 1.2% | Countermovement below half of the nonresident change | safe_with_context |
| 33 | Barton County Community College | KS | Percentage Movement | -155 | R→R | 862 | 556.1% | Countermovement at least as large as the nonresident change | safe_with_context |
| 34 | Saddleback College | CA | Percentage Movement | +152 | R→R | 0 | 0.0% | Countermovement below half of the nonresident change | safe_with_context |
| 35 | Durham Technical Community College | NC | Percentage Movement | +129 | R→R | 5 | 3.9% | Countermovement below half of the nonresident change | hold_for_confirmation |
| 36 | Prairie View A & M University | TX | Percentage Movement | +125 | R→R | 17 | 13.6% | Countermovement below half of the nonresident change | hold_for_confirmation |
| 37 | Humphreys University-Stockton and Modesto Campuses | CA | Percentage Movement | +116 | R→R | 23 | 19.8% | Countermovement below half of the nonresident change | safe_with_context |
| 38 | Austin Peay State University | TN | Percentage Movement | +111 | R→R | 27 | 24.3% | Countermovement below half of the nonresident change | hold_for_confirmation |
| 39 | Knox College | IL | Percentage Movement | +107 | R→R | 6 | 5.6% | Countermovement below half of the nonresident change | safe_with_context |
| 40 | Pikes Peak State College | CO | Percentage Movement | -104 | R→R | 298 | 286.5% | Countermovement at least as large as the nonresident change | safe_with_context |
| 41 | America Evangelical University | CA | Percentage Movement | -92 | R→R | 210 | 228.3% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 42 | University of Lynchburg | VA | Percentage Movement | +91 | R→R | 367 | 403.3% | Countermovement at least as large as the nonresident change | safe_with_context |
| 43 | Monroe Community College | NY | Percentage Movement | +83 | R→R | 99 | 119.3% | Countermovement at least as large as the nonresident change | safe_with_context |
| 44 | University of Maine at Presque Isle | ME | Percentage Movement | +81 | R→R | 1 | 1.2% | Countermovement below half of the nonresident change | hold_for_confirmation |
| 45 | New Mexico Highlands University | NM | Percentage Movement | -81 | R→R | 104 | 128.4% | Countermovement at least as large as the nonresident change | safe_with_context |
| 46 | Northeastern University Oakland | CA | Percentage Movement | +80 | R→R | 100 | 125.0% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 47 | Vincennes University | IN | Percentage Movement | +78 | R→R | 170 | 217.9% | Countermovement at least as large as the nonresident change | safe_with_context |
| 48 | Ana G. Mendez University | FL | Percentage Movement | -76 | R→R | 1,290 | 1697.4% | Countermovement at least as large as the nonresident change | hold_for_confirmation |
| 49 | Anna Maria College | MA | Percentage Movement | -68 | R→R | 40 | 58.8% | Countermovement at least half as large as the nonresident change | safe_with_context |
| 50 | Normandale Community College | MN | Percentage Movement | +60 | R→R | 31 | 51.7% | Countermovement at least half as large as the nonresident change | safe_with_context |

## Accounting and decision rule

For each continuing institution, both endpoint all-student IPEDS rows must reconcile `EFTOTLT` to the nine mutually exclusive race/ethnicity categories including `EFNRALT`, and the change identity must satisfy `total change = nonresident change + net change across all other categories`. A countermovement ratio is calculated only when every endpoint total/category status code is `R` (Reported) or `Z` (Implied zero). Other official status-coded values remain in the source arithmetic but are withheld from the ratio. The diagnostic copies the medium evidence-review publication class only to keep arithmetic and analyst evidence visible together.

A large ratio changes neither the medium-priority route nor the publication class. Institution-specific discussion still depends on the separate evidence review, and every current disposition must be revalidated after the next complete Fall Enrollment release.
