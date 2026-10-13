"""Assemble compact JSON and downloadable CSV assets for the static brief."""

from __future__ import annotations

import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path

from project_config import END_YEAR


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
    benchmark_audit = read_csv(DATA / "benchmark_audit.csv")
    schema_passed = sum(row["status"] == "PASS" for row in schema_audit)
    benchmark_passed = sum(row["status"] == "PASS" for row in benchmark_audit)
    if benchmark_passed != len(benchmark_audit):
        raise RuntimeError("External benchmark audit contains failed checks")

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

    benchmark_latest = [row for row in benchmark_audit if int(row["year"]) == END_YEAR]

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
                "checks": len(benchmark_audit),
                "checks_passed": benchmark_passed,
                "latest_rows": benchmark_latest,
                "status": "PASS" if benchmark_passed == len(benchmark_audit) else "FAIL",
                "url": "https://nces.ed.gov/programs/digest/d25/tables/dt25_306.10.asp",
            },
        },
        "sources": [
            {
                "label": "IPEDS Complete Data Files",
                "url": "https://nces.ed.gov/ipeds/help/complete-data-files",
            },
            {
                "label": f"IPEDS {END_YEAR} Fall Enrollment data",
                "url": f"https://nces.ed.gov/ipeds/complete-data-files/EF{END_YEAR}A.zip",
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

    for name in (
        "national_year.csv",
        "state_year.csv",
        "state_change_summary.csv",
        "control_year.csv",
        f"institutions_{END_YEAR}.csv",
    ):
        shutil.copy2(PROCESSED / name, DOWNLOADS / name)
    shutil.copy2(DATA / "schema_audit.csv", DOWNLOADS / "schema_audit.csv")
    shutil.copy2(DATA / "source_manifest.csv", DOWNLOADS / "source_manifest.csv")
    shutil.copy2(DATA / "benchmark_audit.csv", DOWNLOADS / "benchmark_audit.csv")
    shutil.copy2(
        DATA / "reference" / "nces_digest_2025_306_10.csv",
        DOWNLOADS / "nces_digest_2025_306_10.csv",
    )

    print(f"Wrote {SITE_DATA / 'site_data.json'}")
    print(f"NCES Digest consistency checks: {benchmark_passed}/{len(benchmark_audit)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
