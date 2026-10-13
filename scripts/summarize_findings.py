"""Generate a small machine-readable findings summary from processed outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from project_config import END_YEAR, LATEST_DATA_STATUS, START_YEAR

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "data" / "findings.json"


def read_rows(name: str) -> list[dict[str, str]]:
    with (PROCESSED / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(name: str, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"Cannot write empty processed output: {name}")
    with (PROCESSED / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def n(row: dict[str, str], key: str) -> int:
    return int(row[key])


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def change_pct(new: int, old: int) -> float:
    return (new - old) / old * 100.0


def main() -> int:
    national = {int(row["year"]): row for row in read_rows("national_year.csv")}
    states = read_rows("state_year.csv")
    controls = read_rows("control_year.csv")
    institution_history = read_rows("institution_year.csv")
    institutions = read_rows(f"institutions_{END_YEAR}.csv")

    first = national[min(national)]
    latest = national[max(national)]
    latest_year = int(latest["year"])
    latest_states = [row for row in states if int(row["year"]) == latest_year]
    first_states = {row["state"]: row for row in states if int(row["year"]) == min(national)}

    ranked_latest = sorted(latest_states, key=lambda row: n(row, "nonresident_enrollment"), reverse=True)
    top5_total = sum(n(row, "nonresident_enrollment") for row in ranked_latest[:5])
    latest_total_nonresident = n(latest, "nonresident_enrollment")

    pre_pandemic_year = 2019
    pre_pandemic_states = {
        row["state"]: row for row in states if int(row["year"]) == pre_pandemic_year
    }
    recovery_changes = []
    for row in latest_states:
        baseline = pre_pandemic_states[row["state"]]
        change = n(row, "nonresident_enrollment") - n(baseline, "nonresident_enrollment")
        recovery_changes.append(
            {
                "state": row["state"],
                "baseline": n(baseline, "nonresident_enrollment"),
                "latest": n(row, "nonresident_enrollment"),
                "absolute_change": change,
                "pct_change": round(
                    change_pct(n(row, "nonresident_enrollment"), n(baseline, "nonresident_enrollment")), 1
                ) if n(baseline, "nonresident_enrollment") else None,
            }
        )

    def institution_dynamics(start_year: int, end_year: int) -> tuple[dict, list[dict]]:
        start_rows = {
            row["unitid"]: row
            for row in institution_history
            if int(row["year"]) == start_year
        }
        end_rows = {
            row["unitid"]: row
            for row in institution_history
            if int(row["year"]) == end_year
        }
        continuing = set(start_rows) & set(end_rows)
        entered = set(end_rows) - set(start_rows)
        left = set(start_rows) - set(end_rows)

        detail_rows: list[dict] = []
        continuing_changes: list[int] = []
        for unitid in sorted(set(start_rows) | set(end_rows)):
            start = start_rows.get(unitid)
            end = end_rows.get(unitid)
            start_nr = 0 if start is None else n(start, "nonresident_enrollment")
            end_nr = 0 if end is None else n(end, "nonresident_enrollment")
            change = end_nr - start_nr
            if start is not None and end is not None:
                continuing_changes.append(change)
                if change > 0:
                    status = "Continuing - grew"
                elif change < 0:
                    status = "Continuing - declined"
                else:
                    status = "Continuing - unchanged"
            elif end is not None:
                status = "Entered analytic universe"
            else:
                status = "Left analytic universe"

            label_row = end if end is not None else start
            assert label_row is not None
            detail_rows.append(
                {
                    "unitid": unitid,
                    "institution": label_row["institution"],
                    "state": label_row["state"],
                    "status": status,
                    f"control_{start_year}": "" if start is None else start["control"],
                    f"control_{end_year}": "" if end is None else end["control"],
                    f"nonresident_{start_year}": "" if start is None else start_nr,
                    f"nonresident_{end_year}": "" if end is None else end_nr,
                    "absolute_change": change,
                }
            )

        continuing_change = sum(continuing_changes)
        entered_enrollment = sum(n(end_rows[unitid], "nonresident_enrollment") for unitid in entered)
        left_enrollment = sum(n(start_rows[unitid], "nonresident_enrollment") for unitid in left)
        national_change = continuing_change + entered_enrollment - left_enrollment
        expected_change = (
            n(national[end_year], "nonresident_enrollment")
            - n(national[start_year], "nonresident_enrollment")
        )
        if national_change != expected_change:
            raise RuntimeError(
                f"Institution dynamics do not reconcile for {start_year}-{end_year}: "
                f"{national_change} != {expected_change}"
            )

        summary = {
            "start_year": start_year,
            "end_year": end_year,
            "start_institutions": len(start_rows),
            "end_institutions": len(end_rows),
            "continuing_institutions": len(continuing),
            "entered_institutions": len(entered),
            "left_institutions": len(left),
            "continuing_change": continuing_change,
            "entered_enrollment": entered_enrollment,
            "left_enrollment": left_enrollment,
            "entry_exit_net": entered_enrollment - left_enrollment,
            "national_change": national_change,
            "continuing_grew": sum(change > 0 for change in continuing_changes),
            "continuing_declined": sum(change < 0 for change in continuing_changes),
            "continuing_unchanged": sum(change == 0 for change in continuing_changes),
            "continuing_gross_gains": sum(change for change in continuing_changes if change > 0),
            "continuing_gross_declines": sum(change for change in continuing_changes if change < 0),
            "top10_continuing_gains": sum(
                sorted((change for change in continuing_changes if change > 0), reverse=True)[:10]
            ),
        }
        return summary, detail_rows

    decade_dynamics, decade_institution_rows = institution_dynamics(START_YEAR, latest_year)
    recovery_dynamics, _ = institution_dynamics(pre_pandemic_year, latest_year)
    write_rows("institution_change_summary.csv", decade_institution_rows)

    state_changes = []
    for row in latest_states:
        base = first_states.get(row["state"])
        if not base:
            continue
        state_changes.append(
            {
                "state": row["state"],
                str(START_YEAR): n(base, "nonresident_enrollment"),
                str(latest_year): n(row, "nonresident_enrollment"),
                "absolute_change": n(row, "nonresident_enrollment") - n(base, "nonresident_enrollment"),
                "pct_change": round(
                    change_pct(n(row, "nonresident_enrollment"), n(base, "nonresident_enrollment")), 1
                ) if n(base, "nonresident_enrollment") else None,
            }
        )

    recovery_by_state = {row["state"]: row for row in recovery_changes}
    state_change_rows = []
    for row in sorted(state_changes, key=lambda item: item["state"]):
        recovery = recovery_by_state[row["state"]]
        latest_row = next(
            item for item in latest_states if item["state"] == row["state"]
        )
        state_change_rows.append(
            {
                "state": row["state"],
                f"nonresident_{START_YEAR}": row[str(START_YEAR)],
                f"nonresident_{pre_pandemic_year}": recovery["baseline"],
                f"nonresident_{latest_year}": row[str(latest_year)],
                f"change_{START_YEAR}_{latest_year}": row["absolute_change"],
                f"change_pct_{START_YEAR}_{latest_year}": row["pct_change"],
                f"change_{pre_pandemic_year}_{latest_year}": recovery["absolute_change"],
                f"change_pct_{pre_pandemic_year}_{latest_year}": recovery["pct_change"],
                "recovery_status": (
                    f"At or above {pre_pandemic_year}"
                    if recovery["absolute_change"] >= 0
                    else f"Below {pre_pandemic_year}"
                ),
                f"nonresident_share_pct_{latest_year}": round(
                    f(latest_row, "nonresident_share_pct"), 2
                ),
            }
        )
    write_rows("state_change_summary.csv", state_change_rows)

    control_by_year = {
        (int(row["year"]), row["control"]): row for row in controls
    }
    control_order = ["Public", "Private nonprofit", "Private for-profit"]
    control_changes = []
    for control in control_order:
        start = control_by_year[(START_YEAR, control)]
        end = control_by_year[(latest_year, control)]
        start_nr = n(start, "nonresident_enrollment")
        end_nr = n(end, "nonresident_enrollment")
        control_changes.append(
            {
                "control": control,
                "start_nonresident": start_nr,
                "latest_nonresident": end_nr,
                "absolute_change": end_nr - start_nr,
                "pct_change": round(change_pct(end_nr, start_nr), 1),
                "start_national_share_pct": round(
                    start_nr / n(first, "nonresident_enrollment") * 100, 1
                ),
                "latest_national_share_pct": round(
                    end_nr / latest_total_nonresident * 100, 1
                ),
                "undergraduate_change": n(end, "undergraduate_nonresident")
                - n(start, "undergraduate_nonresident"),
                "graduate_change": n(end, "graduate_nonresident")
                - n(start, "graduate_nonresident"),
                "latest_graduate_share_pct": round(
                    n(end, "graduate_nonresident") / end_nr * 100, 1
                ),
            }
        )

    yoy_rows = [row for row in national.values() if row["yoy_nonresident_pct"]]
    largest_decline = min(yoy_rows, key=lambda row: f(row, "yoy_nonresident_pct"))
    strongest_growth = max(yoy_rows, key=lambda row: f(row, "yoy_nonresident_pct"))

    graduate_change = n(latest, "graduate_nonresident") - n(first, "graduate_nonresident")
    undergraduate_change = n(latest, "undergraduate_nonresident") - n(first, "undergraduate_nonresident")
    top10_institutions = sum(int(row["nonresident_enrollment"]) for row in institutions[:10])
    top100_institutions = sum(int(row["nonresident_enrollment"]) for row in institutions[:100])

    def state_concentration(year: int, count: int) -> float:
        year_rows = sorted(
            (row for row in states if int(row["year"]) == year),
            key=lambda row: n(row, "nonresident_enrollment"),
            reverse=True,
        )
        return round(
            sum(n(row, "nonresident_enrollment") for row in year_rows[:count])
            / n(national[year], "nonresident_enrollment")
            * 100,
            1,
        )

    summary = {
        "coverage": {
            "start_year": int(first["year"]),
            "end_year": latest_year,
            "geography": "50 states and District of Columbia",
            "latest_data_status": LATEST_DATA_STATUS,
        },
        "headline": {
            "latest_nonresident": n(latest, "nonresident_enrollment"),
            "latest_total_enrollment": n(latest, "total_enrollment"),
            "latest_share_pct": round(f(latest, "nonresident_share_pct"), 2),
            "change_since_2015": n(latest, "nonresident_enrollment") - n(first, "nonresident_enrollment"),
            "change_since_2015_pct": round(
                change_pct(n(latest, "nonresident_enrollment"), n(first, "nonresident_enrollment")), 1
            ),
            "largest_yoy_decline": {
                "year": int(largest_decline["year"]),
                "pct": round(f(largest_decline, "yoy_nonresident_pct"), 1),
            },
            "strongest_yoy_growth": {
                "year": int(strongest_growth["year"]),
                "pct": round(f(strongest_growth, "yoy_nonresident_pct"), 1),
            },
            "top5_state_share_pct": round(top5_total / n(latest, "nonresident_enrollment") * 100, 1),
        },
        "level_decomposition": {
            "graduate_change_students": graduate_change,
            "undergraduate_change_students": undergraduate_change,
            "net_change_students": graduate_change + undergraduate_change,
            "graduate_change_pct": round(
                change_pct(n(latest, "graduate_nonresident"), n(first, "graduate_nonresident")), 1
            ),
            "undergraduate_change_pct": round(
                change_pct(n(latest, "undergraduate_nonresident"), n(first, "undergraduate_nonresident")), 1
            ),
        },
        "recovery": {
            "baseline_year": pre_pandemic_year,
            "states_at_or_above_baseline": sum(row["absolute_change"] >= 0 for row in recovery_changes),
            "states_below_baseline": sum(row["absolute_change"] < 0 for row in recovery_changes),
            "largest_gains": sorted(
                recovery_changes, key=lambda row: row["absolute_change"], reverse=True
            )[:8],
            "largest_shortfalls": sorted(
                recovery_changes, key=lambda row: row["absolute_change"]
            )[:8],
        },
        "concentration": {
            "top10_institutions_share_pct": round(top10_institutions / latest_total_nonresident * 100, 1),
            "top100_institutions_share_pct": round(top100_institutions / latest_total_nonresident * 100, 1),
            "top2_states_start_share_pct": state_concentration(START_YEAR, 2),
            "top2_states_latest_share_pct": state_concentration(latest_year, 2),
            "top5_states_start_share_pct": state_concentration(START_YEAR, 5),
            "top5_states_latest_share_pct": state_concentration(latest_year, 5),
        },
        "institution_control": {
            "changes": control_changes,
            "series": [
                {
                    "year": year,
                    "controls": {
                        control: {
                            "nonresident": n(control_by_year[(year, control)], "nonresident_enrollment"),
                            "undergraduate_nonresident": n(
                                control_by_year[(year, control)], "undergraduate_nonresident"
                            ),
                            "graduate_nonresident": n(
                                control_by_year[(year, control)], "graduate_nonresident"
                            ),
                        }
                        for control in control_order
                    },
                }
                for year in range(START_YEAR, latest_year + 1)
            ],
        },
        "institution_dynamics": {
            "decade": decade_dynamics,
            "recovery": recovery_dynamics,
        },
        "top_states_latest": [
            {
                "state": row["state"],
                "nonresident": n(row, "nonresident_enrollment"),
                "share_of_state_enrollment_pct": round(f(row, "nonresident_share_pct"), 2),
            }
            for row in ranked_latest[:10]
        ],
        "largest_state_absolute_growth": sorted(
            state_changes, key=lambda row: row["absolute_change"], reverse=True
        )[:10],
        "largest_state_absolute_decline": sorted(
            state_changes, key=lambda row: row["absolute_change"]
        )[:10],
        "top_institutions_latest": [
            {
                "institution": row["institution"],
                "state": row["state"],
                "nonresident": int(row["nonresident_enrollment"]),
                "share_pct": round(float(row["nonresident_share_pct"]), 2),
            }
            for row in institutions[:15]
        ],
        "national_series": [
            {
                "year": int(row["year"]),
                "nonresident": n(row, "nonresident_enrollment"),
                "total": n(row, "total_enrollment"),
                "share_pct": round(f(row, "nonresident_share_pct"), 2),
                "undergraduate_nonresident": n(row, "undergraduate_nonresident"),
                "graduate_nonresident": n(row, "graduate_nonresident"),
            }
            for _, row in sorted(national.items())
        ],
    }

    OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["headline"], indent=2))
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
