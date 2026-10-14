# Private Nonprofit Growth Concentration, 2015-2024

This analysis follows research-agenda item R03 and tests whether the private-nonprofit increase in U.S. nonresident enrollment is dominated by a small set of institutions or distributed more broadly across the sector.

## Result

Private nonprofit institutions increased from **330,778** U.S. nonresident students in 2015 to **413,603** in 2024, a net change of **+82,825**.

Graduate enrollment contributed **+83,792** while undergraduate enrollment contributed **-967**. The top 10 positive institution contributors account for **34.5%** of gross positive movement, leaving **65.5%** outside the top 10 across **729** positive contributors.

**Decision rule:** call the sector shift concentrated only if the top 10 institutions contribute at least half of gross positive movement. **Result: Broadly distributed beyond the top 10.**

Gross positive movement is the denominator for concentration. Using the net sector change instead would overstate leading-institution shares whenever declining institutions offset some growth.

## Concentration checks

- Gross positive movement: **137,578** across **729** institutions.
- Gross negative movement: **54,753** across **718** institutions.
- Top 1 / top 5 / top 10 / top 25 shares of gross positive movement: **6.7% / 22.4% / 34.5% / 55.8%**.
- Positive-contribution HHI: **184**, equivalent to about **54.5** equally sized positive contributors.
- Endpoint accounting: continuing private nonprofits **+84,498** + entering endpoint enrollment **4,993** - exiting endpoint enrollment **6,666** = **+82,825**.

## Ten largest positive contributors

| Rank | Institution | State | Change | Undergraduate | Graduate | Gross-positive share | Cumulative share | Endpoint status | Latest-release QA gate |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Trine University-Regional/Non-Traditional Campuses | IN | +9,167 | +217 | +8,950 | 6.66% | 6.66% | Private nonprofit in both endpoints | Safe with context |
| 2 | New York University | NY | +6,748 | +3,329 | +3,419 | 4.90% | 11.57% | Private nonprofit in both endpoints | Not high-priority in latest release queue |
| 3 | Northeastern University | MA | +5,580 | -334 | +5,914 | 4.06% | 15.62% | Private nonprofit in both endpoints | Not high-priority in latest release queue |
| 4 | Columbia University in the City of New York | NY | +4,925 | +663 | +4,262 | 3.58% | 19.20% | Private nonprofit in both endpoints | Not high-priority in latest release queue |
| 5 | University of the Cumberlands | KY | +4,390 | +42 | +4,348 | 3.19% | 22.39% | Private nonprofit in both endpoints | Hold for confirmation |
| 6 | Johns Hopkins University | MD | +3,987 | +282 | +3,705 | 2.90% | 25.29% | Private nonprofit in both endpoints | Not high-priority in latest release queue |
| 7 | Indiana Wesleyan University-National & Global | IN | +3,721 | +287 | +3,434 | 2.70% | 28.00% | Entered endpoint sector universe | Not high-priority in latest release queue |
| 8 | Webster University | MO | +3,111 | +262 | +2,849 | 2.26% | 30.26% | Private nonprofit in both endpoints | Safe with context |
| 9 | Boston University | MA | +2,988 | +327 | +2,661 | 2.17% | 32.43% | Private nonprofit in both endpoints | Not high-priority in latest release queue |
| 10 | St. Francis College | NY | +2,886 | +99 | +2,787 | 2.10% | 34.53% | Private nonprofit in both endpoints | Hold for confirmation |

## Interpretation

The decomposition is descriptive, not causal. An institution appearing only in one private-nonprofit endpoint can reflect entry to or exit from the analytic universe, a control-category change, reporting change, merger/reorganization, or another classification change. The endpoint-status field therefore should not be read automatically as a campus opening or closure.

The concentration calculation retains all official IPEDS endpoint values. The institution table shows whether a contributor was private nonprofit in both endpoints or entered the endpoint sector universe, and separately carries the current latest-release QA priority and analyst publication class. Sector entry can reflect control-category or universe change rather than institution-level enrollment growth. A high-priority institution that is unresolved or held may remain in aggregate accounting while its institution-specific interpretation remains withheld.

The top-10 majority rule is an explicit portfolio decision rule for the R03 question, not a general statistical standard. The underlying shares, gross movements, contributor counts, and institution rows are published so a reviewer can apply a different concentration threshold if desired.

## Reproduction

```bash
python scripts/build_private_nonprofit_analysis.py
```

Canonical inputs are `data/processed/control_year.csv` and `data/processed/institution_year.csv`. The generated institution-contribution table is downstream analysis rather than a new analytical authority.
