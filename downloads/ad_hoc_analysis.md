# Ad Hoc Analysis Casebook

This is an explicit **portfolio simulation** of three bounded analyst requests. The questions are constructed to demonstrate request clarification, source selection, calculation, QA, and concise response. They are not client requests, organizational SLAs, or claims of employment history.

## Working pattern

1. Clarify the business question, population, geography, and vintage.
2. Select the smallest validated authority needed to answer it.
3. Calculate only the metrics needed for the decision question.
4. Reconcile the result to an independent total or accounting identity where possible.
5. Return a short answer with the interpretation boundary still visible.

## A01: Which states/DC are still below their 2019 U.S. nonresident enrollment, and how concentrated is the remaining shortfall?

**Decision use:** Prioritize where a follow-up geography review would start.

**Answer:** 18 states/DC remain below 2019.

Combined shortfall is -56,517 students. The five largest shortfalls (CA -33,282, OR -4,265, KS -3,842, WA -3,834, ID -3,648) account for 86.5% of it.

**Source authority:** `data/processed/state_change_summary.csv`

**QA:** Below-baseline rows=18; shortfall sum=-56,517; top-five share=86.5% (**PASS**)

## A02: Which states contributed most to the 2023-2024 national increase?

**Decision use:** Identify the geographies driving the newest annual movement.

**Answer:** The five largest state gains contributed +17,753 students, or 60.1% of the +29,539 national gain.

Largest gains: FL +6,207, KY +4,615, IN +2,422, TX +2,363, IL +2,146.

**Source authority:** `data/processed/state_year.csv; data/processed/national_year.csv`

**QA:** All 51 state/DC changes sum to the national change: +29,539 = +29,539 (**PASS**)

## A03: Which institutional-control sector explains the 2015-2024 net increase?

**Decision use:** Give management a concise structural explanation for the decade result.

**Answer:** Private nonprofit institutions increased by 82,825 students.

That gain was partly offset by Private for-profit -3,338 and Public -16,087, reconciling to the national +63,400 change.

**Source authority:** `data/processed/control_year.csv; data/processed/national_year.csv`

**QA:** Control-sector changes sum to national decade change: +63,400 = +63,400 (**PASS**)

## Reproduction

```bash
python scripts/build_ad_hoc_analysis.py
```

The generated CSV is a compact reviewer/audit surface. The underlying processed CSVs remain the analytical authorities.
