from __future__ import annotations

import csv
import json
import re
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from project_config import CORE_STATES, END_YEAR, START_YEAR  # noqa: E402


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class ResearchProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.national = rows(ROOT / "data" / "processed" / "national_year.csv")
        cls.states = rows(ROOT / "data" / "processed" / "state_year.csv")
        cls.controls = rows(ROOT / "data" / "processed" / "control_year.csv")
        cls.institutions = rows(
            ROOT / "data" / "processed" / f"institutions_{END_YEAR}.csv"
        )
        cls.findings = json.loads((ROOT / "data" / "findings.json").read_text(encoding="utf-8"))
        cls.qa = json.loads((ROOT / "data" / "qa_report.json").read_text(encoding="utf-8"))
        cls.site_data = json.loads(
            (ROOT / "site" / "data" / "site_data.json").read_text(encoding="utf-8")
        )

    def test_expected_year_coverage(self) -> None:
        years = [int(row["year"]) for row in self.national]
        self.assertEqual(years, list(range(START_YEAR, END_YEAR + 1)))

    def test_all_states_and_dc_present_each_year(self) -> None:
        by_year: dict[int, set[str]] = defaultdict(set)
        for row in self.states:
            by_year[int(row["year"])].add(row["state"])
        self.assertEqual(set(by_year), set(range(START_YEAR, END_YEAR + 1)))
        for year, geographies in by_year.items():
            self.assertEqual(geographies, CORE_STATES, f"geography mismatch in {year}")

    def test_state_sums_equal_national_totals(self) -> None:
        metrics = (
            "total_enrollment",
            "nonresident_enrollment",
            "undergraduate_total",
            "undergraduate_nonresident",
            "graduate_total",
            "graduate_nonresident",
        )
        national = {int(row["year"]): row for row in self.national}
        state_sums: dict[int, Counter[str]] = defaultdict(Counter)
        for row in self.states:
            year = int(row["year"])
            for metric in metrics:
                state_sums[year][metric] += int(row[metric])
        for year in national:
            for metric in metrics:
                self.assertEqual(
                    state_sums[year][metric],
                    int(national[year][metric]),
                    f"{year} {metric}",
                )

    def test_control_sums_equal_national_totals(self) -> None:
        metrics = (
            "total_enrollment",
            "nonresident_enrollment",
            "undergraduate_nonresident",
            "graduate_nonresident",
        )
        national = {int(row["year"]): row for row in self.national}
        control_sums: dict[int, Counter[str]] = defaultdict(Counter)
        controls_by_year: dict[int, set[str]] = defaultdict(set)
        for row in self.controls:
            year = int(row["year"])
            controls_by_year[year].add(row["control"])
            for metric in metrics:
                control_sums[year][metric] += int(row[metric])
        expected_controls = {"Public", "Private nonprofit", "Private for-profit"}
        for year in national:
            self.assertEqual(controls_by_year[year], expected_controls)
            for metric in metrics:
                self.assertEqual(control_sums[year][metric], int(national[year][metric]))

    def test_level_components_reconcile_to_total(self) -> None:
        for row in self.national:
            self.assertEqual(
                int(row["total_enrollment"]),
                int(row["undergraduate_total"]) + int(row["graduate_total"]),
            )
            self.assertEqual(
                int(row["nonresident_enrollment"]),
                int(row["undergraduate_nonresident"])
                + int(row["graduate_nonresident"]),
            )

    def test_published_shares_recalculate(self) -> None:
        for row in self.national:
            expected = int(row["nonresident_enrollment"]) / int(row["total_enrollment"]) * 100
            self.assertAlmostEqual(float(row["nonresident_share_pct"]), expected, places=3)
        for row in self.states:
            expected = int(row["nonresident_enrollment"]) / int(row["total_enrollment"]) * 100
            self.assertAlmostEqual(float(row["nonresident_share_pct"]), expected, places=3)

    def test_latest_institution_table_is_sorted(self) -> None:
        counts = [int(row["nonresident_enrollment"]) for row in self.institutions]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertTrue(all(int(row["year"]) == END_YEAR for row in self.institutions))

    def test_findings_reconcile_to_source_tables(self) -> None:
        headline = self.findings["headline"]
        decomposition = self.findings["level_decomposition"]
        recovery = self.findings["recovery"]
        self.assertEqual(
            headline["change_since_2015"], decomposition["net_change_students"]
        )
        self.assertEqual(
            decomposition["graduate_change_students"]
            + decomposition["undergraduate_change_students"],
            decomposition["net_change_students"],
        )
        self.assertEqual(
            recovery["states_at_or_above_baseline"] + recovery["states_below_baseline"],
            51,
        )
        controls = self.findings["institution_control"]["changes"]
        self.assertEqual(sum(row["absolute_change"] for row in controls), headline["change_since_2015"])
        dynamics = self.findings["institution_dynamics"]["decade"]
        self.assertEqual(dynamics["national_change"], headline["change_since_2015"])
        self.assertEqual(
            dynamics["continuing_change"]
            + dynamics["entered_enrollment"]
            - dynamics["left_enrollment"],
            dynamics["national_change"],
        )
        self.assertEqual(
            dynamics["continuing_grew"]
            + dynamics["continuing_declined"]
            + dynamics["continuing_unchanged"],
            dynamics["continuing_institutions"],
        )

        recovery_dynamics = self.findings["institution_dynamics"]["recovery"]
        national = {int(row["year"]): row for row in self.national}
        expected_recovery = (
            int(national[END_YEAR]["nonresident_enrollment"])
            - int(national[2019]["nonresident_enrollment"])
        )
        self.assertEqual(recovery_dynamics["national_change"], expected_recovery)

    def test_state_change_summary_has_one_row_per_geography(self) -> None:
        summary = rows(ROOT / "data" / "processed" / "state_change_summary.csv")
        self.assertEqual(len(summary), 51)
        self.assertEqual({row["state"] for row in summary}, CORE_STATES)
        statuses = Counter(row["recovery_status"] for row in summary)
        self.assertEqual(statuses[f"At or above 2019"], 33)
        self.assertEqual(statuses[f"Below 2019"], 18)

    def test_institution_change_summary_reconciles(self) -> None:
        summary = rows(ROOT / "data" / "processed" / "institution_change_summary.csv")
        dynamics = self.findings["institution_dynamics"]["decade"]
        self.assertEqual(
            len(summary),
            dynamics["continuing_institutions"]
            + dynamics["entered_institutions"]
            + dynamics["left_institutions"],
        )
        self.assertEqual(
            sum(int(row["absolute_change"]) for row in summary),
            dynamics["national_change"],
        )
        statuses = Counter(row["status"] for row in summary)
        self.assertEqual(statuses["Entered analytic universe"], dynamics["entered_institutions"])
        self.assertEqual(statuses["Left analytic universe"], dynamics["left_institutions"])

    def test_qa_report_is_all_pass(self) -> None:
        self.assertTrue(self.qa["checks"])
        self.assertTrue(all(value == "PASS" for value in self.qa["checks"].values()))

    def test_external_benchmark_is_all_pass(self) -> None:
        audit = rows(ROOT / "data" / "benchmark_audit.csv")
        self.assertEqual(len(audit), 24)
        self.assertTrue(all(row["status"] == "PASS" for row in audit))
        self.assertEqual(self.site_data["quality"]["benchmark"]["checks_passed"], 24)

    def test_site_downloads_are_exact_copies(self) -> None:
        pairs = [
            ("data/processed/national_year.csv", "site/downloads/national_year.csv"),
            ("data/processed/state_year.csv", "site/downloads/state_year.csv"),
            (
                "data/processed/state_change_summary.csv",
                "site/downloads/state_change_summary.csv",
            ),
            ("data/processed/control_year.csv", "site/downloads/control_year.csv"),
            (
                "data/processed/institution_change_summary.csv",
                "site/downloads/institution_change_summary.csv",
            ),
            (
                f"data/processed/institutions_{END_YEAR}.csv",
                f"site/downloads/institutions_{END_YEAR}.csv",
            ),
            ("data/schema_audit.csv", "site/downloads/schema_audit.csv"),
            ("data/source_manifest.csv", "site/downloads/source_manifest.csv"),
            ("data/benchmark_audit.csv", "site/downloads/benchmark_audit.csv"),
            (
                "data/reference/nces_digest_2025_306_10.csv",
                "site/downloads/nces_digest_2025_306_10.csv",
            ),
        ]
        for source, public in pairs:
            self.assertEqual((ROOT / source).read_bytes(), (ROOT / public).read_bytes(), public)

    def test_static_page_local_assets_and_ids(self) -> None:
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        ids = re.findall(r'\bid="([^"]+)"', html)
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        self.assertEqual(duplicates, [])

        local_refs = re.findall(r'(?:href|src)="([^"]+)"', html)
        for ref in local_refs:
            if ref.startswith(("http://", "https://", "#")):
                continue
            target = ROOT / "site" / ref
            self.assertTrue(target.exists(), f"missing local site asset: {ref}")


if __name__ == "__main__":
    unittest.main()

