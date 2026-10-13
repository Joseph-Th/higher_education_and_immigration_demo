from __future__ import annotations

import csv
import json
import re
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET
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
        cls.update_review = json.loads(
            (ROOT / "data" / "latest_update_review.json").read_text(encoding="utf-8")
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

    def test_latest_release_review_reconciles(self) -> None:
        review = self.update_review
        national = {int(row["year"]): row for row in self.national}
        prior_year = review["coverage"]["prior_year"]
        latest_year = review["coverage"]["latest_year"]
        expected_change = (
            int(national[latest_year]["nonresident_enrollment"])
            - int(national[prior_year]["nonresident_enrollment"])
        )
        self.assertEqual(review["national"]["absolute_change"], expected_change)
        self.assertEqual(
            review["national"]["undergraduate_change"]
            + review["national"]["graduate_change"],
            expected_change,
        )
        accounting = review["institution_accounting"]
        self.assertEqual(
            accounting["continuing_change"]
            + accounting["entered_enrollment"]
            - accounting["left_enrollment"],
            expected_change,
        )
        queue = rows(ROOT / "data" / "processed" / "latest_release_institution_review.csv")
        counts = Counter(row["review_priority"] for row in queue)
        self.assertEqual(counts["high"], review["review_queue"]["high"])
        self.assertEqual(counts["medium"], review["review_queue"]["medium"])
        self.assertEqual(counts["low"], review["review_queue"]["low"])
        self.assertEqual(
            counts["high"] + counts["medium"] + counts["low"],
            review["review_queue"]["flagged_total"],
        )
        self.assertEqual(self.site_data["latest_update_review"], review)

    def test_research_library_metadata(self) -> None:
        library = rows(ROOT / "data" / "research_library.csv")
        ids = [row["resource_id"] for row in library]
        self.assertEqual(len(ids), len(set(ids)))
        essential_ids = {
            "ipeds_complete_data",
            "digest_306_10",
            "portal_national_data",
            "portal_methodology",
            "undocumented_higher_ed_2026",
            "immigrant_origin_2026",
            "undocumented_hs_graduates_2026",
        }
        self.assertTrue(essential_ids.issubset(set(ids)))
        self.assertTrue(all(row["url"].startswith("https://") for row in library))
        self.assertTrue(
            all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["last_checked"]) for row in library)
        )
        rendered = (ROOT / "docs" / "RESEARCH_LIBRARY.md").read_text(encoding="utf-8")
        for row in library:
            self.assertIn(row["title"], rendered)
            self.assertIn(row["url"], rendered)

    def test_research_agenda_is_structured_and_rendered(self) -> None:
        agenda = rows(ROOT / "data" / "research_agenda.csv")
        self.assertGreaterEqual(len(agenda), 6)
        ids = [row["research_id"] for row in agenda]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"R01", "R02", "R04", "R05"}.issubset(set(ids)))
        self.assertTrue(all(row["priority"] in {"High", "Medium", "Low"} for row in agenda))
        self.assertTrue(any(row["current_ipeds_fit"] == "None" for row in agenda))
        self.assertTrue(any(row["current_ipeds_fit"] == "High" for row in agenda))
        rendered = (ROOT / "docs" / "RESEARCH_AGENDA.md").read_text(encoding="utf-8")
        for row in agenda:
            self.assertIn(row["research_id"], rendered)
            self.assertIn(row["question"], rendered)

    def test_briefing_note_tracks_validated_outputs(self) -> None:
        note = (ROOT / "docs" / "BRIEFING_NOTE.md").read_text(encoding="utf-8")
        headline = self.findings["headline"]
        latest = self.update_review["national"]
        queue = self.update_review["review_queue"]
        self.assertIn(f"{headline['latest_nonresident']:,} students", note)
        self.assertIn(f"{latest['absolute_change']:+,} students", note)
        self.assertIn(f"{latest['undergraduate_change']:+,}", note)
        self.assertIn(f"{latest['graduate_change']:+,}", note)
        self.assertIn(f"{queue['high']} high-priority", note)
        self.assertIn("IPEDS U.S. nonresident status should not be used as a proxy", note)

    def test_excel_workbook_is_valid_and_formula_driven(self) -> None:
        workbook = ROOT / "deliverables" / "ipeds_portfolio_analysis.xlsx"
        self.assertTrue(workbook.exists())
        self.assertGreater(workbook.stat().st_size, 20_000)
        expected_sheets = [
            "Executive Summary",
            "National Trend",
            "State Review",
            "Institution Control",
            "QA & Benchmark",
            "Source Library",
        ]
        with zipfile.ZipFile(workbook) as archive:
            self.assertIsNone(archive.testzip())
            root = ET.fromstring(archive.read("xl/workbook.xml"))
            namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            sheet_names = [
                element.attrib["name"]
                for element in root.findall("main:sheets/main:sheet", namespace)
            ]
            self.assertEqual(sheet_names, expected_sheets)
            worksheet_roots = [
                ET.fromstring(archive.read(name))
                for name in archive.namelist()
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
            ]
            formula_count = sum(
                len(sheet.findall(".//main:f", namespace)) for sheet in worksheet_roots
            )
            values = {
                element.text
                for sheet in worksheet_roots
                for element in sheet.findall(".//main:v", namespace)
            }
            self.assertGreater(formula_count, 0)
            self.assertIn("1044137", values)

    def test_state_profiles_cover_and_reconcile_all_geographies(self) -> None:
        index = rows(ROOT / "data" / "processed" / "state_profile_index.csv")
        self.assertEqual(len(index), 51)
        self.assertEqual({row["state"] for row in index}, CORE_STATES)
        latest_national = int(self.national[-1]["nonresident_enrollment"])
        self.assertEqual(sum(int(row["latest_nonresident"]) for row in index), latest_national)
        profile_dir = ROOT / "docs" / "state_profiles"
        self.assertEqual({path.stem for path in profile_dir.glob("*.md")}, CORE_STATES)
        az = next(row for row in index if row["state"] == "AZ")
        az_summary = next(
            row
            for row in rows(ROOT / "data" / "processed" / "state_change_summary.csv")
            if row["state"] == "AZ"
        )
        self.assertEqual(az["latest_nonresident"], az_summary[f"nonresident_{END_YEAR}"])
        self.assertEqual(int(az["latest_year"]), END_YEAR)
        self.assertEqual(int(az["start_year"]), START_YEAR)
        az_text = (profile_dir / "AZ.md").read_text(encoding="utf-8")
        self.assertIn("Arizona (AZ)", az_text)
        self.assertIn(f"{int(az['latest_nonresident']):,}", az_text)
        self.assertIn("IPEDS U.S. nonresident status is not a complete measure", az_text)
        profile_json = json.loads((ROOT / "data" / "state_profiles.json").read_text(encoding="utf-8"))
        self.assertEqual(set(profile_json["profiles"]), CORE_STATES)
        self.assertEqual(profile_json["profiles"]["AZ"]["latest"]["nonresident_enrollment"], int(az["latest_nonresident"]))
        self.assertEqual(
            (ROOT / "data" / "state_profiles.json").read_bytes(),
            (ROOT / "site" / "data" / "state_profiles.json").read_bytes(),
        )
        public_dir = ROOT / "site" / "downloads" / "state_profiles"
        for state in CORE_STATES:
            self.assertEqual(
                (profile_dir / f"{state}.md").read_bytes(),
                (public_dir / f"{state}.md").read_bytes(),
            )

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
                "data/processed/latest_release_institution_review.csv",
                "site/downloads/latest_release_institution_review.csv",
            ),
            (
                f"data/processed/institutions_{END_YEAR}.csv",
                f"site/downloads/institutions_{END_YEAR}.csv",
            ),
            ("data/schema_audit.csv", "site/downloads/schema_audit.csv"),
            ("data/source_manifest.csv", "site/downloads/source_manifest.csv"),
            ("data/benchmark_audit.csv", "site/downloads/benchmark_audit.csv"),
            ("data/research_library.csv", "site/downloads/research_library.csv"),
            ("data/research_agenda.csv", "site/downloads/research_agenda.csv"),
            (
                "data/processed/state_profile_index.csv",
                "site/downloads/state_profile_index.csv",
            ),
            (
                "deliverables/ipeds_portfolio_analysis.xlsx",
                "site/downloads/ipeds_portfolio_analysis.xlsx",
            ),
            (
                "data/reference/nces_digest_2025_306_10.csv",
                "site/downloads/nces_digest_2025_306_10.csv",
            ),
        ]
        for source, public in pairs:
            self.assertEqual((ROOT / source).read_bytes(), (ROOT / public).read_bytes(), public)
        self.assertEqual(
            (ROOT / "docs" / "LATEST_UPDATE_REVIEW.md").read_bytes(),
            (ROOT / "site" / "downloads" / "latest_update_review.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs" / "RESEARCH_LIBRARY.md").read_bytes(),
            (ROOT / "site" / "downloads" / "research_library.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs" / "RESEARCH_AGENDA.md").read_bytes(),
            (ROOT / "site" / "downloads" / "research_agenda.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs" / "BRIEFING_NOTE.md").read_bytes(),
            (ROOT / "site" / "downloads" / "briefing_note.md").read_bytes(),
        )

    def test_static_page_local_assets_and_ids(self) -> None:
        for page_name in ("index.html", "state.html"):
            html = (ROOT / "site" / page_name).read_text(encoding="utf-8")
            ids = re.findall(r'\bid="([^"]+)"', html)
            duplicates = [item for item, count in Counter(ids).items() if count > 1]
            self.assertEqual(duplicates, [], page_name)

            local_refs = re.findall(r'(?:href|src)="([^"]+)"', html)
            for ref in local_refs:
                if ref.startswith(("http://", "https://", "#")):
                    continue
                path_only = ref.split("?", 1)[0].split("#", 1)[0]
                target = ROOT / "site" / path_only
                self.assertTrue(target.exists(), f"missing local site asset in {page_name}: {ref}")


if __name__ == "__main__":
    unittest.main()

