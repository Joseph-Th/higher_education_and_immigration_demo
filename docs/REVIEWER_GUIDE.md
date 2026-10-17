# Reviewer Guide

This is a portfolio demonstration of end-to-end higher-education research work: source selection, reproducible analysis, QA/QC, methodological judgment, and communication for nontechnical readers. It is designed for fast review. The full repository is an audit trail, not a reading assignment.

Live publication: `https://joseph-th.github.io/higher_education_and_immigration_demo/`

## Five-minute review path

1. **Read `deliverables/research_brief.pdf` (2 pages).** This is the primary writing sample. Look for the research question, the small number of defensible findings, and the interpretation boundaries carried with the results.
2. **Scan the live publication.** Review the headline metrics, national and state findings, state explorer, and latest-release QA section. The page should stand on its own without requiring repository knowledge.
3. **Open `deliverables/management_briefing_deck.pptx` (5 slides).** This shows how the same validated analysis is compressed for leadership: KPI summary, trend, geography, structural drivers, and QA/interpretation guardrails.

If those three artifacts do not establish the value of the work, the supporting material should not be expected to rescue the presentation.

## Technical proof, only if useful

- **Excel:** `deliverables/ipeds_portfolio_analysis.xlsx` demonstrates formula-driven KPIs, state lookup, reconciliation, benchmark QA, and source organization.
- **SQL:** `site/sql-analysis.html` and `sql/portfolio_queries.sql` demonstrate read-only joins, CTEs, conditional aggregation, ranking, and window functions with independent reconciliation.
- **Reproducibility:** `python scripts/validate_project.py` rebuilds the analytical product and runs the project validation suite.
- **Method discipline:** `site/methodology-crosswalk.html` shows why IPEDS U.S. nonresident, SEVIS international, immigrant-origin, undocumented, pipeline, and refugee/asylee measures are not treated as interchangeable.

## Research judgment worth noticing

The strongest part of the project is not the number of artifacts. It is the decision discipline around what is safe to publish.

- **24/24** NCES Digest benchmark checks pass.
- **27/27** high-priority institution flags have manual evidence-backed dispositions: **26 safe with context, 1 held for confirmation**.
- **50/50** medium-priority flags are evidence-reviewed: **42 safe with context, 8 held for confirmation**.
- The **9 held institution-specific claims remain in official aggregate calculations but are kept out of unsupported institution-level narrative**.
- The project separates current-publication readiness from permission to advance to the next data year. A partial next-year package does not silently become a new analysis vintage.

Those controls are visible in `site/qa-review.html`, `site/medium-qa-review.html`, `site/publication-handoff.html`, and `site/release-readiness.html` if a reviewer wants to go deeper.

## What this work sample demonstrates

| Capability | Evidence |
| --- | --- |
| Research and source selection | Official NCES/IPEDS data, cross-year schema audit, population/source crosswalk |
| Quantitative analysis | National, state, student-level, institutional-control, and institution-continuity decompositions |
| QA/QC and judgment | Reconciliation tests, external benchmarks, manual anomaly review, explicit claim holds |
| Excel / SQL / Python | Formula-driven workbook, executable SQL pack, reproducible Python pipeline |
| Research writing | Two-page brief and public research memo |
| Leadership communication | Five-slide management briefing |
| Publication discipline | Claim handoff, release readiness, source lineage, governed public outputs |

## Scope boundary

This is a portfolio simulation, not a claim of access to an employer's internal data, partner workflow, approval chain, or deadlines. The analysis uses public administrative data and does not infer individual immigration status. Supporting operational controls demonstrate how the work would be maintained, but they are secondary to the research brief, live publication, and management deck.
