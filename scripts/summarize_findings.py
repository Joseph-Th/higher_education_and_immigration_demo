"""Generate a small machine-readable findings summary from processed outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "data" / "findings.json"


def read_rows(name: str) -> list[dict[str, str]]:
    with (PROCESSED / name).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def n(row: dict[str, str], key: str) -> int:
    return int(row[key])


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def change_pct(new: int, old: int) -> float:
    return (new - old) / old * 100.0


def main() -> int:
    national = {int(row["year"]): row for row in read_rows("national_year.csv")}
    states = read_rows("state_year.csv")
    institutions = read_rows("institutions_2024.csv")

    first = national[min(national)]
    latest = national[max(national)]
    latest_year = int(latest["year"])
    latest_states = [row for row in states if int(row["year"]) == latest_year]
    first_states = {row["state"]: row for row in states if int(row["year"]) == min(national)}

    ranked_latest = sorted(latest_states, key=lambda row: n(row, "nonresident_enrollment"), reverse=True)
    top5_total = sum(n(row, "nonresident_enrollment") for row in ranked_latest[:5])

    state_changes = []
    for row in latest_states:
        base = first_states.get(row["state"])
        if not base:
            continue
        state_changes.append(
            {
                "state": row["state"],
                "2015": n(base, "nonresident_enrollment"),
                str(latest_year): n(row, "nonresident_enrollment"),
                "absolute_change": n(row, "nonresident_enrollment") - n(base, "nonresident_enrollment"),
                "pct_change": round(
                    change_pct(n(row, "nonresident_enrollment"), n(base, "nonresident_enrollment")), 1
                ) if n(base, "nonresident_enrollment") else None,
            }
        )

    yoy_rows = [row for row in national.values() if row["yoy_nonresident_pct"]]
    largest_decline = min(yoy_rows, key=lambda row: f(row, "yoy_nonresident_pct"))
    strongest_growth = max(yoy_rows, key=lambda row: f(row, "yoy_nonresident_pct"))

    summary = {
        "coverage": {
            "start_year": int(first["year"]),
            "end_year": latest_year,
            "geography": "50 states and District of Columbia",
            "latest_data_status": "provisional",
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
