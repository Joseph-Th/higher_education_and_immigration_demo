"""Check population-crosswalk methodology URLs without coupling live web state to offline validation."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from check_research_library import check


ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "data" / "population_crosswalk.csv"


def main() -> int:
    with CROSSWALK.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    results = []
    for row in rows:
        result = check(row["source_url"])
        results.append(
            {
                "population_id": row["population_id"],
                "population_label": row["population_label"],
                "recorded_last_checked": row["last_checked"],
                "url": row["source_url"],
                **result,
            }
        )

    broken = [
        row
        for row in results
        if not row["ok"] and not row["access_restricted"] and row["status"] != "network_error"
    ]
    network_errors = [row for row in results if row["status"] == "network_error"]
    restricted = [row for row in results if row["access_restricted"]]
    payload = {
        "population_count": len(results),
        "available_count": sum(bool(row["ok"]) for row in results),
        "access_restricted_count": len(restricted),
        "broken_count": len(broken),
        "network_error_count": len(network_errors),
        "all_resolved": not broken and not network_errors,
        "populations": results,
    }
    print(json.dumps(payload, indent=2))

    if network_errors:
        print(
            "Population crosswalk check is incomplete because at least one request failed at the network layer.",
            file=sys.stderr,
        )
        return 2
    if broken:
        print("Population crosswalk check found at least one broken source URL.", file=sys.stderr)
        return 1
    if restricted:
        print(
            f"Population crosswalk check: {len(restricted)} URL(s) block scripted access with HTTP 401/403; manual browser review is required.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
