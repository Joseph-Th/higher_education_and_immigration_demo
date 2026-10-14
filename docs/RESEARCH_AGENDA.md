# Research Agenda and Data-Needs Register

This register turns findings, QA observations, source limitations, and recurring product needs into explicit research questions. It separates questions answerable with the current IPEDS pipeline from questions that require population-specific or partner data.

## Portfolio priorities

| ID | Priority | Research question | Current IPEDS fit | Status |
| --- | --- | --- | --- | --- |
| R01 | High | Does the 2024 undergraduate-led increase persist in the next Fall Enrollment release? | High | Baseline implemented; monitor next release |
| R02 | High | Why have some states recovered above 2019 while others remain below? | High | Implemented in state recovery analysis |
| R04 | High | How do IPEDS U.S. nonresident trends compare with undocumented and immigrant-origin student estimates? | None | Implemented as bounded national population trend comparison |
| R05 | High | Which large institution-level annual changes reflect substantive movement versus reporting or classification discontinuity? | High | Implemented in complete high-priority QA review |
| R03 | Medium | Is private nonprofit growth broad-based or concentrated among a small set of institutions? | High | Implemented in private nonprofit growth analysis |
| R06 | Medium | What does the undocumented high-school graduate pipeline imply for higher-education access questions? | None | Implemented as bounded 2023 state pipeline context |
| R07 | Medium | Which external source updates should trigger Portal refreshes or new research products? | Support | Implemented as source-update triage register |
| R08 | Medium | Which institution-level QA signals should carry forward into the next complete Fall Enrollment release? | Support | Implemented as candidate-year QA carry-forward watchlist |

## Detailed research cards

### High priority

#### R01 · Does the 2024 undergraduate-led increase persist in the next Fall Enrollment release?

- **Evidence trigger:** 2023-2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment declined by 2,053; undergraduate enrollment increased in 45 of 51 states/DC.
- **Current IPEDS fit:** High
- **Additional data needed:** Current IPEDS files establish a fixed 2023-2024 baseline; the next NCES/IPEDS Fall Enrollment release is required to test persistence.
- **Proposed method:** Preserve the 2023-2024 national/state/control/institution-continuity baseline; on the next complete release, repeat the student-level decomposition and compare national direction plus state breadth with the fixed baseline.
- **Proposed output:** Undergraduate shift baseline and next-release update
- **Decision rule:** Classify the shift as broadly persistent only if the next complete release shows positive national undergraduate change and undergraduate growth in at least 26 of 51 states/DC; otherwise do not elevate it to a broad multi-year finding. Report magnitude and concentration separately and do not infer cause.
- **Status:** Baseline implemented; monitor next release

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

- **Evidence trigger:** The public 2026 high-school report labels state estimates as 2023 data, and the Portal exposes a same-year 2023 undocumented higher-education state ranking.
- **Current IPEDS fit:** None
- **Additional data needed:** Current public 2023 state aggregates are sufficient for a bounded ecological comparison; time-aligned policy data or linked/microdata would be required for transition or causal analysis.
- **Proposed method:** Compare the ten states with explicit 2023 high-school graduate estimates against same-year 2023 undocumented higher-education enrollment; treat graduates as an annual flow and enrollment as a stock; compare geographic concentration without individual linkage.
- **Proposed output:** 2023 undocumented pipeline context note
- **Decision rule:** Use only same-year aggregate geography; do not interpret stock-to-flow multiples as college-going, transition, persistence, or causal rates, and do not infer policy effects from the ecological comparison.
- **Status:** Implemented as bounded 2023 state pipeline context

#### R07 · Which external source updates should trigger Portal refreshes or new research products?

- **Evidence trigger:** The maintained Research Library spans primary data, release schedules, methodology, benchmarks, and recurring Portal research products.
- **Current IPEDS fit:** Support
- **Additional data needed:** Current Research Library metadata and source-vintage signals; actual partner delivery schedules remain confirmation-dependent
- **Proposed method:** Classify every maintained source with a baseline route and explicit methodology/new-research escalation triggers; apply the change-type decision ladder before narrative changes.
- **Proposed output:** Source-update triage register and routing note
- **Decision rule:** Treat metadata/date-only change as non-analytical; route same-method new values to routine refresh; escalate definition, denominator, model, schema, geography, privacy, or material conclusion changes before publication.
- **Status:** Implemented as source-update triage register

#### R08 · Which institution-level QA signals should carry forward into the next complete Fall Enrollment release?

- **Evidence trigger:** The current 2023-2024 queue contains 27 high-priority and 50 medium-priority records, while the available 2025 directory review contains 154 structural-change UNITIDs; five medium-priority records overlap the candidate directory changes and no current high-priority record does.
- **Current IPEDS fit:** Support
- **Additional data needed:** Current latest-release QA, evidence-backed high-priority dispositions, and the candidate directory are sufficient to create a pre-release watchlist; the complete 2025 Fall Enrollment package is still required to resolve the next-release outcome.
- **Proposed method:** Union every current high/medium QA row with every candidate directory structural-change UNITID; preserve current publication dispositions only as context, surface cross-signal overlaps, and carry forward explicit next-release actions without inventing candidate-year enrollment values.
- **Proposed output:** Candidate-year QA carry-forward watchlist
- **Decision rule:** Every current high/medium QA row or candidate directory structural change enters the next full-package reconciliation. Existing publication dispositions are revalidated rather than inherited, and directory structure alone never establishes candidate-year enrollment movement or opening/closure.
- **Status:** Implemented as candidate-year QA carry-forward watchlist

## Governance principles

1. A new question should name the population, geography, period, denominator, and decision it is intended to support before analysis begins.
2. Source limitations are part of the research question. A convenient dataset is not a reason to collapse distinct populations into one measure.
3. Questions triggered by apparent anomalies enter QA review before they become public findings.
4. Research requiring partner data should begin with a definitions/methodology crosswalk and release-vintage review.
5. The agenda should be re-reviewed after each annual release because a confirmed pattern, revised source, or resolved anomaly can change priority.
