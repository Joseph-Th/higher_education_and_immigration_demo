# Partner Research Production Cycle

This is a portfolio coordination model for the three recurring research products represented in `data/recurring_report_register.csv`. It does **not** represent the Presidents' Alliance's internal project-management system, staffing model, deadlines, or approval chain. The cycle starts only after a real production kickoff or refreshed partner package is confirmed.

**Shared control stages:** 7
**Recurring products covered:** 3
**Inferred internal deadlines:** 0

## Stage control register

| # | Stage | Coordination role | Entry condition | Blocking condition | Exit condition | Retained evidence |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Kickoff and scope lock | Analyst + partner lead | Confirmed production kickoff | Missing decision owner; unconfirmed source vintage; inferred rather than confirmed milestones; undefined deliverables | Partner confirms scope; roles; milestones; source vintage; delivery format; and decision owner | Cycle brief and confirmed scope record |
| 2 | Versioned intake | Analyst | Kickoff scope is locked | Missing or unreadable files; undocumented source; unversioned package; absent methodology needed to reproduce the product | Complete versioned package is preserved and every required input is either present or explicitly logged as missing | Intake manifest and preserved source package |
| 3 | Method-change review | Analyst + partner method lead | Versioned intake is complete | Any material method change is unexplained; comparability is assumed rather than demonstrated; source vintage is ambiguous | Every material change is documented with its expected effect on comparability and publication language | Method-change comparison and decision notes |
| 4 | Reproduction and QA | Analyst | Method-change review is complete | Headline totals cannot be reproduced; components do not reconcile; material break lacks a discrepancy record | Required totals reproduce or every material exception has an owned discrepancy record with evidence needs | QA results and discrepancy log |
| 5 | Discrepancy and question resolution | Analyst + partner lead | QA has identified questions or confirmed no material discrepancies | Material discrepancy remains unresolved; partner response is missing for a decision that depends on it; evidence contradicts proposed interpretation | Material issues are resolved or explicitly disclosed and any remaining nonmaterial items are documented for handoff | Resolved question/discrepancy log |
| 6 | Publication gate | Designated reviewer + analyst | Analysis and material discrepancy review are complete | Missing sign-off; stale source or citation; unresolved material issue; release disclosure not carried into public copy | Designated reviewer records approval or an explicit hold and the public-release decision matches the evidence | Publication handoff and approval/hold record |
| 7 | Archive and next-cycle handoff | Analyst | Publication decision is recorded | Missing provenance; missing approval/hold record; final package cannot reproduce the published or held decision | Cycle package is archived with enough evidence for a new analyst to reconstruct decisions without relying on oral memory | Archive manifest and next-cycle handoff note |

## Product kickoff packet

The shared stages define how work advances; the recurring-report register defines what must be checked for each product.

### Undocumented Students in U.S. Higher Education

- **Current portfolio position:** Current public product and methodology reference reviewed
- **Trigger for a real cycle:** Production kickoff or delivery of a refreshed ACS-based estimate package
- **Intake evidence:** Versioned source extract; data dictionary; modeling/code notes; prior-report methodology; change log; table shells; suppression and uncertainty rules
- **Method-change review:** Confirm undocumented-identification model, international-student exclusions, DACA-subset logic, ACS vintage, geography, weighting, and any changed eligibility assumptions
- **QA gate:** Reproduce partner national totals; reconcile state tables to documented methods; compare with the prior report; log unexplained breaks; hold publication until material discrepancies are resolved
- **Expected outputs after approval:** Recurring report tables; methodology notes; Portal data updates; archived source and review package
- **Pre-kickoff next action:** At kickoff, confirm partner timeline, exact ACS vintage, method changes, delivery format, review milestones, and final sign-off owner

### Immigrant-Origin Students in Higher Education

- **Current portfolio position:** Current public product and methodology reference reviewed
- **Trigger for a real cycle:** Production kickoff or delivery of a refreshed CPS immigrant-origin analysis package
- **Intake evidence:** Versioned analytic tables or extract; variable definitions; weighting notes; prior-report methodology; change log; table shells; state-coverage notes
- **Method-change review:** Confirm first- and second-generation definitions, age/education universe, nonimmigrant-student exclusion, CPS vintage, survey weights, state-support rules, and any revised workforce measures
- **QA gate:** Reproduce national headline totals; verify first/second-generation components; compare supported state estimates with prior publication; document sampling/definition changes before narrative use
- **Expected outputs after approval:** Recurring report tables; methodology notes; Portal data updates; archived source and review package
- **Pre-kickoff next action:** At kickoff, confirm partner timeline, CPS vintage, population-definition changes, state outputs, review milestones, and final sign-off owner

### Undocumented Students Graduating High School

- **Current portfolio position:** Current public product and methodology reference reviewed
- **Trigger for a real cycle:** Production kickoff or delivery of refreshed ACS/graduation-rate inputs
- **Intake evidence:** Versioned ACS-derived estimates; NCES graduation-rate inputs; model assumptions; prior-report methodology; change log; table shells; demographic/state input tables
- **Method-change review:** Confirm age universe, undocumented-estimation method, pooled ACS period, differential graduation-rate assumptions, state/race-ethnicity inputs, and any revised treatment of recent arrivals
- **QA gate:** Reproduce the annual graduate estimate from documented inputs; trace each assumption; compare demographic/state components with prior report; log sensitivity or definition changes before publication
- **Expected outputs after approval:** Recurring report estimates; methodology notes; Portal research update; archived source and review package
- **Pre-kickoff next action:** At kickoff, confirm partner timeline, pooled ACS period, NCES rate vintage, model changes, review milestones, and final sign-off owner

## Minimum coordination record

A live cycle should retain, at minimum, a cycle identifier, report ID, stage, opened date, owner role, question or discrepancy, materiality, evidence requested, response/evidence received, decision, disclosure requirement, status, and closed date. Dates and named owners belong in the real cycle record only after kickoff; they are intentionally absent from this portfolio template.

## Advancement rule

Calendar time alone never advances a stage. Work moves forward only when the current stage's required record exists, its blocking conditions are cleared or explicitly carried as a hold/disclosure, and its exit condition is documented.
