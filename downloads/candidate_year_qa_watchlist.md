# Candidate-Year QA Carry-Forward Watchlist

This pre-release watchlist combines the current 2023-2024 high/medium institution QA queue with the already-available 2025 candidate directory structural review. It contains **226 unique UNITIDs** and is intended to make the next full-package QA pass faster without inventing candidate-year enrollment values.

## Reconciliation

- **Current high-priority QA rows:** 27
- **Current medium-priority QA rows:** 50
- **Candidate directory structural-change rows:** 154
- **Current high + candidate directory overlaps:** 0
- **Current medium + candidate directory overlaps:** 5
- **Unique union:** 27 + 50 + 154 - 5 = **226**

The existing high-priority evidence review remains **11 safe with context / 16 held for confirmation**, and the medium-priority evidence review remains **5 safe with context / 45 held**, for the current 2024 publication. Those decisions are carried as context only and must be revalidated after the next complete Fall Enrollment build; they are not automatically inherited by 2025.

## Medium-priority rows that also changed in the candidate directory

Five current medium-priority rows also have a candidate directory structural signal. Together they represent **2,443 current-year U.S. nonresident students**. This overlap changes review order, not publication status.

| Institution | State | 2023-2024 change | Current publication class | Candidate directory signal | 2024 nonresident |
| --- | --- | ---: | --- | --- | ---: |
| Lindsey Wilson College | KY | +590 | Hold for confirmation | Shared attribute change: institution_name_changed | 2,027 |
| FIDM-Fashion Institute of Design & Merchandising | CA | -166 | Hold for confirmation | Left directory eligible: title_iv_first_look_status_lost | 128 |
| Humphreys University-Stockton and Modesto Campuses | CA | +116 | Hold for confirmation | Shared attribute change: institution_name_changed | 288 |
| City College-Hollywood | FL | 0 | Hold for confirmation | Left directory eligible: title_iv_first_look_status_lost | 0 |
| City College-Altamonte Springs | FL | 0 | Hold for confirmation | Left directory eligible: title_iv_first_look_status_lost | 0 |

## Current high-priority carry-forwards

The first ten rows below are ordered by absolute current latest-release change. Current publication classes are shown because they already have evidence-backed review, but the next-release action is still to revalidate rather than inherit the decision.

| Institution | State | 2023-2024 change | Current publication class |
| --- | --- | ---: | --- |
| University of the Cumberlands | KY | +4,616 | Hold for confirmation |
| Collin County Community College District | TX | +2,256 | Hold for confirmation |
| Broward College | FL | +2,005 | Hold for confirmation |
| Miami Dade College | FL | +1,458 | Hold for confirmation |
| Trine University-Regional/Non-Traditional Campuses | IN | +1,441 | Safe with context |
| Campbellsville University | KY | -1,358 | Safe with context |
| The University of Texas at Dallas | TX | -1,225 | Hold for confirmation |
| St. Francis College | NY | +1,220 | Safe with context |
| Community College of Rhode Island | RI | +1,176 | Hold for confirmation |
| University of North Texas | TX | -1,052 | Safe with context |

## Candidate-directory-only rows with the largest current exposure

There are **149** candidate structural-change rows that are not in the current high/medium queue. Their current-year U.S. nonresident exposure sums to **9,326**. Exposure only determines display order here; it is not a risk score or a forecast.

| Institution | Current state | Candidate signal | 2024 nonresident | Candidate identity/state/control |
| --- | --- | --- | ---: | --- |
| Houston Community College | TX | Shared attribute change: institution_name_changed | 4,670 | Houston City College; TX; Public |
| Grand Canyon University | AZ | Shared attribute change: control_changed | 967 | Grand Canyon University; AZ; Private nonprofit |
| MCPHS University | MA | Shared attribute change: institution_name_changed | 866 | Massachusetts College of Pharmacy and Health Sciences; MA; Private nonprofit |
| Shoreline Community College | WA | Shared attribute change: institution_name_changed | 615 | Shoreline College; WA; Public |
| Hillsborough Community College | FL | Shared attribute change: institution_name_changed | 409 | Hillsborough College; FL; Public |
| Indiana University of Pennsylvania-Main Campus | PA | Shared attribute change: institution_name_changed | 373 | Indiana University of Pennsylvania; PA; Public |
| Mississippi College | MS | Shared attribute change: institution_name_changed | 160 | Mississippi Christian University; MS; Private nonprofit |
| University of Houston-Victoria | TX | Shared attribute change: institution_name_changed | 145 | Texas A&M University-Victoria; TX; Public |
| Siena College | NY | Shared attribute change: institution_name_changed | 122 | Siena University; NY; Private nonprofit |
| Salus University | PA | Left directory eligible: title_iv_first_look_status_lost | 106 | Salus University; PA; Private nonprofit |

## Review order and boundary

The CSV uses the existing review signals rather than inventing a new risk score. Current high-priority rows come first, then current medium rows that also have a candidate directory change, then the remaining current medium rows, then candidate-directory-only rows ordered by current-year U.S. nonresident exposure. UNITID breaks ties.

**Boundary:** Carry-forward QA signal only; do not infer 2025 enrollment movement, institutional opening/closure, or continued publication eligibility from this row. Reassess against the full 2025 Fall Enrollment package.

When the complete candidate-year package arrives, every watchlist row should be reconciled against the full Fall Enrollment join before any institution-specific next-release narrative is published. A current `safe_with_context` decision is not a standing approval for a future release.
