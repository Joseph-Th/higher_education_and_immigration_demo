"""Assemble compact JSON and downloadable CSV assets for the static brief."""

from __future__ import annotations

import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
SITE = ROOT / "site"
SITE_DATA = SITE / "data"
DOWNLOADS = SITE / "downloads"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    qa = json.loads((DATA / "qa_report.json").read_text(encoding="utf-8"))
    state_rows = read_csv(PROCESSED / "state_year.csv")
    source_manifest = read_csv(DATA / "source_manifest.csv")
    schema_audit = read_csv(DATA / "schema_audit.csv")
    schema_passed = sum(row["status"] == "PASS" for row in schema_audit)

    state_series: dict[str, list[dict]] = defaultdict(list)
    for row in state_rows:
        state_series[row["state"]].append(
            {
                "year": int(row["year"]),
                "nonresident": int(row["nonresident_enrollment"]),
                "total": int(row["total_enrollment"]),
                "share_pct": round(float(row["nonresident_share_pct"]), 2),
            }
        )

    latest_qa = next(item for item in qa["years"] if item["year"] == findings["coverage"]["end_year"])
    latest_total = findings["headline"]["latest_total_enrollment"]

    # NCES Digest 2025 table 306.10 reports the same 2024 universe in thousands,
    # rounded to one decimal place. This is an independent publication-level
    # benchmark rather than a second transformation of our raw files.
    benchmark_thousands = 19659.6
    derived_thousands = round(latest_total / 1000.0, 1)
    if derived_thousands != benchmark_thousands:
        raise RuntimeError(
            f"NCES Digest benchmark mismatch: derived {derived_thousands} vs {benchmark_thousands}"
        )

    payload = {
        **findings,
        "state_series": dict(sorted(state_series.items())),
        "quality": {
            "source_archives": len(source_manifest),
            "schema_years_passed": schema_passed,
            "institution_year_rows": qa["institution_year_rows"],
            "latest_institutions": latest_qa["institutions_in_analytic_universe"],
            "latest_total_flag_counts": latest_qa["total_flag_counts"],
            "latest_nonresident_flag_counts": latest_qa["nonresident_flag_counts"],
            "benchmark": {
                "name": "NCES Digest of Education Statistics 2025, Table 306.10",
                "published_total_thousands": benchmark_thousands,
                "derived_total_thousands": derived_thousands,
                "status": "PASS",
                "url": "https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp",
            },
        },
        "sources": [
            {
                "label": "IPEDS Complete Data Files",
                "url": "https://nces.ed.gov/ipeds/help/complete-data-files",
            },
            {
                "label": "IPEDS 2024 Fall Enrollment data",
                "url": "https://nces.ed.gov/ipeds/complete-data-files/EF2024A.zip",
            },
            {
                "label": "NCES Digest 2025 Table 306.10",
                "url": "https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp",
            },
            {
                "label": "IPEDS release schedule",
                "url": "https://nces.ed.gov/ipeds/survey-components/data-release-schedule",
            },
        ],
    }

    SITE_DATA.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "site_data.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    for name in ("national_year.csv", "state_year.csv", "institutions_2024.csv"):
        shutil.copy2(PROCESSED / name, DOWNLOADS / name)
    shutil.copy2(DATA / "schema_audit.csv", DOWNLOADS / "schema_audit.csv")
    shutil.copy2(DATA / "source_manifest.csv", DOWNLOADS / "source_manifest.csv")

    print(f"Wrote {SITE_DATA / 'site_data.json'}")
    print("NCES Digest 2024 total benchmark: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
