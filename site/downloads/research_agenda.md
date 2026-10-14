# Research Agenda and Data-Needs Register

This register turns findings, QA observations, source limitations, and recurring product needs into explicit research questions. It separates questions answerable with the current IPEDS pipeline from questions that require population-specific or partner data.

## Portfolio priorities

| ID | Priority | Research question | Current IPEDS fit | Status |
| --- | --- | --- | --- | --- |
| R01 | High | Does the 2024 undergraduate-led increase persist in the next Fall Enrollment release? | High | Monitor next release |
| R02 | High | Why have some states recovered above 2019 while others remain below? | High | Implemented in state recovery analysis |
| R04 | High | How do IPEDS U.S. nonresident trends compare with undocumented and immigrant-origin student estimates? | None | Implemented as bounded national population trend comparison |
| R05 | High | Which large institution-level annual changes reflect substantive movement versus reporting or classification discontinuity? | High | Implemented in complete high-priority QA review |
| R03 | Medium | Is private nonprofit growth broad-based or concentrated among a small set of institutions? | High | Implemented in private nonprofit growth analysis |
| R06 | Medium | What does the undocumented high-school graduate pipeline imply for higher-education access questions? | None | Requires partner/population data |
| R07 | Medium | Which external source updates should trigger Portal refreshes or new research products? | Support | Ongoing monitoring |

## Detailed research cards

### High priority

#### R01 · Does the 2024 undergraduate-led increase persist in the next Fall Enrollment release?

- **Evidence trigger:** 2023-2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment declined by 2,053.
- **Current IPEDS fit:** High
- **Additional data needed:** Next NCES/IPEDS Fall Enrollment release
- **Proposed method:** Repeat the national and state student-level decomposition; compare direction and contribution to change with 2024.
- **Proposed output:** Annual update brief
- **Decision rule:** Elevate to a multi-year finding only if the next release confirms that undergraduate growth remains a material contributor rather than a one-year reversal.
- **Status:** Monitor next release

#### R02 · Why have some states recovered above 2019 while others remain below?

- **Evidence trigger:** 33 states/DC are at or above 2019 U.S. nonresident enrollment and 18 remain below.
- **Current IPEDS fit:** High
- **Additional data needed:** Current institution-level IPEDS files are sufficient for first-pass decomposition
- **Proposed method:** Decompose state change by institution continuity, institutional control, and undergraduate/graduate level; inspect concentration among leading contributors.
- **Proposed output:** State recovery decomposition brief
- **Decision rule:** Prioritize states with the largest absolute gains and shortfalls, then test whether change is broad-based or concentrated in a few institutions.
- **Status:** Implemented in state recovery analysis

#### R04 · How do IPEDS U.S. nonresident trends compare with undocumented and immigrant-origin student estimates?

- **Evidence trigger:** IPEDS U.S. nonresident is explicitly not a measure of undocumented, DACA, immigrant-origin, or all foreign-born students.
- **Current IPEDS fit:** None
- **Additional data needed:** Current published national estimates support a bounded comparison; method-equivalent microdata and aligned geography would be required for deeper cross-series or state analysis.
- **Proposed method:** Keep the populations as separate series; compare change only within method-compatible source segments; use same-year national levels for scale context without adding, subtracting, or treating one population as a proxy for another.
- **Proposed output:** National population trend comparison note
- **Decision rule:** Direct arithmetic is permitted only within a compatible population/source segment. Cross-population levels are contextual and not addable; state comparison remains held when geography or denominator definitions differ.
- **Status:** Implemented as bounded national population trend comparison

#### R05 · Which large institution-level annual changes reflect substantive movement versus reporting or classification discontinuity?

- **Evidence trigger:** The 2023-2024 review queue contains 27 high-priority and 50 medium-priority institution records.
- **Current IPEDS fit:** High
- **Additional data needed:** Current and revised IPEDS files plus institution-level contextual documentation when needed
- **Proposed method:** Resolve every high-priority review item using recent history, imputation/status fields, universe membership, source-vintage checks, and institution-level evidence; retain an explicit publication disposition for each record.
- **Proposed output:** Complete high-priority QA review and release memo
- **Decision rule:** Institution-specific movements enter public narrative only after high-priority flags are resolved or explicitly caveated; aggregate source values are never rewritten by the review layer.
- **Status:** Implemented in complete high-priority QA review

### Medium priority

#### R03 · Is private nonprofit growth broad-based or concentrated among a small set of institutions?

- **Evidence trigger:** Private nonprofit institutions added 82,825 U.S. nonresident students from 2015 to 2024, driven primarily by graduate enrollment.
- **Current IPEDS fit:** High
- **Additional data needed:** Current institution-level IPEDS files
- **Proposed method:** Rank institution contributions within private nonprofits; calculate concentration against gross positive movement; separate undergraduate/graduate change and retain current institution QA gates.
- **Proposed output:** Private nonprofit growth concentration note
- **Decision rule:** Classify the shift as concentrated if the top 10 institutions account for at least 50% of gross positive movement; otherwise classify it as broadly distributed beyond the top 10.
- **Status:** Implemented in private nonprofit growth analysis

#### R06 · What does the undocumented high-school graduate pipeline imply for higher-education access questions?

- **Evidence trigger:** The target organization's recurring research includes undocumented high-school graduate estimates alongside higher-education enrollment estimates.
- **Current IPEDS fit:** None
- **Additional data needed:** Population-specific high-school graduate estimates and undocumented higher-education estimates with state coverage and methods
- **Proposed method:** Compare geographic patterns and scale using an ecological state-level design; document that the datasets do not track the same individuals.
- **Proposed output:** Pipeline research brief
- **Decision rule:** Proceed only for geographies and years with compatible estimates, and avoid causal or individual-transition claims.
- **Status:** Requires partner/population data

#### R07 · Which external source updates should trigger Portal refreshes or new research products?

- **Evidence trigger:** The maintained Research Library spans primary data, release schedules, methodology, benchmarks, and recurring Portal research products.
- **Current IPEDS fit:** Support
- **Additional data needed:** Current source release dates, revised-file notices, and partner delivery schedules
- **Proposed method:** Use the data calendar and Research Library to classify changes as routine refresh, methodology review, or potential new research question.
- **Proposed output:** Quarterly source/data-needs review
- **Decision rule:** Escalate a source change when it changes definitions, population coverage, release vintage, or a published conclusion rather than only the file date.
- **Status:** Ongoing monitoring

## Governance principles

1. A new question should name the population, geography, period, denominator, and decision it is intended to support before analysis begins.
2. Source limitations are part of the research question. A convenient dataset is not a reason to collapse distinct populations into one measure.
3. Questions triggered by apparent anomalies enter QA review before they become public findings.
4. Research requiring partner data should begin with a definitions/methodology crosswalk and release-vintage review.
5. The agenda should be re-reviewed after each annual release because a confirmed pattern, revised source, or resolved anomaly can change priority.
