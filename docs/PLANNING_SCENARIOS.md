# Planning Scenarios and Variance Review

This is a **portfolio planning exercise, not a predictive forecast**. It demonstrates how an analyst can create a transparent baseline, compare a known actual with that baseline, and present multiple forward planning cases without claiming statistical certainty.

## Backtest: forecast vs. actual

Using the 2021-2023 CAGR (7.25%) as a simple end-of-2023 planning baseline would have implied **1,088,197** U.S. nonresident students in 2024. The observed 2024 total was **1,044,137**, a variance of **-44,060** (-4.05%).

The point is not that this baseline should have been used. The point is that even a transparent growth-rate assumption can materially miss the actual result, so reporting should show both the assumption and the variance.

## 2025 planning cases

| Case | Historical basis | Annual rate | 2025 planning value |
| --- | --- | ---: | ---: |
| Long-run recovery pace | 2019-2024 | 1.42% | 1,058,964 |
| Latest-year pace | 2023-2024 | 2.91% | 1,074,536 |
| Recent two-year recovery pace | 2022-2024 | 4.09% | 1,086,816 |

The data-derived range is **1,058,964 to 1,086,816**, a spread of **27,852** students. The latest-year pace produces the middle case of **1,074,536**.

These are scenario anchors for planning discussion. No 2025 actual is available in this project, and the cases do not incorporate policy, visa, institution-specific, economic, or other causal drivers.

## Reproduction

```bash
python scripts/build_planning_scenarios.py
```

The canonical historical authority remains `data/processed/national_year.csv`. The scenario CSV is a downstream analytical support artifact.
