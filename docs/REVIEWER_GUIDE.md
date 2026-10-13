# Reviewer Guide

This repository is intended to be evaluated as a small recurring research product, not only as a coding exercise. A reviewer should be able to understand the research question, inspect the public result, trace a number to source data, and see how the product would be maintained when a new release appears.

## Five-minute review path

1. Open `site/index.html` through a local static server or deployed Pages URL. Read the six longitudinal findings, the latest-release review, and inspect the state explorer.
2. Read `docs/FINDINGS.md` for the exact numerical basis behind the public narrative.
3. Read `docs/METHODOLOGY.md` for population definitions, universe rules, endpoint matching, and limitations.
4. Inspect `data/source_manifest.csv`, `data/schema_audit.csv`, `data/benchmark_audit.csv`, and `data/research_library.csv` to see provenance, validation evidence, and source organization.
5. Run `python scripts/validate_project.py`. If browser tooling is available, also run `python scripts/browser_smoke.py`.
6. Read `docs/UPDATE_PLAYBOOK.md` and `docs/DATA_CALENDAR.md` to see how the next NCES release would be detected, reviewed, and published.

## What the project demonstrates

| Analyst responsibility | Evidence in this repository |
| --- | --- |
| Acquire public administrative data | `scripts/fetch_ipeds.py` retrieves official NCES data and dictionaries and records exact source URLs |
| Preserve source lineage | `data/source_manifest.csv` records retrieval time, bytes, SHA-256 hashes, and extracted files |
| Handle changing schemas | `scripts/audit_ipeds_schema.py`, `data/schema_audit.csv`, and `docs/VARIABLE_MAPPING.md` verify required variables and labels year by year |
| Define an analytic universe | `docs/METHODOLOGY.md` documents the degree-granting First Look/Digest universe and 50-states-plus-DC rule |
| Build reproducible transformations | `scripts/build_analysis.py` creates institution-, state-, control-, and national-level outputs from the same normalized records |
| Perform substantive analysis | `scripts/summarize_findings.py` produces level, geography, control, concentration, recovery, and institution-dynamics findings |
| Investigate apparent discrepancies | `scripts/validate_benchmarks.py` quantifies release-vintage differences instead of forcing current data to match an older Digest publication |
| Review a new annual release | `scripts/build_update_review.py`, `docs/LATEST_UPDATE_REVIEW.md`, and `data/processed/latest_release_institution_review.csv` reconcile the new year and produce a reason-coded QA queue |
| Organize a Research Library | `data/research_library.csv` and `scripts/build_research_library.py` maintain structured source metadata and generate `docs/RESEARCH_LIBRARY.md` |
| Quality-control published numbers | `tests/test_research_product.py` checks reconciliation identities, coverage, shares, outputs, downloads, and benchmark status |
| Communicate to nontechnical readers | `site/` turns the analysis into a concise research brief with plain-language definitions and limitations |
| Validate the published artifact | `scripts/browser_smoke.py` checks desktop/mobile rendering, interactions, downloads, console errors, and overflow |
| Maintain a recurring product | `scripts/check_for_new_release.py`, `docs/DATA_CALENDAR.md`, and `docs/UPDATE_PLAYBOOK.md` separate release detection from validation and publication |

## A concise project explanation

The project asks how U.S. nonresident fall enrollment changed across U.S. degree-granting institutions from 2015 through 2024. I built the series from official IPEDS complete-data files, audited the variables and aggregation codes across all ten years, restricted the data to a documented NCES/Digest universe, and created national, state, student-level, institutional-control, and institution-panel analyses. I then added structural QA, an independent NCES Digest benchmark, source hashes, downloadable outputs, and a static public brief. The project also includes an update playbook and release checker so it can operate as a recurring data product rather than a one-time analysis.

## Findings worth discussing

The strongest findings are not merely descriptive rankings:

- The 2015-2024 national increase came entirely from graduate enrollment. Graduate U.S. nonresident enrollment rose by 138,765 while undergraduate enrollment fell by 75,365.
- Recovery is geographically uneven. Thirty-three states/DC were at or above 2019 by 2024, while 18 remained below.
- Private nonprofit institutions account for the major positive shift by control, adding 82,825 U.S. nonresident students over the decade.
- Institution-panel accounting shows the +63,400 national increase was not created by adding more institutions to the analytic universe. Continuing institutions contributed +66,981 while universe entry and exit netted -3,581.
- The newest release has a different short-run composition: from 2023 to 2024 undergraduate U.S. nonresident enrollment increased by 31,592 while graduate enrollment decreased by 2,053, producing a net increase of 29,539.
- Current IPEDS subgroup values differ slightly from the March 2026 Digest publication even though the overall enrollment universe is effectively identical. The project records that source-vintage difference rather than hiding it.

## Interpretation boundaries

The project deliberately avoids claims the data cannot support. IPEDS U.S. nonresident status is not a complete measure of international, immigrant-origin, undocumented, DACA, or foreign-born students. Fall Enrollment is a point-in-time snapshot. State values are based on institution location. UNITID matching helps with endpoint accounting but does not fully resolve mergers, splits, acquisitions, or reorganizations.

## Reproduction commands

Core rebuild and validation:

```bash
python scripts/validate_project.py
```

Optional browser publication QA:

```bash
python scripts/browser_smoke.py
```

Live next-release check:

```bash
python scripts/check_for_new_release.py
```

The first command is intentionally offline once raw IPEDS files have been collected. The release checker is intentionally online and separate, so a future NCES posting cannot silently change the reproducibility of the current published result.
