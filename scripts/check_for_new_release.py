"""Check NCES for the next Fall Enrollment and directory complete-data files.

This is intentionally separate from the offline validation lane. It makes live
HTTP requests and is meant as a lightweight release-monitoring aid, not as a
dependency for reproducing the currently published analysis.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from project_config import END_YEAR


BASE = "https://nces.ed.gov/ipeds/complete-data-files"
USER_AGENT = "Mozilla/5.0 (compatible; ipeds-portfolio-release-check/1.0)"


def check(url: str) -> dict[str, object]:
    request = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=20) as response:
            return {
                "available": response.status == 200,
                "status": response.status,
                "content_length": response.headers.get("Content-Length"),
            }
    except HTTPError as exc:
        return {"available": False, "status": exc.code, "content_length": None}
    except URLError as exc:
        return {
            "available": False,
            "status": "network_error",
            "content_length": None,
            "error": str(exc.reason),
        }


def build_payload() -> dict[str, object]:
    year = END_YEAR + 1
    names = [
        f"EF{year}A.zip",
        f"EF{year}A_Dict.zip",
        f"HD{year}.zip",
        f"HD{year}_Dict.zip",
    ]
    results = []
    for name in names:
        url = f"{BASE}/{name}"
        result = {"file": name, "url": url, **check(url)}
        results.append(result)

    fall_enrollment_ready = all(
        bool(row["available"]) for row in results if row["file"].startswith(f"EF{year}A")
    )
    directory_ready = all(
        bool(row["available"]) for row in results if row["file"].startswith(f"HD{year}")
    )
    package_ready = fall_enrollment_ready and directory_ready
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "current_analysis_end_year": END_YEAR,
        "candidate_next_year": year,
        "fall_enrollment_ready": fall_enrollment_ready,
        "directory_ready": directory_ready,
        "package_ready": package_ready,
        "release_decision": "READY_FOR_SCHEMA_REVIEW" if package_ready else "HOLD_YEAR_ADVANCE",
        "files": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-snapshot",
        type=Path,
        help="Optional path for a dated JSON monitoring snapshot.",
    )
    args = parser.parse_args()

    payload = build_payload()
    print(json.dumps(payload, indent=2))

    if args.write_snapshot:
        args.write_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.write_snapshot.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote monitoring snapshot to {args.write_snapshot}", file=sys.stderr)

    if any(row["status"] == "network_error" for row in payload["files"]):
        print("Release check incomplete because at least one request failed at the network layer.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

