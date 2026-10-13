# SQL Analysis and Reconciliation

This layer demonstrates read-only SQL analysis over the project's validated processed CSVs. `scripts/build_sql_analysis.py` rebuilds an in-memory SQLite database on every run, loads five canonical CSV tables, executes the public query pack in `sql/portfolio_queries.sql`, and compares each query's result with an independently calculated value from the source CSVs. No SQLite database is stored or published.

**Queries executed:** 6
**Query checks passed:** 6/6
**Source tables loaded:** 5
**Stored database artifacts:** 0

## Query audit

| Query | Purpose | Skills | Rows | Check | Status |
| --- | --- | --- | ---: | --- | --- |
| Q01 | National year-over-year change | CTE, LAG window function, CASE, arithmetic | 10 | latest annual change: `29539` | PASS |
| Q02 | State recovery from 2019 to 2024 | CTE, conditional aggregation, CASE, RANK | 51 | states/DC at or above 2019: `33` | PASS |
| Q03 | Institutional-control decade change | CTE, conditional aggregation, ROUND, RANK | 3 | largest control-group decade increase: `Private nonprofit|82825` | PASS |
| Q04 | Largest 2024 institutions and national share | JOIN, ROW_NUMBER, cumulative SUM window | 20 | largest latest-year institution: `New York University|19202` | PASS |
| Q05 | Institution-universe change accounting | CTE, CASE classification, GROUP BY, SUM window | 2 | institution-universe change accounting: `66981|-3581|63400` | PASS |
| Q06 | State totals reconcile to national totals | CTE, GROUP BY, JOIN, reconciliation deltas | 10 | maximum state-to-national reconciliation delta: `0` | PASS |

## Q01: National year-over-year change

**SQL skills:** CTE, LAG window function, CASE, arithmetic

**Independent check:** latest annual change = `29539` (PASS)

| year | nonresident_enrollment | prior_nonresident | annual_change | annual_change_pct |
| --- | --- | --- | --- | --- |
| 2015 | 980737 |  |  |  |
| 2016 | 996383 | 980737 | 15646 | 1.6 |
| 2017 | 998471 | 996383 | 2088 | 0.21 |
| 2018 | 988488 | 998471 | -9983 | -1.0 |
| 2019 | 973058 | 988488 | -15430 | -1.56 |

_First 5 of 10 result rows shown._

## Q02: State recovery from 2019 to 2024

**SQL skills:** CTE, conditional aggregation, CASE, RANK

**Independent check:** states/DC at or above 2019 = `33` (PASS)

| state | nonresident_2019 | nonresident_2024 | change_since_2019 | recovery_status | recovery_rank |
| --- | --- | --- | --- | --- | --- |
| IL | 41291 | 55755 | 14464 | AT_OR_ABOVE_2019 | 1 |
| TX | 63451 | 77730 | 14279 | AT_OR_ABOVE_2019 | 2 |
| IN | 24229 | 37082 | 12853 | AT_OR_ABOVE_2019 | 3 |
| FL | 46411 | 58391 | 11980 | AT_OR_ABOVE_2019 | 4 |
| MO | 16288 | 27436 | 11148 | AT_OR_ABOVE_2019 | 5 |

_First 5 of 51 result rows shown._

## Q03: Institutional-control decade change

**SQL skills:** CTE, conditional aggregation, ROUND, RANK

**Independent check:** largest control-group decade increase = `Private nonprofit|82825` (PASS)

| control | nonresident_2015 | nonresident_2024 | decade_change | decade_change_pct | decade_change_rank |
| --- | --- | --- | --- | --- | --- |
| Private nonprofit | 330778 | 413603 | 82825 | 25.04 | 1 |
| Private for-profit | 23840 | 20502 | -3338 | -14.0 | 2 |
| Public | 626119 | 610032 | -16087 | -2.57 | 3 |

## Q04: Largest 2024 institutions and national share

**SQL skills:** JOIN, ROW_NUMBER, cumulative SUM window

**Independent check:** largest latest-year institution = `New York University|19202` (PASS)

| unitid | institution | state | control | nonresident_enrollment | national_share_pct | institution_rank | cumulative_nonresident |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 193900 | New York University | NY | Private nonprofit | 19202 | 1.84 | 1 | 19202 |
| 190150 | Columbia University in the City of New York | NY | Private nonprofit | 13812 | 1.32 | 2 | 33014 |
| 139755 | Georgia Institute of Technology-Main Campus | GA | Public | 13496 | 1.29 | 3 | 46510 |
| 145637 | University of Illinois Urbana-Champaign | IL | Public | 13350 | 1.28 | 4 | 59860 |
| 104151 | Arizona State University Campus Immersion | AZ | Public | 12563 | 1.2 | 5 | 72423 |

_First 5 of 20 result rows shown._

## Q05: Institution-universe change accounting

**SQL skills:** CTE, CASE classification, GROUP BY, SUM window

**Independent check:** institution-universe change accounting = `66981|-3581|63400` (PASS)

| movement_group | institution_records | net_change | national_net_change |
| --- | --- | --- | --- |
| Continuing institutions | 3470 | 66981 | 63400 |
| Universe entry/exit | 1419 | -3581 | 63400 |

## Q06: State totals reconcile to national totals

**SQL skills:** CTE, GROUP BY, JOIN, reconciliation deltas

**Independent check:** maximum state-to-national reconciliation delta = `0` (PASS)

| year | national_nonresident | state_nonresident | nonresident_delta | national_total | state_total | total_delta |
| --- | --- | --- | --- | --- | --- | --- |
| 2015 | 980737 | 980737 | 0 | 19988204 | 19988204 | 0 |
| 2016 | 996383 | 996383 | 0 | 19846904 | 19846904 | 0 |
| 2017 | 998471 | 998471 | 0 | 19778151 | 19778151 | 0 |
| 2018 | 988488 | 988488 | 0 | 19651412 | 19651412 | 0 |
| 2019 | 973058 | 973058 | 0 | 19630178 | 19630178 | 0 |

_First 5 of 10 result rows shown._

## Reproduction

```bash
python scripts/build_sql_analysis.py
```

The SQL query pack is intentionally SELECT-only. The builder rejects data-definition or data-mutation statements so the SQL layer cannot rewrite the validated source tables.
