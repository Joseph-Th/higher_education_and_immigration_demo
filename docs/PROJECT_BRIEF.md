# Project Brief

## Working title

**U.S. Nonresident Students in Higher Education: National and State Enrollment Trends, 2015-2024**

## Purpose

Create a portfolio research product that demonstrates the practical work expected of a data and research analyst supporting higher-education policy: maintaining recurring source data, validating quantitative information, identifying meaningful changes, documenting methodology, and translating findings for nontechnical readers.

The project should be useful as a standalone research brief, not merely as a technical demonstration.

## Intended audience

- Higher-education leaders and administrators.
- Policy and research staff.
- Researchers and advocates who need a concise overview of international/nonresident enrollment patterns.
- Hiring reviewers evaluating research, writing, and data-analysis ability.

## Primary research question

How did fall enrollment of U.S. nonresident students change nationally and across states from 2015 through 2024?

## Secondary questions

1. How did the national count and share of U.S. nonresident students change over the period?
2. Which states had the largest absolute increases or decreases?
3. Which states experienced the largest percentage changes among states with a meaningful baseline population?
4. How did undergraduate and graduate patterns differ, where the source tables support a consistent cross-year comparison?
5. How much of the national change is concentrated in a small number of states or institutions?
6. How did trends differ across public, private nonprofit, and private for-profit institutions?
7. Is the national change driven by enrollment changes at continuing institutions, or by changes in which institutions are in the analytic universe?
8. What changed in the newest annual release, and which institution-level changes warrant analyst review before publication?
9. Where do public 2023 undocumented high-school graduate and undocumented higher-education estimates overlap geographically, and what can that same-year ecological context support without being misread as an individual transition rate?

## Evidence standard

Every published figure should be traceable to:

1. an official NCES source file;
2. a documented variable definition;
3. a reproducible transformation;
4. an explicit QA/QC check; and
5. a stated limitation when interpretation is not straightforward.

## Deliverables

### Research brief

A short web-based brief containing:

- an executive summary;
- a small set of defensible findings prioritized for policy/research readers;
- national trend visualization;
- state comparison visualization/table;
- generated state/DC profile briefs for repeatable state-level publication;
- undergraduate/graduate comparison if cross-year definitions permit;
- institutional-control comparison;
- institution endpoint-change accounting;
- newest-release change decomposition and QA triage summary;
- methodology and limitations;
- source and update information.

A concise PDF version should also be available for reviewers who expect a conventional policy-research publication rather than a repository or interactive site. The PDF must be generated from the same validated memo and carry a freshness check tying it to the exact source HTML.

### Reproducible research materials

- source-data download script;
- source manifest with checksums;
- variable mapping across years;
- cleaned analysis dataset;
- QA/QC checks;
- analysis code;
- chart-generation code;
- documentation sufficient for another analyst to reproduce the result.
- external publication benchmark audit and release-vintage documentation.
- generated latest-release review memo and reason-coded institution queue.
- generated stakeholder briefing note built from validated findings rather than separately maintained figures.
- reviewer-ready Excel workbook demonstrating formula-based analysis, lookup, QA/QC, presentation, and source organization.
- reviewer-ready six-slide PowerPoint management briefing generated from validated KPI, trend, geography, driver, and QA outputs with a source/builder freshness manifest.
- public six-query SQL analysis pack demonstrating joins, CTEs, grouping, conditional aggregation, ranking, and window functions against an ephemeral SQLite database rebuilt from validated CSV outputs.
- explicit three-case ad hoc analysis casebook demonstrating how bounded management questions are clarified, answered from validated authorities, reconciled, and returned concisely without fabricating requesters, deadlines, or client history.
- state recovery decomposition that explains the 2019-2024 state outcomes with exact undergraduate/graduate, institutional-control, and institution-continuity accounting plus a concentration measure for leading institution contributors.
- private-nonprofit growth concentration analysis that reconciles institution endpoint contributions to the sector total, separates undergraduate/graduate change, measures concentration against gross positive movement, and carries current latest-release QA gates for named institutions.
- planning-scenario and variance artifact that backtests a transparent historical-growth baseline against the known 2024 actual and presents three 2025 planning anchors without claiming a predictive model or observed future value.
- dated release/freshness monitoring artifact that preserves the current next-year NCES availability observation, applies a complete-package year-advance gate, retains source-review dates, and exposes recurring-product triggers without inventing future deadlines.
- generated 50-state-plus-DC profile set and machine-readable profile index.
- structured research-needs register connecting findings and source limitations to proposed methods, outputs, and decision rules.
- structured Research Library with machine-readable source metadata and generated documentation.
- structured population/source crosswalk that prevents IPEDS, SEVIS, immigrant-origin, undocumented, pipeline, and refugee/asylee concepts from being treated as interchangeable.
- bounded national population-trend comparison that uses the crosswalk as a hard gate, retains separate method-compatible trend segments, and prevents unlike immigration-related populations from being combined into a single enrollment series.
- bounded 2023 undocumented pipeline context that compares same-year state aggregate annual high-school graduate flow with higher-education enrollment stock, preserves fixed source vintages, and explicitly blocks individual-transition and causal-policy interpretations.
- structured recurring-report operations register for the three research products named in the target role, with explicit partner-confirmed scheduling, versioned intake, methodology-change review, QA gates, publication outputs, and archival handoff.
- structured seven-stage production-cycle register that separates shared coordination gates from product-specific methodology and requires evidence at each handoff rather than inferred calendar progress.
- blank production-cycle log template plus validator for a real kickoff record, with controlled report/stage IDs, record types, materiality, statuses, dates, and nonpublic-by-default handling for completed partner logs.
- structured public-release register and generated data-governance page that enforce data minimization and an exact allowlist for public artifacts.
- online Research Library URL-health checker kept separate from offline reproducibility validation.
- online population-crosswalk source-health checker kept separate from offline reproducibility validation.
- reviewer-ready PDF research brief plus a source/PDF SHA-256 manifest.
- browser-level publication smoke test.

## Non-goals

- The project will not treat IPEDS "U.S. nonresident" as synonymous with all immigrants, all international students, undocumented students, DACA recipients, or immigrant-origin students.
- The project will not infer immigration status beyond what the IPEDS reporting category supports.
- The project will not collect or publish person-level immigration-status data merely because a research question concerns immigrant or undocumented students; future restricted partner inputs would remain nonpublic unless a separate release decision authorizes aggregate outputs.
- The project will not rank institutions or states as "good" or "bad" based only on enrollment counts.
- The first release will favor a small number of well-supported findings over a large interactive dashboard.

## Publication principle

The public page should read like a small policy-research product. Technical complexity is useful only when it improves reproducibility, accuracy, or reader understanding.

