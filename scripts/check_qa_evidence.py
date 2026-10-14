"""Check QA-resolution evidence URLs without coupling live web state to offline validation."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
LOGS = (
    ("high", ROOT / "data" / "qa_resolution_log.csv"),
    ("medium", ROOT / "data" / "medium_qa_resolution_log.csv"),
)
USER_AGENT = "Mozilla/5.0 (compatible; qa-evidence-health-check/1.0)"


def curl_fallback(url: str) -> dict[str, object] | None:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if curl is None:
        return None
    result = subprocess.run(
        [
            curl,
            "-L",
            "-sS",
            "-o",
            "NUL" if sys.platform.startswith("win") else "/dev/null",
            "-w",
            "%{http_code}\n%{url_effective}",
            "--max-time",
            "20",
            "--user-agent",
            USER_AGENT,
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()
    if not lines or not lines[0].isdigit():
        return None
    status = int(lines[0])
    final_url = lines[1] if len(lines) > 1 and lines[1] else url
    return {
        "ok": 200 <= status < 400,
        "access_restricted": status in {401, 403},
        "status": status,
        "final_url": final_url,
        "transport": "curl_fallback",
    }


def check(url: str) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
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
    except (URLError, OSError) as exc:
        fallback = curl_fallback(url)
        if fallback is not None:
            return fallback
        reason = getattr(exc, "reason", exc)
        return {
            "ok": False,
            "access_restricted": False,
            "status": "network_error",
            "final_url": url,
            "error": str(reason),
        }


def main() -> int:
    results: list[dict[str, object]] = []
    queue_counts: dict[str, int] = {}
    for priority, log_path in LOGS:
        with log_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        queue_counts[priority] = len(rows)
        for row in rows:
            results.append(
                {
                    "priority": priority,
                    "unitid": row["unitid"],
                    "institution": row["institution"],
                    "evidence_label": row["evidence_label"],
                    "url": row["evidence_url"],
                    **check(row["evidence_url"]),
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
        "evidence_count": len(results),
        "queue_counts": queue_counts,
        "available_count": sum(bool(row["ok"]) for row in results),
        "access_restricted_count": len(restricted),
        "broken_count": len(broken),
        "network_error_count": len(network_errors),
        "all_resolved": not broken and not network_errors,
        "evidence": results,
    }
    print(json.dumps(payload, indent=2))

    if network_errors:
        print(
            "QA evidence check incomplete because at least one request failed at the network layer.",
            file=sys.stderr,
        )
        return 2
    if broken:
        print("QA evidence check found at least one broken HTTP URL.", file=sys.stderr)
        return 1
    if restricted:
        print(
            f"QA evidence check: {len(restricted)} URL(s) block scripted access with HTTP 401/403; manual browser review is required.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
