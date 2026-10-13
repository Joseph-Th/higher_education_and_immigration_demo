"""Generate one concise, reproducible research profile for every state and DC."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from project_config import CORE_STATES, END_YEAR, LATEST_DATA_STATUS, START_YEAR


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "docs" / "state_profiles"
INDEX = PROCESSED / "state_profile_index.csv"
JSON_OUTPUT = ROOT / "data" / "state_profiles.json"

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed(value: int) -> str:
    return f"{value:+,}" if value else "0"


def signed_pct(value: float) -> str:
    return f"{value:+.1f}%" if value else "0.0%"


def pct_change(new: int, old: int) -> float | None:
    if old == 0:
        return None
    return (new - old) / old * 100.0


def main() -> int:
    state_year = read_rows(PROCESSED / "state_year.csv")
    summaries = {row["state"]: row for row in read_rows(PROCESSED / "state_change_summary.csv")}
    institutions = read_rows(PROCESSED / f"institutions_{END_YEAR}.csv")

    series: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in state_year:
        series[row["state"]].append(row)
    by_state_institutions: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in institutions:
        by_state_institutions[row["state"]].append(row)
    for rows in by_state_institutions.values():
        rows.sort(key=lambda row: int(row["nonresident_enrollment"]), reverse=True)

    if set(series) != CORE_STATES or set(summaries) != CORE_STATES:
        raise RuntimeError("State profile inputs do not contain exactly the 50 states plus DC")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT_DIR.glob("*.md"):
        old.unlink()

    baseline_year = 2019
    start_change = f"change_{START_YEAR}_{END_YEAR}"
    start_change_pct = f"change_pct_{START_YEAR}_{END_YEAR}"
    baseline_change = f"change_{baseline_year}_{END_YEAR}"
    baseline_change_pct = f"change_pct_{baseline_year}_{END_YEAR}"

    index_rows: list[dict[str, object]] = []
    profile_payload: dict[str, dict[str, object]] = {}
    for state in sorted(CORE_STATES, key=lambda code: STATE_NAMES[code]):
        rows = sorted(series[state], key=lambda row: int(row["year"]))
        if [int(row["year"]) for row in rows] != list(range(START_YEAR, END_YEAR + 1)):
            raise RuntimeError(f"Incomplete annual series for {state}")
        latest = rows[-1]
        prior = rows[-2]
        summary = summaries[state]
        latest_nonresident = int(latest["nonresident_enrollment"])
        prior_nonresident = int(prior["nonresident_enrollment"])
        latest_change = latest_nonresident - prior_nonresident
        latest_change_pct = pct_change(latest_nonresident, prior_nonresident)
        graduate = int(latest["graduate_nonresident"])
        undergraduate = int(latest["undergraduate_nonresident"])
        graduate_share = graduate / latest_nonresident * 100 if latest_nonresident else 0.0
        top = by_state_institutions[state][:5]
        top_name = top[0]["institution"] if top else ""
        top_count = int(top[0]["nonresident_enrollment"]) if top else 0

        index_rows.append(
            {
                "state": state,
                "state_name": STATE_NAMES[state],
                "start_year": START_YEAR,
                "baseline_year": baseline_year,
                "latest_year": END_YEAR,
                "latest_nonresident": latest_nonresident,
                "latest_share_pct": f"{float(latest['nonresident_share_pct']):.2f}",
                "change_since_start": int(summary[start_change]),
                "change_pct_since_start": summary[start_change_pct],
                "change_since_baseline": int(summary[baseline_change]),
                "change_pct_since_baseline": summary[baseline_change_pct],
                "recovery_status": summary["recovery_status"],
                "year_over_year_change": latest_change,
                "year_over_year_pct": "" if latest_change_pct is None else f"{latest_change_pct:.1f}",
                "graduate_share_pct": f"{graduate_share:.1f}",
                "top_institution": top_name,
                "top_institution_nonresident": top_count,
                "profile_file": f"{state}.md",
            }
        )
        profile_payload[state] = {
            "state": state,
            "state_name": STATE_NAMES[state],
            "latest": {
                "year": END_YEAR,
                "institution_count": int(latest["institution_count"]),
                "total_enrollment": int(latest["total_enrollment"]),
                "nonresident_enrollment": latest_nonresident,
                "nonresident_share_pct": round(float(latest["nonresident_share_pct"]), 2),
                "undergraduate_nonresident": undergraduate,
                "graduate_nonresident": graduate,
                "graduate_share_pct": round(graduate_share, 1),
            },
            "changes": {
                "since_start": {
                    "absolute": int(summary[start_change]),
                    "pct": float(summary[start_change_pct]),
                },
                "since_2019": {
                    "absolute": int(summary[baseline_change]),
                    "pct": float(summary[baseline_change_pct]),
                    "recovery_status": summary["recovery_status"],
                },
                "latest_year": {
                    "prior_year": END_YEAR - 1,
                    "absolute": latest_change,
                    "pct": None if latest_change_pct is None else round(latest_change_pct, 1),
                },
            },
            "top_institutions": [
                {
                    "institution": row["institution"],
                    "control": row["control"],
                    "nonresident_enrollment": int(row["nonresident_enrollment"]),
                    "nonresident_share_pct": round(float(row["nonresident_share_pct"]), 2),
                }
                for row in top
            ],
            "series": [
                {
                    "year": int(row["year"]),
                    "institution_count": int(row["institution_count"]),
                    "nonresident_enrollment": int(row["nonresident_enrollment"]),
                    "nonresident_share_pct": round(float(row["nonresident_share_pct"]), 2),
                    "undergraduate_nonresident": int(row["undergraduate_nonresident"]),
                    "graduate_nonresident": int(row["graduate_nonresident"]),
                }
                for row in rows
            ],
            "markdown_file": f"{state}.md",
        }

        lines = [
            f"# {STATE_NAMES[state]} ({state}) | U.S. Nonresident Enrollment Profile",
            "",
            f"**Coverage:** Fall {START_YEAR}-{END_YEAR}, degree-granting institutions in the IPEDS First Look/Digest Title IV universe  ",
            f"**Latest data status:** {LATEST_DATA_STATUS.capitalize()}  ",
            "**Geography:** Institution location, not student residence or country of origin",
            "",
            "## Current snapshot",
            "",
            f"- **{latest_nonresident:,}** U.S. nonresident students in Fall {END_YEAR}.",
            f"- **{float(latest['nonresident_share_pct']):.2f}%** of total enrollment in the state analytic universe.",
            f"- **{undergraduate:,} undergraduate** and **{graduate:,} graduate** U.S. nonresident students; graduate students account for **{graduate_share:.1f}%** of the state total.",
            f"- **{int(latest['institution_count']):,} institutions** are in the state analytic universe for {END_YEAR}.",
            "",
            "## Change over time",
            "",
            f"- {START_YEAR}-{END_YEAR}: **{signed(int(summary[start_change]))} ({signed_pct(float(summary[start_change_pct]))})**.",
            f"- {baseline_year}-{END_YEAR}: **{signed(int(summary[baseline_change]))} ({signed_pct(float(summary[baseline_change_pct]))})**; **{summary['recovery_status']}**.",
            f"- {END_YEAR - 1}-{END_YEAR}: **{signed(latest_change)}**" + (f" (**{signed_pct(latest_change_pct)}**)" if latest_change_pct is not None else "") + ".",
            "",
            f"## Largest institutions in {END_YEAR}",
            "",
            "| Institution | Control | U.S. nonresident | Share of institution enrollment |",
            "| --- | --- | ---: | ---: |",
        ]
        if top:
            for row in top:
                lines.append(
                    f"| {row['institution']} | {row['control']} | {int(row['nonresident_enrollment']):,} | {float(row['nonresident_share_pct']):.2f}% |"
                )
        else:
            lines.append("| No institutions in current analytic universe | - | 0 | - |")

        lines.extend(
            [
                "",
                "## Ten-year series",
                "",
                "| Fall year | Institutions | U.S. nonresident | Share of total | Undergraduate | Graduate |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['year']} | {int(row['institution_count']):,} | {int(row['nonresident_enrollment']):,} | {float(row['nonresident_share_pct']):.2f}% | {int(row['undergraduate_nonresident']):,} | {int(row['graduate_nonresident']):,} |"
            )
        lines.extend(
            [
                "",
                "## Interpretation boundaries",
                "",
                "IPEDS U.S. nonresident status is not a complete measure of international, immigrant-origin, undocumented, DACA, or foreign-born students. Counts are Fall Enrollment point-in-time measures. State assignment is based on institution location. Institution membership in the analytic universe can change because of reporting, eligibility, classification, merger, or UNITID changes.",
                "",
                "## Source and reproducibility",
                "",
                f"Derived from the same official NCES/IPEDS Fall Enrollment and institutional directory files used by the national brief. See `docs/METHODOLOGY.md`, `data/source_manifest.csv`, and `data/schema_audit.csv`. Profile generated from validated project outputs for Fall {END_YEAR}.",
                "",
            ]
        )
        (OUTPUT_DIR / f"{state}.md").write_text("\n".join(lines), encoding="utf-8")

    with INDEX.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(index_rows[0].keys()))
        writer.writeheader()
        writer.writerows(index_rows)

    JSON_OUTPUT.write_text(
        json.dumps(
            {
                "coverage": {
                    "start_year": START_YEAR,
                    "end_year": END_YEAR,
                    "latest_data_status": LATEST_DATA_STATUS,
                    "geographies": "50 states and District of Columbia",
                },
                "profiles": profile_payload,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"State profiles: {len(index_rows)} profiles")
    print(f"Wrote {INDEX}")
    print(f"Wrote {JSON_OUTPUT}")
    print(f"Wrote {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
