"""Compare derived national results with an independent NCES Digest publication.

The Digest publishes values in thousands rounded to one decimal place. Its 2024
figures were prepared in March 2026 from provisional data, while this project
uses the currently posted IPEDS complete-data files retrieved in October 2026.
The audit therefore distinguishes close universe consistency from exact source-
vintage identity.
"""

from __future__ import annotations

import csv
from pathlib import Path

from project_config import DIGEST_BENCHMARK_URL


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "reference" / "nces_digest_2025_306_10.csv"
DERIVED = ROOT / "data" / "processed" / "national_year.csv"
OUTPUT = ROOT / "data" / "benchmark_audit.csv"

METRICS = {
    "total_enrollment": ("total_enrollment_thousands", 0.02),
    "nonresident_enrollment": ("nonresident_total_thousands", 1.00),
    "undergraduate_nonresident": ("undergraduate_nonresident_thousands", 1.00),
    "graduate_nonresident": ("graduate_nonresident_thousands", 1.00),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    reference = {int(row["year"]): row for row in read_csv(REFERENCE)}
    derived = {int(row["year"]): row for row in read_csv(DERIVED)}
    output_rows: list[dict[str, str | int | float]] = []
    failures: list[str] = []

    for year in sorted(reference):
        if year not in derived:
            failures.append(f"{year}: missing from derived national series")
            continue
        for metric, (reference_field, threshold_pct) in METRICS.items():
            current = int(derived[year][metric])
            published_thousands = float(reference[year][reference_field])
            published_approx = published_thousands * 1000.0
            difference = current - published_approx
            pct_difference = difference / published_approx * 100.0
            status = "PASS" if abs(pct_difference) <= threshold_pct else "FAIL"
            if status == "FAIL":
                failures.append(
                    f"{year} {metric}: {pct_difference:.3f}% difference exceeds {threshold_pct:.2f}%"
                )
            output_rows.append(
                {
                    "year": year,
                    "metric": metric,
                    "current_ipeds_value": current,
                    "digest_published_thousands": f"{published_thousands:.1f}",
                    "digest_approx_students": f"{published_approx:.0f}",
                    "difference_students": f"{difference:.0f}",
                    "difference_pct": f"{pct_difference:.4f}",
                    "consistency_threshold_pct": f"{threshold_pct:.2f}",
                    "status": status,
                    "digest_release_status": reference[year]["release_status"],
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"External benchmark: {len(output_rows)} metric-year checks")
    print(f"Reference: {DIGEST_BENCHMARK_URL}")
    for row in output_rows:
        if row["year"] == 2024:
            print(
                f"2024 {row['metric']}: current={row['current_ipeds_value']} "
                f"digest~={row['digest_approx_students']} "
                f"delta={row['difference_pct']}% {row['status']}"
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("External benchmark consistency: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

