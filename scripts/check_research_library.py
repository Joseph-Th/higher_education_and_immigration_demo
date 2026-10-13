"""Check Research Library URLs without coupling live web state to offline validation."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "research_library.csv"
USER_AGENT = "Mozilla/5.0 (compatible; research-library-health-check/1.0)"


def check(url: str) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/zip,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            status = int(response.status)
            return {
                "ok": 200 <= status < 400,
                "access_restricted": False,
                "status": status,
                "final_url": response.geturl(),
            }
    except HTTPError as exc:
        access_restricted = exc.code in {401, 403}
        return {
            "ok": False,
            "access_restricted": access_restricted,
            "status": exc.code,
            "final_url": url,
            "error": str(exc.reason),
        }
    except URLError as exc:
        return {
            "ok": False,
            "access_restricted": False,
            "status": "network_error",
            "final_url": url,
            "error": str(exc.reason),
        }


def main() -> int:
    with LIBRARY.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    results = []
    for row in rows:
        result = check(row["url"])
        results.append(
            {
                "resource_id": row["resource_id"],
                "title": row["title"],
                "recorded_last_checked": row["last_checked"],
                "url": row["url"],
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
        "resource_count": len(results),
        "available_count": sum(bool(row["ok"]) for row in results),
        "access_restricted_count": len(restricted),
        "broken_count": len(broken),
        "network_error_count": len(network_errors),
        "all_resolved": not broken and not network_errors,
        "resources": results,
    }
    print(json.dumps(payload, indent=2))

    if network_errors:
        print(
            "Research Library check incomplete because at least one request failed at the network layer.",
            file=sys.stderr,
        )
        return 2
    if broken:
        print("Research Library check found at least one broken HTTP URL.", file=sys.stderr)
        return 1
    if restricted:
        print(
            f"Research Library check: {len(restricted)} URL(s) block scripted access with HTTP 401/403; manual browser review is required.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
