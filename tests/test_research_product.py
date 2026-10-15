from __future__ import annotations

import csv
import hashlib
import html as html_module
import json
import re
import sqlite3
import sys
import tempfile
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
from build_data_governance import (  # noqa: E402
    expand_pairs as expand_public_release_pairs,
    read_register as read_public_release_register,
    validate_register_rows,
    validate_public_tree,
)
from build_production_cycle import validate_stages as validate_production_stages  # noqa: E402
from validate_production_cycle_log import (  # noqa: E402
    FIELDS as PRODUCTION_LOG_FIELDS,
    validate_log_rows as validate_production_log_rows,
)
from build_sql_analysis import (  # noqa: E402
    EXPECTED_QUERY_IDS,
    build_connection as build_sql_connection,
    read_queries as read_sql_queries,
)
from build_candidate_directory_change_review import (  # noqa: E402
    validate_capture as validate_candidate_directory_change_review,
)


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

    def test_state_recovery_analysis_reconciles_three_independent_decompositions(self) -> None:
        analysis = rows(ROOT / "data" / "state_recovery_analysis.csv")
        self.assertEqual(len(analysis), 51)
        self.assertEqual({row["state"] for row in analysis}, CORE_STATES)
        statuses = Counter(row["recovery_status"] for row in analysis)
        self.assertEqual(statuses["At or above 2019"], 33)
        self.assertEqual(statuses["Below 2019"], 18)

        for row in analysis:
            net = int(row["change_2019_2024"])
            self.assertEqual(
                int(row["undergraduate_change"]) + int(row["graduate_change"]),
                net,
                row["state"],
            )
            self.assertEqual(
                int(row["public_change"])
                + int(row["private_nonprofit_change"])
                + int(row["private_forprofit_change"]),
                net,
                row["state"],
            )
            self.assertIn(
                row["control_driver"],
                {"Public-led", "Private nonprofit-led", "Private for-profit-led", "Balanced / offsetting"},
            )
            institution_net = (
                int(row["continuing_change"])
                + int(row["entered_enrollment"])
                - int(row["exited_enrollment"])
            )
            self.assertEqual(institution_net, net, row["state"])
            self.assertEqual(int(row["institution_accounting_net"]), net, row["state"])
            if net:
                self.assertEqual(
                    int(row["directional_movement"]) - int(row["offsetting_movement"]),
                    abs(net),
                    row["state"],
                )
            self.assertLessEqual(
                int(row["top3_directional_contribution"]),
                int(row["directional_movement"]),
                row["state"],
            )
            self.assertGreaterEqual(float(row["top3_directional_share_pct"]), 0.0)
            self.assertLessEqual(float(row["top3_directional_share_pct"]), 100.0)

        national = {int(row["year"]): row for row in self.national}
        national_change = (
            int(national[END_YEAR]["nonresident_enrollment"])
            - int(national[2019]["nonresident_enrollment"])
        )
        self.assertEqual(sum(int(row["change_2019_2024"]) for row in analysis), national_change)
        self.assertEqual(national_change, 71079)

        california = next(row for row in analysis if row["state"] == "CA")
        illinois = next(row for row in analysis if row["state"] == "IL")
        self.assertEqual(california["change_2019_2024"], "-33282")
        self.assertEqual(california["level_driver"], "Undergraduate-led")
        self.assertEqual(california["top3_directional_share_pct"], "13.8")
        self.assertEqual(illinois["change_2019_2024"], "14464")
        self.assertEqual(illinois["level_driver"], "Graduate-led")

        rendered = (ROOT / "docs" / "STATE_RECOVERY_ANALYSIS.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "state-recovery.html").read_text(encoding="utf-8")
        self.assertIn("**33 states/DC**", rendered)
        self.assertIn("**27** were graduate-led", rendered)
        self.assertIn("By institutional control", rendered)
        self.assertIn("+71,079", rendered)
        self.assertIn("accounting, not causal attribution", html)
        self.assertIn("not automatically a campus opening or closure", html)

    def test_undergraduate_shift_baseline_is_fixed_broad_and_reconciled(self) -> None:
        analysis = rows(ROOT / "data" / "undergraduate_shift_baseline.csv")
        self.assertEqual(len(analysis), 51)
        self.assertEqual({row["state"] for row in analysis}, CORE_STATES)
        directions = Counter(row["undergraduate_direction"] for row in analysis)
        self.assertEqual(directions["Increase"], 45)
        self.assertEqual(directions["Decline"], 6)
        self.assertEqual(directions["Flat"], 0)

        for row in analysis:
            undergraduate = int(row["undergraduate_change"])
            graduate = int(row["graduate_change"])
            total = int(row["total_change"])
            self.assertEqual(undergraduate + graduate, total, row["state"])
            self.assertEqual(
                int(row["public_undergraduate_change"])
                + int(row["private_nonprofit_undergraduate_change"])
                + int(row["private_forprofit_undergraduate_change"]),
                undergraduate,
                row["state"],
            )
            self.assertEqual(
                int(row["continuing_undergraduate_change"])
                + int(row["entered_undergraduate_enrollment"])
                - int(row["exited_undergraduate_enrollment"]),
                undergraduate,
                row["state"],
            )
            self.assertEqual(int(row["undergraduate_accounting_net"]), undergraduate)
            if undergraduate:
                self.assertEqual(
                    int(row["directional_institution_movement"])
                    - int(row["offsetting_institution_movement"]),
                    abs(undergraduate),
                    row["state"],
                )
            self.assertGreaterEqual(float(row["top3_directional_share_pct"]), 0.0)
            self.assertLessEqual(float(row["top3_directional_share_pct"]), 100.0)

        self.assertEqual(sum(int(row["undergraduate_change"]) for row in analysis), 31592)
        self.assertEqual(sum(int(row["graduate_change"]) for row in analysis), -2053)
        self.assertEqual(sum(int(row["total_change"]) for row in analysis), 29539)
        self.assertEqual(sum(int(row["public_undergraduate_change"]) for row in analysis), 28580)
        self.assertEqual(
            sum(int(row["private_nonprofit_undergraduate_change"]) for row in analysis),
            3193,
        )
        self.assertEqual(
            sum(int(row["private_forprofit_undergraduate_change"]) for row in analysis),
            -181,
        )

        positive = sorted(
            (row for row in analysis if int(row["undergraduate_change"]) > 0),
            key=lambda row: int(row["positive_state_rank"]),
        )
        negative = [row for row in analysis if int(row["undergraduate_change"]) < 0]
        self.assertEqual(sum(int(row["undergraduate_change"]) for row in positive), 33778)
        self.assertEqual(-sum(int(row["undergraduate_change"]) for row in negative), 2186)
        self.assertEqual(sum(int(row["undergraduate_change"]) for row in positive[:5]), 18080)
        self.assertEqual(positive[4]["cumulative_positive_state_share_pct"], "53.53")

        by_state = {row["state"]: row for row in analysis}
        self.assertEqual(by_state["FL"]["undergraduate_change"], "6418")
        self.assertEqual(by_state["TX"]["undergraduate_change"], "6316")
        self.assertEqual(by_state["CA"]["undergraduate_change"], "-1490")

        agenda = {row["research_id"]: row for row in rows(ROOT / "data" / "research_agenda.csv")}
        self.assertEqual(agenda["R01"]["status"], "Baseline implemented; monitor next release")
        self.assertIn("at least 26 of 51 states/DC", agenda["R01"]["decision_rule"])

        rendered = (ROOT / "docs" / "UNDERGRADUATE_SHIFT_BASELINE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "undergraduate-shift.html").read_text(encoding="utf-8")
        self.assertIn("**+31,592**", rendered)
        self.assertIn("**45 of 51 states/DC**", rendered)
        self.assertIn("**third consecutive annual undergraduate increase**", rendered)
        self.assertIn("**20.6%**", rendered)
        self.assertIn("answer whether the shift persists", rendered)
        self.assertIn("does not establish persistence or causation", html)
        self.assertIn("remains fixed at 2023-2024", html)

    def test_private_nonprofit_growth_is_broadly_distributed_and_qa_gated(self) -> None:
        analysis = rows(ROOT / "data" / "private_nonprofit_growth.csv")
        self.assertEqual(len(analysis), 1831)
        controls = {
            int(row["year"]): row
            for row in self.controls
            if row["control"] == "Private nonprofit"
        }
        expected_2015 = int(controls[START_YEAR]["nonresident_enrollment"])
        expected_2024 = int(controls[END_YEAR]["nonresident_enrollment"])
        expected_net = expected_2024 - expected_2015
        self.assertEqual(expected_net, 82825)
        self.assertEqual(sum(int(row["nonresident_2015"]) for row in analysis), expected_2015)
        self.assertEqual(sum(int(row["nonresident_2024"]) for row in analysis), expected_2024)
        self.assertEqual(sum(int(row["change_2015_2024"]) for row in analysis), expected_net)
        self.assertEqual(sum(int(row["undergraduate_change"]) for row in analysis), -967)
        self.assertEqual(sum(int(row["graduate_change"]) for row in analysis), 83792)

        positive = [row for row in analysis if int(row["change_2015_2024"]) > 0]
        negative = [row for row in analysis if int(row["change_2015_2024"]) < 0]
        self.assertEqual(len(positive), 729)
        self.assertEqual(len(negative), 718)
        gross_positive = sum(int(row["change_2015_2024"]) for row in positive)
        gross_negative = -sum(int(row["change_2015_2024"]) for row in negative)
        self.assertEqual(gross_positive, 137578)
        self.assertEqual(gross_negative, 54753)
        self.assertEqual(gross_positive - gross_negative, expected_net)

        ranked = sorted(positive, key=lambda row: int(row["positive_rank"]))
        self.assertEqual([int(row["positive_rank"]) for row in ranked], list(range(1, 730)))
        top10 = ranked[:10]
        self.assertEqual(sum(int(row["change_2015_2024"]) for row in top10), 47503)
        self.assertEqual(top10[-1]["cumulative_positive_share_pct"], "34.53")
        self.assertLess(float(top10[-1]["cumulative_positive_share_pct"]), 50.0)
        self.assertEqual(top10[0]["institution"], "Trine University-Regional/Non-Traditional Campuses")

        by_unitid = {row["unitid"]: row for row in analysis}
        self.assertEqual(by_unitid["414878"]["narrative_gate"], "safe_with_context")
        self.assertEqual(by_unitid["156541"]["narrative_gate"], "hold_for_confirmation")
        self.assertEqual(by_unitid["179894"]["narrative_gate"], "safe_with_context")
        self.assertEqual(by_unitid["195173"]["narrative_gate"], "safe_with_context")
        self.assertEqual(by_unitid["175421"]["narrative_gate"], "safe_with_context")
        self.assertEqual(by_unitid["156365"]["narrative_gate"], "safe_with_context")
        self.assertEqual(
            by_unitid["488679"]["endpoint_status"],
            "Entered private-nonprofit endpoint universe",
        )

        agenda = {row["research_id"]: row for row in rows(ROOT / "data" / "research_agenda.csv")}
        self.assertEqual(agenda["R03"]["status"], "Implemented in private nonprofit growth analysis")
        self.assertIn("at least 50% of gross positive movement", agenda["R03"]["decision_rule"])
        rendered = (ROOT / "docs" / "PRIVATE_NONPROFIT_GROWTH.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "private-nonprofit-growth.html").read_text(encoding="utf-8")
        self.assertIn("**34.5%**", rendered)
        self.assertIn("**729** positive contributors", rendered)
        self.assertIn("Broadly distributed beyond the top 10", html)
        self.assertIn("Hold for confirmation", html)
        self.assertIn("Safe with context", html)

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
            "ipeds_race_ethnicity_definitions",
            "digest_306_10",
            "portal_national_data",
            "portal_methodology",
            "undocumented_higher_ed_2026",
            "immigrant_origin_2026",
            "undocumented_hs_graduates_2026",
        }
        self.assertTrue(essential_ids.issubset(set(ids)))
        self.assertTrue(all(row["url"].startswith("https://") for row in library))
        self.assertTrue(all(row["population_tags"].strip() for row in library))
        self.assertTrue(all(row["workflow_stage"].strip() for row in library))
        self.assertTrue(
            all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["last_checked"]) for row in library)
        )
        rendered = (ROOT / "docs" / "RESEARCH_LIBRARY.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "research-library.html").read_text(encoding="utf-8")
        for row in library:
            self.assertIn(row["title"], rendered)
            self.assertIn(row["url"], rendered)
            self.assertIn(html_module.escape(row["title"]), html)
            self.assertIn(html_module.escape(row["url"], quote=True), html)

    def test_research_library_public_interface(self) -> None:
        library = rows(ROOT / "data" / "research_library.csv")
        html = (ROOT / "site" / "research-library.html").read_text(encoding="utf-8")
        script = (ROOT / "site" / "research-library.js").read_text(encoding="utf-8")
        self.assertEqual(html.count('class="library-card"'), len(library))
        self.assertIn('id="library-search"', html)
        self.assertIn('id="library-population-filter"', html)
        self.assertIn('id="library-type-filter"', html)
        self.assertIn('id="library-publisher-filter"', html)
        self.assertIn('src="research-library.js"', html)
        self.assertIn("applyLibraryFilters", script)
        self.assertIn("card.hidden = !show", script)
        self.assertIn("matchesPopulation", script)

    def test_publication_handoff_tracks_validated_claims(self) -> None:
        handoff = rows(ROOT / "data" / "publication_handoff.csv")
        ids = [row["claim_id"] for row in handoff]
        self.assertEqual(len(handoff), 17)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"N01", "N05", "N06", "S01", "Q01", "Q02", "Q03", "M01", "M02", "P01", "G01", "B01"}.issubset(set(ids)))
        self.assertTrue(
            all(
                row["publication_status"]
                in {"READY", "READY WITH CONTEXT", "READY WITH CLAIM-LEVEL HOLDS"}
                for row in handoff
            )
        )
        library_ids = {row["resource_id"] for row in rows(ROOT / "data" / "research_library.csv")}
        self.assertTrue(all(row["research_library_id"] in library_ids for row in handoff))
        n01 = next(row for row in handoff if row["claim_id"] == "N01")
        self.assertIn(f"{self.findings['headline']['latest_nonresident']:,}", n01["public_copy"])
        n05 = next(row for row in handoff if row["claim_id"] == "N05")
        self.assertIn(f"{self.update_review['national']['absolute_change']:+,}", n05["public_copy"])
        n06 = next(row for row in handoff if row["claim_id"] == "N06")
        self.assertIn("+31,592", n06["public_copy"])
        self.assertIn("45 of 51 states/DC", n06["public_copy"])
        self.assertIn("does not answer persistence", n06["release_disclosure"])
        q01 = next(row for row in handoff if row["claim_id"] == "Q01")
        resolution = json.loads((ROOT / "data" / "qa_resolution_summary.json").read_text(encoding="utf-8"))
        self.assertIn(str(resolution["reviewed_count"]), q01["public_copy"])
        self.assertIn("11 safe with context", q01["public_copy"])
        self.assertIn("16 held for confirmation", q01["public_copy"])
        self.assertEqual(q01["publication_status"], "READY WITH CLAIM-LEVEL HOLDS")
        q02 = next(row for row in handoff if row["claim_id"] == "Q02")
        self.assertIn("226 unique UNITIDs", q02["public_copy"])
        self.assertIn("five medium/directory overlaps", q02["public_copy"])
        self.assertIn("no high/directory overlap", q02["public_copy"])
        self.assertIn("not a 2025 enrollment finding", q02["release_disclosure"])
        self.assertIn("revalidated", q02["release_disclosure"])
        self.assertEqual(q02["publication_status"], "READY WITH CONTEXT")
        q03 = next(row for row in handoff if row["claim_id"] == "Q03")
        self.assertIn("All 50 current medium-priority institution flags", q03["public_copy"])
        self.assertIn("28 percentage-movement", q03["public_copy"])
        self.assertIn("5 are safe with context", q03["public_copy"])
        self.assertIn("45 remain held for confirmation", q03["public_copy"])
        self.assertIn("data/medium_qa_resolution_log.csv", q03["authority"])
        self.assertIn("does not correct IPEDS values", q03["release_disclosure"])
        self.assertIn("standing approval", q03["release_disclosure"])
        self.assertEqual(q03["publication_status"], "READY WITH CLAIM-LEVEL HOLDS")
        m02 = next(row for row in handoff if row["claim_id"] == "M02")
        self.assertIn("not addable", m02["public_copy"])
        self.assertIn("no 2021-2023 undocumented trend", m02["public_copy"])
        p01 = next(row for row in handoff if row["claim_id"] == "P01")
        self.assertIn("70.7%", p01["public_copy"])
        self.assertIn("70.4%", p01["public_copy"])
        self.assertIn("not a college-going rate", p01["release_disclosure"])
        g01 = next(row for row in handoff if row["claim_id"] == "G01")
        self.assertIn("All 17 maintained Research Library sources", g01["public_copy"])
        self.assertIn("zero inferred internal deadlines", g01["public_copy"])
        rendered = (ROOT / "docs" / "PUBLICATION_HANDOFF.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "publication-handoff.html").read_text(encoding="utf-8")
        for row in handoff:
            self.assertIn(row["claim_id"], rendered)
            self.assertIn(row["public_copy"], rendered)
            self.assertIn(html_module.escape(row["public_copy"]), html)
        self.assertIn("does **not** represent the Presidents' Alliance's internal publication workflow", rendered)

    def test_public_release_register_enforces_allowlisted_publication(self) -> None:
        release_rows = read_public_release_register()
        self.assertEqual(len(release_rows), 70)
        ids = [row["artifact_id"] for row in release_rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["release_decision"] == "PUBLIC" for row in release_rows))
        self.assertTrue(all(row["person_level_data"] == "No" for row in release_rows))
        self.assertTrue(all(row["immigration_status_data"] == "No" for row in release_rows))
        self.assertTrue(all(not row["source_path"].startswith("data/raw/") for row in release_rows))
        self.assertTrue(all(row["public_path"].startswith("site/downloads/") for row in release_rows))
        pairs = expand_public_release_pairs(release_rows)
        self.assertEqual(len(pairs), 120)
        self.assertEqual(validate_public_tree(release_rows), 120)

        rendered = (ROOT / "docs" / "DATA_GOVERNANCE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "data-governance.html").read_text(encoding="utf-8")
        self.assertIn("Expanded public download files:** 120", rendered)
        self.assertIn("restricted by default", rendered)
        self.assertIn("Public by design does not mean publish everything.", html)
        self.assertIn("120</strong><span>expanded public download files", html)

        unsafe = [dict(row) for row in release_rows]
        unsafe[0]["person_level_data"] = "Yes"
        with self.assertRaisesRegex(RuntimeError, "Person-level or immigration-status data"):
            validate_register_rows(unsafe)
        unsafe = [dict(row) for row in release_rows]
        unsafe[0]["immigration_status_data"] = "Yes"
        with self.assertRaisesRegex(RuntimeError, "Person-level or immigration-status data"):
            validate_register_rows(unsafe)

        injected = ROOT / "site" / "downloads" / "__unregistered_release_test.tmp"
        try:
            injected.write_text("must be rejected", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Unregistered files"):
                validate_public_tree(release_rows)
        finally:
            injected.unlink(missing_ok=True)
        self.assertEqual(validate_public_tree(release_rows), 120)

    def test_release_readiness_separates_current_publication_from_year_advance(self) -> None:
        readiness = rows(ROOT / "data" / "release_readiness.csv")
        self.assertEqual(
            [row["gate_id"] for row in readiness],
            ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "Y01"],
        )
        self.assertEqual(len(readiness), 8)
        by_id = {row["gate_id"]: row for row in readiness}
        self.assertEqual(by_id["A03"]["status"], "PASS_WITH_CLAIM_HOLDS")
        self.assertEqual(by_id["A04"]["status"], "PASS_WITH_CLAIM_HOLDS")
        self.assertEqual(by_id["Y01"]["status"], "HOLD")
        self.assertEqual(by_id["Y01"]["blocks_current_release"], "No")
        self.assertEqual(by_id["Y01"]["blocks_year_advance"], "Yes")
        self.assertIn("27/27", by_id["A03"]["evidence"])
        self.assertIn("50/50", by_id["A03"]["evidence"])
        self.assertIn("70 artifact families", by_id["A05"]["evidence"])
        self.assertIn("2/4", by_id["Y01"]["evidence"])
        self.assertIn("candidate directory preflight=PASS", by_id["Y01"]["evidence"])
        self.assertIn("3,864 directory-eligible rows", by_id["Y01"]["evidence"])
        self.assertIn("154 institution change-review rows", by_id["Y01"]["evidence"])
        self.assertIn("226 carry-forward QA rows", by_id["Y01"]["evidence"])
        self.assertIn("5 medium-priority/directory overlaps", by_id["Y01"]["evidence"])
        self.assertTrue(
            all(
                row["status"] != "HOLD"
                for row in readiness
                if row["blocks_current_release"] == "Yes"
            )
        )
        rendered = (ROOT / "docs" / "RELEASE_READINESS.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "release-readiness.html").read_text(encoding="utf-8")
        self.assertIn("`READY_WITH_CLAIM_LEVEL_HOLDS`", rendered)
        self.assertIn("`HOLD_YEAR_ADVANCE`", rendered)
        self.assertIn("partial candidate-year package blocks changing `END_YEAR`", rendered)
        self.assertEqual(html.count('data-readiness-gate="'), 8)
        self.assertIn("READY_WITH_CLAIM_LEVEL_HOLDS", html)
        self.assertIn("HOLD_YEAR_ADVANCE", html)
        self.assertIn("61</strong><span>institution-specific claims still held", html)

    def test_freshness_monitor_preserves_release_gate_and_trigger_boundaries(self) -> None:
        snapshot = json.loads(
            (ROOT / "data" / "release_monitor_snapshot.json").read_text(encoding="utf-8")
        )
        self.assertEqual(snapshot["current_analysis_end_year"], 2024)
        self.assertEqual(snapshot["candidate_next_year"], 2025)
        self.assertFalse(snapshot["fall_enrollment_ready"])
        self.assertTrue(snapshot["directory_ready"])
        self.assertFalse(snapshot["package_ready"])
        self.assertEqual(snapshot["release_decision"], "HOLD_YEAR_ADVANCE")
        self.assertEqual(len(snapshot["files"]), 4)
        availability = {row["file"]: row["available"] for row in snapshot["files"]}
        self.assertFalse(availability["EF2025A.zip"])
        self.assertFalse(availability["EF2025A_Dict.zip"])
        self.assertTrue(availability["HD2025.zip"])
        self.assertTrue(availability["HD2025_Dict.zip"])

        monitor = rows(ROOT / "data" / "freshness_monitor.csv")
        self.assertEqual(len(monitor), 11)
        self.assertEqual(
            [row["monitor_id"] for row in monitor[:6]],
            ["R01", "R02", "R03", "R04", "D01", "G01"],
        )
        directory = next(row for row in monitor if row["monitor_id"] == "D01")
        self.assertEqual(directory["status"], "PASS")
        self.assertIn("6/6 required directory fields preserved", directory["evidence"])
        self.assertIn("70/70 full data/dictionary fields align", directory["evidence"])
        self.assertIn("3,864 directory-eligible rows", directory["evidence"])
        self.assertIn("3,812 shared UNITIDs", directory["evidence"])
        self.assertIn("net eligible change -4", directory["evidence"])
        self.assertIn("154 affected UNITIDs", directory["evidence"])
        gate = next(row for row in monitor if row["monitor_id"] == "G01")
        self.assertEqual(gate["status"], "HOLD YEAR ADVANCE")
        self.assertIn("2/4 required candidate-year files available", gate["evidence"])
        self.assertIn("Keep END_YEAR=2024", gate["next_action"])
        self.assertEqual(sum(row["monitor_area"] == "Recurring product" for row in monitor), 3)

        rendered = (ROOT / "docs" / "FRESHNESS_MONITOR.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "freshness-monitor.html").read_text(encoding="utf-8")
        self.assertIn("dated portfolio monitoring snapshot", rendered.lower())
        self.assertIn("dates are not inferred", rendered)
        self.assertIn("not continuously live", html)
        self.assertIn("HOLD YEAR ADVANCE", html)
        self.assertIn("Candidate directory preflight", html)
        self.assertIn("3,864", html)
        self.assertIn("3,812", html)
        self.assertIn("154", html)
        self.assertIn("612", html)
        self.assertIn("226", html)
        self.assertIn("5 medium-priority rows overlap the directory changes", html)
        self.assertEqual(html.count('data-monitor-id="'), 4)
        self.assertEqual(html.count('data-product-monitor="'), 3)

    def test_candidate_directory_preflight_is_structural_and_non_authorizing(self) -> None:
        payload = json.loads(
            (ROOT / "data" / "candidate_directory_preflight.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["current_analysis_end_year"], 2024)
        self.assertEqual(payload["candidate_next_year"], 2025)
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["year_advance_authorized"])
        self.assertEqual(payload["release_monitor_decision"], "HOLD_YEAR_ADVANCE")
        self.assertEqual(payload["candidate_directory_rows"], 5_985)
        self.assertEqual(payload["candidate_field_count"], 70)
        self.assertEqual(payload["candidate_dictionary_variable_count"], 70)
        self.assertTrue(payload["candidate_full_field_dictionary_match"])
        self.assertEqual(payload["candidate_fields_missing_from_dictionary"], [])
        self.assertEqual(payload["candidate_dictionary_variables_missing_from_data"], [])
        self.assertEqual(payload["candidate_core_states_dc_count"], 51)
        self.assertEqual(payload["candidate_duplicate_unitid_count"], 0)
        self.assertEqual(payload["candidate_directory_eligible_rows"], 3_864)
        self.assertEqual(
            payload["candidate_control_counts"],
            {"Public": 1_644, "Private nonprofit": 1_577, "Private for-profit": 643},
        )
        current = payload["current_reference"]
        self.assertEqual(current["directory_rows"], 6_072)
        self.assertEqual(current["field_count"], 72)
        self.assertEqual(current["directory_eligible_rows"], 3_868)
        self.assertEqual(
            current["control_counts"],
            {"Public": 1_642, "Private nonprofit": 1_578, "Private for-profit": 648},
        )
        continuity = payload["eligible_universe_continuity"]
        self.assertEqual(continuity["shared_unitids"], 3_812)
        self.assertEqual(continuity["entering_unitids"], 52)
        self.assertEqual(continuity["leaving_unitids"], 56)
        self.assertEqual(continuity["net_change"], -4)
        self.assertEqual(continuity["shared_control_changes"], 6)
        self.assertEqual(continuity["shared_state_changes"], 3)
        self.assertEqual(continuity["shared_name_changes"], 41)
        schema = payload["schema_delta"]
        self.assertEqual(schema["field_count_change"], -2)
        self.assertEqual(schema["removed_fields"], ["DFRCGID", "DFRCUSCG"])
        self.assertEqual(schema["added_fields"], [])
        self.assertTrue(schema["required_fields_preserved"])
        review = payload["change_review"]
        self.assertEqual(review["csv_path"], "data/candidate_directory_change_review.csv")
        self.assertEqual(review["row_count"], 154)
        self.assertEqual(review["entered_directory_eligible"], 52)
        self.assertEqual(review["left_directory_eligible"], 56)
        self.assertEqual(review["shared_attribute_change_rows"], 46)
        self.assertEqual(
            review["entry_reason_counts"],
            {
                "degree_granting_status_gained": 11,
                "new_directory_record": 35,
                "title_iv_first_look_status_gained": 6,
            },
        )
        self.assertEqual(
            review["exit_reason_counts"],
            {
                "degree_granting_status_lost": 3,
                "directory_record_absent": 15,
                "title_iv_first_look_status_lost": 38,
            },
        )
        self.assertEqual(review["current_analysis_present_leavers"], 54)
        self.assertEqual(review["current_nonresident_exposure_leavers"], 612)
        self.assertEqual(review["current_total_enrollment_exposure_leavers"], 17_593)
        self.assertEqual(review["current_nonresident_exposure_control_changes"], 1_069)
        self.assertEqual(review["current_nonresident_exposure_state_changes"], 193)
        self.assertEqual(review["current_nonresident_exposure_name_changes"], 10_184)
        review_bytes = (ROOT / "data" / "candidate_directory_change_review.csv").read_bytes()
        self.assertEqual(hashlib.sha256(review_bytes).hexdigest(), review["csv_sha256"])
        source = payload["candidate_source"]
        self.assertEqual(
            source["data_sha256"],
            "aadad9277a2255c85813b6d206475ddbf8a7330d79cc0236c2ecae685b00f1bf",
        )
        self.assertEqual(
            source["dictionary_sha256"],
            "dc454aa6fbc246f3d47d773cd02ebe3b5efcedacbd2f71c54ff39f5844215343",
        )
        rendered = (ROOT / "docs" / "CANDIDATE_DIRECTORY_PREFLIGHT.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "candidate-directory-preflight.html").read_text(encoding="utf-8")
        for expected in ("6/6", "70/70", "3,864", "3,812", "52", "56", "154", "612", "-4", "DFRCGID", "DFRCUSCG"):
            self.assertIn(expected, rendered)
            self.assertIn(expected, html)
        self.assertIn("not the final analytic universe", rendered)
        self.assertIn("No 2025 enrollment claims yet", html)
        self.assertIn("HOLD_YEAR_ADVANCE", html)

    def test_candidate_directory_change_review_is_hashed_reconciled_and_non_predictive(self) -> None:
        review_rows = rows(ROOT / "data" / "candidate_directory_change_review.csv")
        self.assertEqual(len(review_rows), 154)
        self.assertEqual(len({row["unitid"] for row in review_rows}), 154)
        class_counts = Counter(row["change_class"] for row in review_rows)
        self.assertEqual(
            class_counts,
            Counter(
                {
                    "LEFT_DIRECTORY_ELIGIBLE": 56,
                    "ENTERED_DIRECTORY_ELIGIBLE": 52,
                    "SHARED_ATTRIBUTE_CHANGE": 46,
                }
            ),
        )
        entry_reasons = Counter(
            reason
            for row in review_rows
            if row["change_class"] == "ENTERED_DIRECTORY_ELIGIBLE"
            for reason in row["change_reasons"].split(";")
        )
        self.assertEqual(
            entry_reasons,
            Counter(
                {
                    "new_directory_record": 35,
                    "degree_granting_status_gained": 11,
                    "title_iv_first_look_status_gained": 6,
                }
            ),
        )
        exit_reasons = Counter(
            reason
            for row in review_rows
            if row["change_class"] == "LEFT_DIRECTORY_ELIGIBLE"
            for reason in row["change_reasons"].split(";")
        )
        self.assertEqual(
            exit_reasons,
            Counter(
                {
                    "title_iv_first_look_status_lost": 38,
                    "directory_record_absent": 15,
                    "degree_granting_status_lost": 3,
                }
            ),
        )
        leavers = [row for row in review_rows if row["change_class"] == "LEFT_DIRECTORY_ELIGIBLE"]
        self.assertEqual(sum(row["current_analysis_present"] == "Yes" for row in leavers), 54)
        self.assertEqual(sum(int(row["current_nonresident_enrollment"] or 0) for row in leavers), 612)
        self.assertEqual(sum(int(row["current_total_enrollment"] or 0) for row in leavers), 17_593)

        shared = [row for row in review_rows if row["change_class"] == "SHARED_ATTRIBUTE_CHANGE"]
        self.assertEqual(sum(row["control_changed"] == "Yes" for row in shared), 6)
        self.assertEqual(sum(row["state_changed"] == "Yes" for row in shared), 3)
        self.assertEqual(sum(row["name_changed"] == "Yes" for row in shared), 41)
        self.assertEqual(
            sum(int(row["current_nonresident_enrollment"] or 0) for row in shared if row["control_changed"] == "Yes"),
            1_069,
        )
        self.assertEqual(
            sum(int(row["current_nonresident_enrollment"] or 0) for row in shared if row["state_changed"] == "Yes"),
            193,
        )
        self.assertEqual(
            sum(int(row["current_nonresident_enrollment"] or 0) for row in shared if row["name_changed"] == "Yes"),
            10_184,
        )

        by_unitid = {row["unitid"]: row for row in review_rows}
        grand_canyon = by_unitid["104717"]
        self.assertEqual(grand_canyon["current_control"], "Private for-profit")
        self.assertEqual(grand_canyon["candidate_control"], "Private nonprofit")
        self.assertEqual(grand_canyon["current_nonresident_enrollment"], "967")
        ua_global = by_unitid["154022"]
        self.assertEqual(ua_global["current_control"], "Private for-profit")
        self.assertEqual(ua_global["candidate_control"], "Public")
        self.assertEqual((ua_global["current_state"], ua_global["candidate_state"]), ("CA", "AZ"))
        self.assertEqual(ua_global["current_nonresident_enrollment"], "96")
        houston = by_unitid["225423"]
        self.assertEqual(houston["current_institution"], "Houston Community College")
        self.assertEqual(houston["candidate_institution"], "Houston City College")
        self.assertEqual(houston["current_nonresident_enrollment"], "4670")
        fidm = by_unitid["114354"]
        self.assertEqual(fidm["change_class"], "LEFT_DIRECTORY_ELIGIBLE")
        self.assertEqual(fidm["current_nonresident_enrollment"], "128")
        self.assertTrue(
            all("do not infer institutional opening/closure or 2025 enrollment movement" in row["interpretation_boundary"] for row in review_rows)
        )

        review_path = ROOT / "data" / "candidate_directory_change_review.csv"
        original_review = review_path.read_bytes()
        try:
            review_path.write_bytes(original_review + b"\n")
            with self.assertRaisesRegex(RuntimeError, "SHA-256"):
                validate_candidate_directory_change_review()
        finally:
            review_path.write_bytes(original_review)
        validate_candidate_directory_change_review()

        rendered = (ROOT / "docs" / "CANDIDATE_DIRECTORY_CHANGE_REVIEW.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "candidate-directory-changes.html").read_text(encoding="utf-8")
        for expected in ("154", "52", "56", "612", "17,593", "1,069", "193", "10,184", "Grand Canyon University", "Houston City College"):
            self.assertIn(expected, rendered)
            self.assertIn(expected, html)
        self.assertIn("not projected 2025 losses", rendered)
        self.assertIn("not enrollment findings", html)
        self.assertIn("HOLD_YEAR_ADVANCE", html)

    def test_candidate_year_qa_watchlist_reconciles_current_and_candidate_signals(self) -> None:
        watchlist = rows(ROOT / "data" / "candidate_year_qa_watchlist.csv")
        self.assertEqual(len(watchlist), 226)
        self.assertEqual(len({row["unitid"] for row in watchlist}), 226)
        self.assertEqual([int(row["review_order"]) for row in watchlist], list(range(1, 227)))

        groups = Counter(row["carry_forward_group"] for row in watchlist)
        self.assertEqual(
            groups,
            Counter(
                {
                    "CURRENT_HIGH_PRIORITY": 27,
                    "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE": 5,
                    "CURRENT_MEDIUM_PRIORITY": 45,
                    "CANDIDATE_DIRECTORY_CHANGE_ONLY": 149,
                }
            ),
        )
        self.assertEqual(groups["CURRENT_HIGH_PLUS_DIRECTORY_CHANGE"], 0)
        self.assertEqual(sum(row["current_review_priority"] == "high" for row in watchlist), 27)
        self.assertEqual(sum(row["current_review_priority"] == "medium" for row in watchlist), 50)
        self.assertEqual(sum(bool(row["candidate_change_class"]) for row in watchlist), 154)

        high = [row for row in watchlist if row["current_review_priority"] == "high"]
        self.assertEqual(
            Counter(row["high_priority_publication_class"] for row in high),
            Counter({"hold_for_confirmation": 16, "safe_with_context": 11}),
        )
        medium = [row for row in watchlist if row["current_review_priority"] == "medium"]
        self.assertTrue(all(not row["high_priority_publication_class"] for row in medium))
        self.assertEqual(
            Counter(row["medium_priority_publication_class"] for row in medium),
            Counter({"hold_for_confirmation": 45, "safe_with_context": 5}),
        )
        self.assertTrue(all(not row["medium_priority_publication_class"] for row in high))

        overlap = [
            row for row in watchlist
            if row["carry_forward_group"] == "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE"
        ]
        self.assertEqual(
            {row["unitid"] for row in overlap},
            {"157216", "114354", "115773", "244233", "417327"},
        )
        self.assertEqual(sum(int(row["current_2024_nonresident"] or 0) for row in overlap), 2_443)

        candidate_only = [
            row for row in watchlist
            if row["carry_forward_group"] == "CANDIDATE_DIRECTORY_CHANGE_ONLY"
        ]
        self.assertEqual(len(candidate_only), 149)
        self.assertEqual(
            sum(int(row["current_2024_nonresident"] or 0) for row in candidate_only),
            9_326,
        )

        by_unitid = {row["unitid"]: row for row in watchlist}
        lindsey = by_unitid["157216"]
        self.assertEqual(lindsey["carry_forward_group"], "CURRENT_MEDIUM_PLUS_DIRECTORY_CHANGE")
        self.assertEqual(lindsey["latest_release_change"], "590")
        self.assertEqual(lindsey["candidate_change_reasons"], "institution_name_changed")
        self.assertEqual(lindsey["current_2024_nonresident"], "2027")
        fidm = by_unitid["114354"]
        self.assertEqual(fidm["latest_release_change"], "-166")
        self.assertEqual(fidm["candidate_change_class"], "LEFT_DIRECTORY_ELIGIBLE")
        self.assertEqual(fidm["current_2024_nonresident"], "128")
        houston = by_unitid["225423"]
        self.assertEqual(houston["carry_forward_group"], "CANDIDATE_DIRECTORY_CHANGE_ONLY")
        self.assertEqual(houston["current_institution"], "Houston Community College")
        self.assertEqual(houston["candidate_institution"], "Houston City College")
        self.assertEqual(houston["current_2024_nonresident"], "4670")
        grand_canyon = by_unitid["104717"]
        self.assertEqual(grand_canyon["current_control"], "Private for-profit")
        self.assertEqual(grand_canyon["candidate_control"], "Private nonprofit")
        self.assertEqual(grand_canyon["current_2024_nonresident"], "967")
        self.assertEqual(by_unitid["156541"]["high_priority_publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["414878"]["high_priority_publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["228459"]["medium_priority_publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["157216"]["medium_priority_publication_class"], "hold_for_confirmation")
        self.assertTrue(
            all(
                not row["high_priority_publication_class"] and not row["medium_priority_publication_class"]
                for row in candidate_only
            )
        )
        self.assertTrue(
            all(
                "do not infer 2025 enrollment movement, institutional opening/closure" in row["interpretation_boundary"]
                and "Reassess against the full 2025 Fall Enrollment package" in row["interpretation_boundary"]
                for row in watchlist
            )
        )

        rendered = (ROOT / "docs" / "CANDIDATE_YEAR_QA_WATCHLIST.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "candidate-year-watchlist.html").read_text(encoding="utf-8")
        for expected in (
            "226",
            "2,443",
            "9,326",
            "Lindsey Wilson College",
            "Houston City College",
            "Grand Canyon University",
        ):
            self.assertIn(expected, rendered)
            self.assertIn(expected, html)
        self.assertIn("rather than inventing a new risk score", rendered)
        self.assertIn("not standing approval", html)
        self.assertIn("Carry forward the question, not the answer.", html)

    def test_medium_priority_review_routes_existing_signals_without_clearance(self) -> None:
        review = rows(ROOT / "data" / "medium_priority_review.csv")
        self.assertEqual(len(review), 50)
        self.assertEqual(len({row["unitid"] for row in review}), 50)
        self.assertEqual([int(row["review_order"]) for row in review], list(range(1, 51)))

        routes = Counter(row["review_route"] for row in review)
        self.assertEqual(
            routes,
            Counter(
                {
                    "PERCENTAGE_MOVEMENT": 28,
                    "ABSOLUTE_MOVEMENT": 11,
                    "ABSOLUTE_AND_PERCENTAGE": 8,
                    "STRUCTURAL_OR_REPORTING": 3,
                }
            ),
        )
        self.assertEqual(
            Counter(row["status"] for row in review),
            Counter({"Continuing": 49, "Entered analytic universe": 1}),
        )
        self.assertEqual(
            Counter(row["control"] for row in review),
            Counter({"Public": 24, "Private nonprofit": 22, "Private for-profit": 4}),
        )

        gains = [int(row["absolute_change"]) for row in review if int(row["absolute_change"]) > 0]
        declines = [int(row["absolute_change"]) for row in review if int(row["absolute_change"]) < 0]
        zero = [row for row in review if int(row["absolute_change"]) == 0]
        self.assertEqual((len(gains), len(declines), len(zero)), (25, 23, 2))
        self.assertEqual(sum(gains), 7_806)
        self.assertEqual(-sum(declines), 9_241)
        self.assertEqual(sum(gains) + sum(declines), -1_435)
        self.assertEqual(sum(abs(int(row["absolute_change"])) for row in review), 17_047)

        overlap = [row for row in review if row["candidate_directory_overlap"] == "yes"]
        self.assertEqual(len(overlap), 5)
        self.assertEqual(
            {row["unitid"] for row in overlap},
            {"157216", "114354", "115773", "244233", "417327"},
        )
        self.assertEqual(sum(int(row["nonresident_2024"] or 0) for row in overlap), 2_443)

        structural = [row for row in review if row["review_route"] == "STRUCTURAL_OR_REPORTING"]
        self.assertEqual({row["unitid"] for row in structural}, {"159948", "244233", "417327"})
        by_unitid = {row["unitid"]: row for row in review}
        self.assertEqual(by_unitid["159948"]["status"], "Entered analytic universe")
        self.assertEqual(by_unitid["244233"]["flag_2023"], "R")
        self.assertEqual(by_unitid["244233"]["flag_2024"], "P")
        self.assertEqual(by_unitid["417327"]["flag_2023"], "R")
        self.assertEqual(by_unitid["417327"]["flag_2024"], "P")
        self.assertEqual(by_unitid["157216"]["review_route"], "ABSOLUTE_AND_PERCENTAGE")
        self.assertEqual(by_unitid["114354"]["review_route"], "PERCENTAGE_MOVEMENT")
        self.assertTrue(all("publication clearance" in row["interpretation_boundary"] for row in review))
        self.assertTrue(all(row["next_review_step"].strip() for row in review))

        rendered = (ROOT / "docs" / "MEDIUM_PRIORITY_REVIEW.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "medium-priority-review.html").read_text(encoding="utf-8")
        self.assertIn("50 current medium-priority", rendered)
        self.assertIn("<strong>50</strong><span>current medium-priority rows", html)
        for expected in (
            "28 rows",
            "11 rows",
            "8 rows",
            "3 rows",
            "2,443",
            "+7,806",
            "-9,241",
            "17,047",
            "-1,435",
            "New Orleans Baptist Theological Seminary",
            "Lindsey Wilson College",
        ):
            self.assertIn(expected, rendered)
            self.assertIn(expected, html)
        self.assertIn("not a national trend estimate", rendered)
        self.assertIn("none is a severity grade", html)
        self.assertIn("No automatic clearance", html)

    def test_medium_qa_resolution_log_covers_every_medium_flag(self) -> None:
        routing = rows(ROOT / "data" / "medium_priority_review.csv")
        resolution = rows(ROOT / "data" / "medium_qa_resolution_log.csv")
        self.assertEqual(len(resolution), 50)
        self.assertEqual(
            [row["unitid"] for row in resolution],
            [row["unitid"] for row in routing],
        )
        self.assertEqual(
            Counter(row["publication_class"] for row in resolution),
            Counter({"hold_for_confirmation": 45, "safe_with_context": 5}),
        )
        safe_unitids = {
            row["unitid"] for row in resolution if row["publication_class"] == "safe_with_context"
        }
        self.assertEqual(safe_unitids, {"110635", "139755", "151111", "228459", "230782"})
        self.assertTrue(all(row["evidence_url"].startswith("https://") for row in resolution))
        self.assertTrue(all(row["analyst_note"].strip() for row in resolution))

        by_unitid = {row["unitid"]: row for row in resolution}
        self.assertEqual(by_unitid["228459"]["disposition"], "corroborated_external_count")
        self.assertEqual(by_unitid["151111"]["disposition"], "expected_structural_change")
        self.assertEqual(by_unitid["126614"]["disposition"], "external_scope_mismatch")
        self.assertIn("student-stats2024.pdf", by_unitid["110635"]["evidence_url"])

        summary = json.loads(
            (ROOT / "data" / "medium_qa_resolution_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(summary["reviewed_count"], 50)
        self.assertEqual(summary["coverage_pct"], 100.0)
        self.assertEqual(summary["safe_with_context"], 5)
        self.assertEqual(summary["hold_for_confirmation"], 45)
        self.assertTrue(summary["required_medium_priority_covered"])
        self.assertEqual(summary["candidate_overlap_reviewed"], 5)

        rendered = (ROOT / "docs" / "MEDIUM_QA_RESOLUTION_LOG.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "medium-qa-review.html").read_text(encoding="utf-8")
        for expected in (
            "50/50 current medium-priority institution flags",
            "Safe with context:** 5",
            "Held for confirmation:** 45",
            "Texas State University",
            "University of California-Berkeley",
            "not standing approval for the next release",
        ):
            self.assertIn(expected, rendered)
        self.assertIn("50/50</strong><span>medium-priority records reviewed", html)
        self.assertIn("Five records have enough corroboration", html)
        self.assertIn("not standing approval for a future release", html)
        self.assertEqual(html.count('target="_blank"'), 50)

    def test_planning_scenarios_reconcile_and_remain_non_predictive(self) -> None:
        scenario_rows = rows(ROOT / "data" / "planning_scenarios.csv")
        self.assertEqual(
            [row["case_id"] for row in scenario_rows],
            ["BT01", "PS01", "PS02", "PS03"],
        )
        self.assertTrue(all(row["status"] == "PASS" for row in scenario_rows))

        backtest = scenario_rows[0]
        self.assertEqual(backtest["planned_value"], "1088197")
        self.assertEqual(backtest["actual_value"], "1044137")
        self.assertEqual(backtest["variance"], "-44060")
        self.assertEqual(backtest["variance_pct"], "-4.05")

        forward = scenario_rows[1:]
        self.assertEqual(
            [row["planned_value"] for row in forward],
            ["1058964", "1074536", "1086816"],
        )
        self.assertTrue(all(row["actual_value"] == "" for row in forward))
        self.assertTrue(all(row["variance"] == "" for row in forward))

        rendered = (ROOT / "docs" / "PLANNING_SCENARIOS.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "planning-scenarios.html").read_text(encoding="utf-8")
        self.assertIn("not a predictive forecast", rendered.lower())
        self.assertIn("not a predictive model", html)
        self.assertIn("-44,060", rendered)
        self.assertIn("1,058,964 to 1,086,816", rendered)
        self.assertEqual(html.count('data-scenario-id="'), 3)

    def test_ad_hoc_analysis_casebook_is_reproducible_and_explicitly_simulated(self) -> None:
        case_rows = rows(ROOT / "data" / "ad_hoc_analysis_results.csv")
        self.assertEqual([row["case_id"] for row in case_rows], ["A01", "A02", "A03"])
        self.assertTrue(all(row["status"] == "PASS" for row in case_rows))

        a01 = next(row for row in case_rows if row["case_id"] == "A01")
        self.assertEqual(a01["primary_answer"], "18 states/DC remain below 2019.")
        self.assertIn("-56,517", a01["response_detail"])
        self.assertIn("86.5%", a01["response_detail"])
        self.assertIn("CA -33,282", a01["response_detail"])

        a02 = next(row for row in case_rows if row["case_id"] == "A02")
        self.assertIn("+17,753", a02["primary_answer"])
        self.assertIn("60.1%", a02["primary_answer"])
        self.assertIn("+29,539 = +29,539", a02["qa_check"])

        a03 = next(row for row in case_rows if row["case_id"] == "A03")
        self.assertIn("82,825", a03["primary_answer"])
        self.assertIn("Public -16,087", a03["response_detail"])
        self.assertIn("+63,400 = +63,400", a03["qa_check"])

        rendered = (ROOT / "docs" / "AD_HOC_ANALYSIS.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "ad-hoc-analysis.html").read_text(encoding="utf-8")
        self.assertIn("portfolio simulation", rendered.lower())
        self.assertIn("not client requests", rendered)
        self.assertIn("not real client requests", html)
        self.assertEqual(html.count('data-case-id="'), 3)
        for row in case_rows:
            self.assertIn(row["business_question"], rendered)
            self.assertIn(html_module.escape(row["business_question"]), html)

    def test_sql_analysis_executes_and_reconciles(self) -> None:
        specs = read_sql_queries()
        self.assertEqual(tuple(spec.query_id for spec in specs), EXPECTED_QUERY_IDS)
        sql_text = (ROOT / "sql" / "portfolio_queries.sql").read_text(encoding="utf-8").upper()
        for keyword in ("WITH", "LAG(", "RANK()", "JOIN", "CASE", "SUM("):
            self.assertIn(keyword, sql_text)

        audit = rows(ROOT / "data" / "sql_analysis_audit.csv")
        self.assertEqual([row["query_id"] for row in audit], list(EXPECTED_QUERY_IDS))
        self.assertEqual(len(audit), 6)
        self.assertTrue(all(row["status"] == "PASS" for row in audit))
        self.assertEqual(next(row for row in audit if row["query_id"] == "Q01")["observed_value"], "29539")
        self.assertEqual(next(row for row in audit if row["query_id"] == "Q02")["observed_value"], "33")
        self.assertEqual(next(row for row in audit if row["query_id"] == "Q05")["observed_value"], "66981|-3581|63400")
        self.assertEqual(next(row for row in audit if row["query_id"] == "Q06")["observed_value"], "0")

        rendered = (ROOT / "docs" / "SQL_ANALYSIS.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "sql-analysis.html").read_text(encoding="utf-8")
        self.assertIn("**Query checks passed:** 6/6", rendered)
        self.assertIn("SQLite database on every run", rendered)
        for spec in specs:
            self.assertIn(spec.title, rendered)
            self.assertIn(html_module.escape(spec.title), html)
        self.assertIn('href="downloads/portfolio_queries.sql"', html)

        connection = build_sql_connection()
        try:
            self.assertEqual(connection.execute("PRAGMA query_only").fetchone()[0], 1)
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM national_year")
        finally:
            connection.close()

        with tempfile.TemporaryDirectory() as temp_dir:
            unsafe = Path(temp_dir) / "unsafe.sql"
            unsafe.write_text(
                "-- QUERY: Q01 | Unsafe | mutation\nDELETE FROM national_year;\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "non-read-only"):
                read_sql_queries(unsafe)

    def test_research_agenda_is_structured_and_rendered(self) -> None:
        agenda = rows(ROOT / "data" / "research_agenda.csv")
        self.assertGreaterEqual(len(agenda), 6)
        ids = [row["research_id"] for row in agenda]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"R01", "R02", "R04", "R05"}.issubset(set(ids)))
        self.assertTrue(all(row["priority"] in {"High", "Medium", "Low"} for row in agenda))
        self.assertTrue(any(row["current_ipeds_fit"] == "None" for row in agenda))
        self.assertTrue(any(row["current_ipeds_fit"] == "High" for row in agenda))
        r04 = next(row for row in agenda if row["research_id"] == "R04")
        self.assertEqual(
            r04["status"],
            "Implemented as bounded national population trend comparison",
        )
        self.assertIn("not addable", r04["decision_rule"].lower())
        r01 = next(row for row in agenda if row["research_id"] == "R01")
        self.assertEqual(r01["status"], "Baseline implemented; monitor next release")
        self.assertEqual(
            r01["proposed_output"],
            "Undergraduate shift baseline and next-release update",
        )
        self.assertIn("at least 26 of 51 states/DC", r01["decision_rule"])
        r02 = next(row for row in agenda if row["research_id"] == "R02")
        self.assertEqual(r02["status"], "Implemented in state recovery analysis")
        self.assertEqual(r02["proposed_output"], "State recovery decomposition brief")
        r07 = next(row for row in agenda if row["research_id"] == "R07")
        self.assertEqual(r07["status"], "Implemented as source-update triage register")
        self.assertEqual(r07["proposed_output"], "Source-update triage register and routing note")
        r06 = next(row for row in agenda if row["research_id"] == "R06")
        self.assertEqual(r06["status"], "Implemented as bounded 2023 state pipeline context")
        self.assertEqual(r06["proposed_output"], "2023 undocumented pipeline context note")
        self.assertIn("do not interpret", r06["decision_rule"].lower())
        r08 = next(row for row in agenda if row["research_id"] == "R08")
        self.assertEqual(r08["status"], "Implemented as candidate-year QA carry-forward watchlist")
        self.assertEqual(r08["proposed_output"], "Candidate-year QA carry-forward watchlist")
        self.assertIn("revalidated rather than inherited", r08["decision_rule"])
        self.assertIn("five medium-priority records overlap", r08["evidence_trigger"])
        r09 = next(row for row in agenda if row["research_id"] == "R09")
        self.assertEqual(r09["status"], "Implemented as medium-priority QA triage and evidence review")
        self.assertEqual(r09["proposed_output"], "Medium-priority institution QA routing and evidence review")
        self.assertIn("exactly one non-severity route", r09["decision_rule"])
        self.assertIn("exactly one evidence-backed publication class", r09["decision_rule"])
        self.assertIn("28 are percentage-movement cases", r09["evidence_trigger"])
        self.assertIn("clears 5 only", r09["evidence_trigger"])
        rendered = (ROOT / "docs" / "RESEARCH_AGENDA.md").read_text(encoding="utf-8")
        for row in agenda:
            self.assertIn(row["research_id"], rendered)
            self.assertIn(row["question"], rendered)

    def test_source_update_triage_covers_library_and_routes_material_changes(self) -> None:
        library = rows(ROOT / "data" / "research_library.csv")
        triage = rows(ROOT / "data" / "source_update_triage.csv")
        self.assertEqual(len(library), 17)
        self.assertEqual(len(triage), 17)
        self.assertEqual(
            {row["resource_id"] for row in triage},
            {row["resource_id"] for row in library},
        )
        counts = Counter(row["baseline_route"] for row in triage)
        self.assertEqual(counts["ROUTINE_REFRESH"], 8)
        self.assertEqual(counts["METHODOLOGY_REVIEW"], 3)
        self.assertEqual(counts["RESEARCH_QUESTION_REVIEW"], 2)
        self.assertEqual(counts["GOVERNANCE_REVIEW"], 1)
        self.assertEqual(counts["MONITOR_ONLY"], 1)
        self.assertEqual(counts["ARCHIVAL_REFERENCE"], 2)

        by_id = {row["resource_id"]: row for row in triage}
        self.assertEqual(
            by_id["portal_methodology"]["baseline_route"],
            "METHODOLOGY_REVIEW",
        )
        self.assertEqual(
            by_id["portal_national_data"]["baseline_route"],
            "RESEARCH_QUESTION_REVIEW",
        )
        self.assertEqual(
            by_id["tuition_equity_privacy_2026"]["baseline_route"],
            "GOVERNANCE_REVIEW",
        )
        self.assertTrue(all(row["methodology_escalation"].strip() for row in triage))
        self.assertTrue(all(row["research_question_escalation"].strip() for row in triage))

        rendered = (ROOT / "docs" / "SOURCE_UPDATE_TRIAGE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "source-update-triage.html").read_text(encoding="utf-8")
        self.assertIn("17/17 resources", rendered)
        self.assertIn("Inferred deadlines:** 0", rendered)
        self.assertIn("newer file or publication date alone", rendered)
        self.assertEqual(html.count('data-source-route="'), 17)
        self.assertIn("0 inferred deadlines", html)
        self.assertIn("not the Presidents' Alliance's internal refresh schedule", html)

    def test_undocumented_pipeline_context_is_same_year_ecological_and_not_a_rate(self) -> None:
        reference = rows(ROOT / "data" / "undocumented_pipeline_reference.csv")
        comparison = rows(ROOT / "data" / "undocumented_pipeline_comparison.csv")
        self.assertEqual(len(reference), 11)
        self.assertEqual(len(comparison), 10)
        self.assertEqual(len({row["geography_id"] for row in reference}), 11)
        national = next(row for row in reference if row["geography_id"] == "US")
        self.assertEqual(int(national["high_school_graduates_annual_2023"]), 75000)
        self.assertEqual(int(national["higher_ed_enrollment_2023"]), 510000)

        self.assertEqual(
            sum(int(row["high_school_graduates_annual_2023"]) for row in comparison),
            53000,
        )
        self.assertEqual(
            sum(int(row["higher_ed_enrollment_2023"]) for row in comparison),
            358836,
        )
        top4 = [row for row in comparison if row["state"] in {"TX", "CA", "FL", "NY"}]
        self.assertEqual(sum(int(row["high_school_graduates_annual_2023"]) for row in top4), 35000)
        self.assertEqual(sum(int(row["higher_ed_enrollment_2023"]) for row in top4), 257125)
        self.assertEqual({row["state"] for row in comparison[:4]}, {"TX", "CA", "FL", "NY"})

        by_state = {row["state"]: row for row in comparison}
        self.assertEqual(by_state["TX"]["hs_rank"], "1")
        self.assertEqual(by_state["CA"]["higher_ed_rank_within_overlap"], "1")
        self.assertEqual(by_state["MD"]["stock_flow_scale_multiple"], "3.89")
        self.assertEqual(by_state["CA"]["stock_flow_scale_multiple"], "9.36")
        self.assertTrue(all("NOT a transition rate" in row["interpretation_gate"] for row in comparison))

        agenda = {row["research_id"]: row for row in rows(ROOT / "data" / "research_agenda.csv")}
        self.assertEqual(agenda["R06"]["status"], "Implemented as bounded 2023 state pipeline context")
        rendered = (ROOT / "docs" / "UNDOCUMENTED_PIPELINE_CONTEXT.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "undocumented-pipeline.html").read_text(encoding="utf-8")
        self.assertIn("70.7%", rendered)
        self.assertIn("70.4%", rendered)
        self.assertIn("not a transition rate", rendered.lower())
        self.assertIn("NOT A RATE", html)
        self.assertIn("stock", html.lower())
        self.assertIn("annual flow", html.lower())

    def test_population_crosswalk_is_structured_and_rendered(self) -> None:
        crosswalk = rows(ROOT / "data" / "population_crosswalk.csv")
        required = {
            "ipeds_us_nonresident",
            "immigrant_origin",
            "international_sevis",
            "undocumented_higher_ed",
            "undocumented_hs_graduates",
            "refugee_asylee",
        }
        self.assertEqual({row["population_id"] for row in crosswalk}, required)
        self.assertEqual(len(crosswalk), len(required))
        self.assertTrue(all(row["source_url"].startswith("https://") for row in crosswalk))
        ipeds = next(row for row in crosswalk if row["population_id"] == "ipeds_us_nonresident")
        self.assertIn("undocumented", ipeds["explicit_exclusions"].lower())
        self.assertIn("not", ipeds["comparison_warning"].lower())
        rendered = (ROOT / "docs" / "POPULATION_CROSSWALK.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "methodology-crosswalk.html").read_text(encoding="utf-8")
        for row in crosswalk:
            self.assertIn(row["population_label"], rendered)
            self.assertIn(row["source_url"], rendered)
            self.assertIn(row["population_label"], html)
            self.assertIn(row["source_url"], html)

    def test_population_trend_comparison_keeps_population_boundaries(self) -> None:
        reference = rows(ROOT / "data" / "population_trend_reference.csv")
        comparison = rows(ROOT / "data" / "population_trend_comparison.csv")
        self.assertEqual(len(reference), 6)
        self.assertEqual(len(comparison), 12)
        self.assertEqual(len({row["reference_id"] for row in reference}), 6)
        self.assertTrue(all(row["source_url"].startswith("https://") for row in reference))

        by_key = {
            (row["population_id"], int(row["observation_year"])): row
            for row in comparison
        }
        self.assertEqual(int(by_key[("ipeds_us_nonresident", 2019)]["estimate"]), 973058)
        self.assertEqual(int(by_key[("ipeds_us_nonresident", 2023)]["estimate"]), 1014598)
        self.assertEqual(int(by_key[("ipeds_us_nonresident", 2024)]["estimate"]), 1044137)
        self.assertEqual(by_key[("ipeds_us_nonresident", 2024)]["within_segment_change_pct"], "7.3")
        self.assertEqual(int(by_key[("immigrant_origin", 2000)]["estimate"]), 2900000)
        self.assertEqual(int(by_key[("immigrant_origin", 2023)]["estimate"]), 5991000)
        self.assertEqual(by_key[("immigrant_origin", 2023)]["reported_change_pct"], "107.0")
        self.assertEqual(int(by_key[("undocumented_higher_ed", 2019)]["estimate"]), 427000)
        self.assertEqual(int(by_key[("undocumented_higher_ed", 2021)]["estimate"]), 408000)
        self.assertEqual(by_key[("undocumented_higher_ed", 2021)]["reported_change_pct"], "-4.2")
        self.assertEqual(int(by_key[("undocumented_higher_ed", 2023)]["estimate"]), 510000)
        self.assertEqual(int(by_key[("undocumented_higher_ed", 2024)]["estimate"]), 525000)
        self.assertEqual(by_key[("undocumented_higher_ed", 2024)]["within_segment_change_pct"], "2.94")

        undocumented_segments = {
            row["trend_segment"]
            for row in comparison
            if row["population_id"] == "undocumented_higher_ed"
        }
        self.assertEqual(
            undocumented_segments,
            {"undocumented_2019_2021", "undocumented_2023_2024"},
        )
        library_ids = {row["resource_id"] for row in rows(ROOT / "data" / "research_library.csv")}
        self.assertTrue(all(row["research_library_id"] in library_ids for row in comparison))
        agenda = {row["research_id"]: row for row in rows(ROOT / "data" / "research_agenda.csv")}
        self.assertEqual(
            agenda["R04"]["status"],
            "Implemented as bounded national population trend comparison",
        )
        rendered = (ROOT / "docs" / "POPULATION_TREND_COMPARISON.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "population-trends.html").read_text(encoding="utf-8")
        self.assertIn("must not be added", rendered)
        self.assertIn("does **not** calculate a 2021-2023 undocumented trend", rendered)
        self.assertIn("NOT ADDABLE", html)
        self.assertIn("no 2021–2023 undocumented trend is calculated", html)

    def test_recurring_report_register_is_relational_and_rendered(self) -> None:
        register = rows(ROOT / "data" / "recurring_report_register.csv")
        library_ids = {row["resource_id"] for row in rows(ROOT / "data" / "research_library.csv")}
        population_ids = {row["population_id"] for row in rows(ROOT / "data" / "population_crosswalk.csv")}
        required = {
            "undocumented_higher_ed",
            "immigrant_origin_higher_ed",
            "undocumented_hs_graduates",
        }
        self.assertEqual({row["report_id"] for row in register}, required)
        self.assertEqual(len(register), 3)
        self.assertTrue(all(row["research_library_id"] in library_ids for row in register))
        self.assertTrue(all(row["population_id"] in population_ids for row in register))
        self.assertTrue(all("confirm" in row["schedule_status"].lower() for row in register))
        self.assertTrue(all("sign-off" in row["next_action"].lower() for row in register))
        rendered = (ROOT / "docs" / "RECURRING_REPORT_REGISTER.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "research-operations.html").read_text(encoding="utf-8")
        self.assertIn("does **not** claim access to", rendered)
        self.assertIn("does not represent the Presidents' Alliance's internal schedule", html)
        for row in register:
            self.assertIn(row["report_title"], rendered)
            self.assertIn(row["report_title"], html)

    def test_production_cycle_register_is_structured_and_rendered(self) -> None:
        cycle = rows(ROOT / "data" / "production_cycle_register.csv")
        expected_ids = [
            "kickoff_scope_lock",
            "versioned_intake",
            "method_change_review",
            "reproduction_qa",
            "discrepancy_resolution",
            "publication_gate",
            "archive_handoff",
        ]
        self.assertEqual([row["stage_id"] for row in cycle], expected_ids)
        self.assertEqual([int(row["stage_order"]) for row in cycle], list(range(1, 8)))
        self.assertIn("Confirmed production kickoff", cycle[0]["entry_condition"])
        for index, row in enumerate(cycle[:-1]):
            self.assertEqual(row["next_stage_id"], cycle[index + 1]["stage_id"])
            self.assertTrue(row["required_record"].strip())
            self.assertTrue(row["blocking_condition"].strip())
            self.assertTrue(row["exit_condition"].strip())
        self.assertEqual(cycle[-1]["next_stage_id"], "COMPLETE")

        broken = [dict(row) for row in cycle]
        broken[2]["next_stage_id"] = "publication_gate"
        with self.assertRaisesRegex(RuntimeError, "Broken production-cycle handoff"):
            validate_production_stages(broken)

        reports = rows(ROOT / "data" / "recurring_report_register.csv")
        rendered = (ROOT / "docs" / "PRODUCTION_CYCLE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "production-cycle.html").read_text(encoding="utf-8")
        self.assertIn("does **not** represent the Presidents' Alliance's internal", rendered)
        self.assertIn("does not represent the Presidents' Alliance's internal project-management system", html)
        self.assertIn("**Inferred internal deadlines:** 0", rendered)
        for row in cycle:
            self.assertIn(row["stage_label"], rendered)
            self.assertIn(html_module.escape(row["stage_label"]), html)
        for report in reports:
            self.assertIn(report["report_title"], rendered)
            self.assertIn(html_module.escape(report["report_title"]), html)

    def test_production_cycle_log_template_and_validator(self) -> None:
        template_path = ROOT / "data" / "production_cycle_log_template.csv"
        with template_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(tuple(reader.fieldnames or ()), PRODUCTION_LOG_FIELDS)
            self.assertEqual(list(reader), [])

        valid = {field: "" for field in PRODUCTION_LOG_FIELDS}
        valid.update(
            {
                "cycle_id": "validator-demo-cycle",
                "report_id": "undocumented_higher_ed",
                "stage_id": "kickoff_scope_lock",
                "record_id": "REC001",
                "record_type": "stage_evidence",
                "owner_role": "Analyst",
                "opened_date": "2026-10-13",
                "materiality": "not_applicable",
                "evidence_received": "Confirmed scope record",
                "status": "CLOSED",
                "closed_date": "2026-10-13",
                "notes": "In-memory validator fixture; not a partner record",
            }
        )
        self.assertEqual(validate_production_log_rows([valid]), [valid])

        invalid_report = dict(valid, report_id="unknown_report")
        with self.assertRaisesRegex(RuntimeError, "Unknown recurring report_id"):
            validate_production_log_rows([invalid_report])
        invalid_stage = dict(valid, stage_id="unknown_stage")
        with self.assertRaisesRegex(RuntimeError, "Unknown production stage_id"):
            validate_production_log_rows([invalid_stage])
        invalid_close = dict(valid, closed_date="")
        with self.assertRaisesRegex(RuntimeError, "Terminal status requires closed_date"):
            validate_production_log_rows([invalid_close])
        invalid_status = dict(valid, status="DONE")
        with self.assertRaisesRegex(RuntimeError, "Invalid status"):
            validate_production_log_rows([invalid_status])
        invalid_terminal_evidence = dict(valid, evidence_received="", decision="")
        with self.assertRaisesRegex(RuntimeError, "Terminal status requires evidence or decision"):
            validate_production_log_rows([invalid_terminal_evidence])
        invalid_discrepancy = dict(
            valid,
            record_type="discrepancy",
            materiality="high",
            decision="",
        )
        with self.assertRaisesRegex(RuntimeError, "Closed discrepancy requires a decision"):
            validate_production_log_rows([invalid_discrepancy])
        mixed_report = dict(valid, record_id="REC002", report_id="immigrant_origin_higher_ed")
        with self.assertRaisesRegex(RuntimeError, "mixes report IDs"):
            validate_production_log_rows([valid, mixed_report])
        extra_column = dict(valid)
        extra_column[None] = ["unexpected"]
        with self.assertRaisesRegex(RuntimeError, "extra CSV columns"):
            validate_production_log_rows([extra_column])
        short_row = dict(valid)
        short_row["notes"] = None
        with self.assertRaisesRegex(RuntimeError, "missing CSV columns"):
            validate_production_log_rows([short_row])

        rendered = (ROOT / "docs" / "PRODUCTION_CYCLE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "production-cycle.html").read_text(encoding="utf-8")
        self.assertIn("production_cycle_log_template.csv", rendered)
        self.assertIn("completed partner logs are not part of the public release allowlist", rendered)
        self.assertIn('href="downloads/production_cycle_log_template.csv"', html)

    def test_qa_resolution_log_tracks_current_high_priority_queue(self) -> None:
        log = rows(ROOT / "data" / "qa_resolution_log.csv")
        queue = {
            row["unitid"]: row
            for row in rows(ROOT / "data" / "processed" / "latest_release_institution_review.csv")
        }
        summary = json.loads(
            (ROOT / "data" / "qa_resolution_summary.json").read_text(encoding="utf-8")
        )
        high_priority = [row for row in queue.values() if row["review_priority"] == "high"]
        high_priority_order = [
            row["unitid"]
            for row in rows(ROOT / "data" / "processed" / "latest_release_institution_review.csv")
            if row["review_priority"] == "high"
        ]
        self.assertEqual(len(log), 27)
        self.assertEqual(len(log), len(high_priority))
        self.assertEqual([row["unitid"] for row in log], high_priority_order)
        self.assertEqual(len({row["unitid"] for row in log}), len(log))
        self.assertEqual(summary["reviewed_count"], len(log))
        self.assertEqual(summary["high_priority_total"], len(high_priority))
        self.assertEqual(summary["coverage_pct"], 100.0)
        self.assertTrue(summary["required_high_priority_covered"])
        self.assertEqual(set(summary["required_high_priority_unitids"]), {row["unitid"] for row in high_priority})
        self.assertEqual(summary["safe_with_context"], 11)
        self.assertEqual(summary["hold_for_confirmation"], 16)
        self.assertTrue(summary["required_top_10_covered"])
        expected_top_10 = [
            row["unitid"]
            for row in rows(ROOT / "data" / "processed" / "latest_release_institution_review.csv")
            if row["review_priority"] == "high"
        ][:10]
        self.assertEqual(summary["required_top_10_unitids"], expected_top_10)
        self.assertTrue(set(expected_top_10).issubset({row["unitid"] for row in log}))
        self.assertEqual(
            summary["safe_with_context"] + summary["hold_for_confirmation"], len(log)
        )
        self.assertEqual(set(queue_row["unitid"] for queue_row in high_priority), {row["unitid"] for row in log})
        self.assertEqual(len(summary["case_studies"]), 3)
        self.assertEqual(
            {case["case_type"] for case in summary["case_studies"]},
            {"unresolved_anomaly", "corroborated_movement", "structural_change"},
        )
        self.assertTrue(
            {case["unitid"] for case in summary["case_studies"]}.issubset(
                {row["unitid"] for row in log}
            )
        )
        for row in log:
            self.assertIn(row["unitid"], queue)
            self.assertEqual(queue[row["unitid"]]["review_priority"], "high")
            self.assertEqual(queue[row["unitid"]]["institution"], row["institution"])
            self.assertIn(row["publication_class"], {"safe_with_context", "hold_for_confirmation"})
            self.assertTrue(row["evidence_url"].startswith("https://"))
        by_unitid = {row["unitid"]: row for row in log}
        self.assertEqual(by_unitid["227216"]["publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["227216"]["disposition"], "corroborated_external_count")
        self.assertIn("institutionalresearch.unt.edu/fact-book", by_unitid["227216"]["evidence_url"])
        self.assertEqual(by_unitid["137564"]["disposition"], "external_scope_mismatch")
        self.assertIn("fact-book/2024-25", by_unitid["137564"]["evidence_url"])
        self.assertIn("Fall-Semester-2024-Enrollment-Statistics.pdf", by_unitid["101912"]["evidence_url"])
        self.assertEqual(by_unitid["159647"]["publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["159647"]["disposition"], "corroborated_direction")
        self.assertIn("six-year-enrollment-milestone", by_unitid["159647"]["evidence_url"])
        self.assertEqual(by_unitid["228787"]["disposition"], "partial_component_corroboration")
        self.assertIn("report44675", by_unitid["228787"]["evidence_url"])
        self.assertIn("cds-2023-2024-collin-college.pdf", by_unitid["247834"]["evidence_url"])
        self.assertEqual(by_unitid["195173"]["publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["195173"]["disposition"], "corroborated_external_count")
        self.assertIn("office-of-institutional-effectiveness-accreditation", by_unitid["195173"]["evidence_url"])
        self.assertEqual(by_unitid["175421"]["publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["175421"]["disposition"], "corroborated_external_count")
        self.assertIn("pdfs/archived/tartan-2024.pdf", by_unitid["175421"]["evidence_url"])
        self.assertEqual(by_unitid["156365"]["publication_class"], "safe_with_context")
        self.assertEqual(by_unitid["156365"]["disposition"], "corroborated_direction")
        self.assertIn("officeofinstitutionalresearch-institutionalreviewboard.html", by_unitid["156365"]["evidence_url"])
        self.assertEqual(by_unitid["135717"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["135717"]["disposition"], "external_scope_mismatch")
        self.assertIn("fb_credit_student_enrollment_profile.pdf", by_unitid["135717"]["evidence_url"])
        self.assertEqual(by_unitid["232937"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["232937"]["disposition"], "context_support_only")
        self.assertIn("Supporting-The-Success-Of-Global-Scholars", by_unitid["232937"]["evidence_url"])
        self.assertEqual(by_unitid["147800"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["147800"]["disposition"], "confirmed_reporting_discontinuity")
        self.assertIn("fall_2022-fall_2026_enrollment_comparison_report.pdf", by_unitid["147800"]["evidence_url"])
        self.assertEqual(by_unitid["110778"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["110778"]["disposition"], "partial_component_corroboration")
        self.assertIn("Official_Fall-Quick-Facts-2024.pdf", by_unitid["110778"]["evidence_url"])
        self.assertEqual(by_unitid["217633"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["217633"]["disposition"], "unresolved_discontinuity")
        self.assertIn("first-international-graduate-school-graduates", by_unitid["217633"]["evidence_url"])
        self.assertEqual(by_unitid["217475"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["217475"]["disposition"], "partial_component_corroboration")
        self.assertEqual(by_unitid["217475"]["evidence_url"], "https://www.ccri.edu/ie/")
        self.assertEqual(by_unitid["487649"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["487649"]["disposition"], "partial_component_corroboration")
        self.assertIn("bppe.ca.gov/webapplications/annualReports/2023", by_unitid["487649"]["evidence_url"])
        self.assertEqual(by_unitid["156541"]["publication_class"], "hold_for_confirmation")
        self.assertEqual(by_unitid["156541"]["disposition"], "partial_component_corroboration")
        self.assertIn("cumberlands-students-saved-63m", by_unitid["156541"]["evidence_url"])
        rendered = (ROOT / "docs" / "QA_RESOLUTION_LOG.md").read_text(encoding="utf-8")
        qa_html = (ROOT / "site" / "qa-review.html").read_text(encoding="utf-8")
        for row in log:
            self.assertIn(row["institution"], rendered)
            self.assertIn(row["evidence_url"], rendered)
            self.assertIn(html_module.escape(row["institution"]), qa_html)
            self.assertIn(html_module.escape(row["evidence_url"], quote=True), qa_html)
        self.assertIn("27/27", qa_html)
        self.assertIn("100%", qa_html)
        self.assertEqual(self.site_data["qa_resolution_summary"], summary)

    def test_research_memo_tracks_validated_outputs(self) -> None:
        memo = (ROOT / "docs" / "RESEARCH_MEMO.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "research-memo.html").read_text(encoding="utf-8")
        headline = self.findings["headline"]
        latest = self.update_review["national"]
        cases = self.site_data["qa_resolution_summary"]["case_studies"]
        self.assertIn(f"{headline['latest_nonresident']:,}", memo)
        self.assertIn(f"{latest['absolute_change']:+,}", memo)
        self.assertIn("fixed baseline, not a persistence finding", memo)
        self.assertIn(f'id="memo-total">{headline["latest_nonresident"]:,}', html)
        self.assertIn(f'id="memo-latest-change">{latest["absolute_change"]:+,}', html)
        for case in cases:
            self.assertIn(case["institution"], memo)
            self.assertIn(case["evidence_url"], memo)
            self.assertIn(case["institution"], html)
            self.assertIn(case["evidence_url"], html)

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

    def test_powerpoint_management_deck_is_valid_and_fresh(self) -> None:
        deck = ROOT / "deliverables" / "management_briefing_deck.pptx"
        public = ROOT / "site" / "downloads" / "management_briefing_deck.pptx"
        manifest = json.loads(
            (ROOT / "deliverables" / "management_briefing_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(deck.exists())
        payload = deck.read_bytes()
        self.assertGreater(len(payload), 40_000)
        self.assertTrue(payload.startswith(b"PK"))
        self.assertEqual(payload, public.read_bytes())
        self.assertEqual(manifest["slide_count"], 6)
        self.assertEqual(manifest["pptx_bytes"], len(payload))
        self.assertEqual(manifest["pptx_sha256"], hashlib.sha256(payload).hexdigest())
        builder = ROOT / manifest["builder"]
        self.assertEqual(
            manifest["builder_sha256"], hashlib.sha256(builder.read_bytes()).hexdigest()
        )
        for source_path, expected_hash in manifest["source_sha256"].items():
            self.assertEqual(
                expected_hash,
                hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest(),
                source_path,
            )

        drawing_ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        with zipfile.ZipFile(deck) as archive:
            self.assertIsNone(archive.testzip())
            slide_names = sorted(
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            )
            self.assertEqual(len(slide_names), 6)
            text = "\n".join(
                node.text or ""
                for slide_name in slide_names
                for node in ET.fromstring(archive.read(slide_name)).findall(
                    ".//a:t", drawing_ns
                )
            )
        for expected in (
            "1,044,137",
            "+29,539",
            "+31,592",
            "45 of 51 states/DC",
            "+28,580",
            "26 of 51 states/DC",
            "33 of 51",
            "+82,825",
            "+66,981",
            "-3,581",
            "+63,400",
            "Guardrails before reuse",
        ):
            self.assertIn(expected, text)
        self.assertEqual(manifest["metrics"]["latest_nonresident"], 1_044_137)
        self.assertEqual(manifest["metrics"]["states_recovered"], 33)
        self.assertEqual(manifest["metrics"]["undergraduate_positive_states"], 45)
        self.assertEqual(manifest["metrics"]["undergraduate_latest_change"], 31_592)
        self.assertIn("data/undergraduate_shift_baseline.csv", manifest["source_sha256"])

    def test_pdf_research_brief_is_valid_and_published(self) -> None:
        pdf = ROOT / "deliverables" / "research_brief.pdf"
        public = ROOT / "site" / "downloads" / "research_brief.pdf"
        manifest = json.loads(
            (ROOT / "deliverables" / "research_brief_manifest.json").read_text(encoding="utf-8")
        )
        memo = ROOT / manifest["source"]
        self.assertTrue(pdf.exists())
        payload = pdf.read_bytes()
        self.assertGreater(len(payload), 40_000)
        self.assertTrue(payload.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", payload[-2048:])
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", payload)), 3)
        self.assertEqual(payload, public.read_bytes())
        self.assertEqual(manifest["pdf_bytes"], len(payload))
        self.assertEqual(manifest["page_count"], 3)
        self.assertEqual(manifest["pdf_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(manifest["source_sha256"], hashlib.sha256(memo.read_bytes()).hexdigest())
        memo_text = (ROOT / "docs" / "RESEARCH_MEMO.md").read_text(encoding="utf-8")
        self.assertIn("45 of 51 states/DC", memo_text)
        self.assertIn("+28,580", memo_text)
        self.assertIn("26 of 51 states/DC", memo_text)

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
        release_rows = read_public_release_register()
        pairs = expand_public_release_pairs(release_rows)
        self.assertEqual(len(pairs), 120)
        for source, public, row in pairs:
            self.assertEqual(source.read_bytes(), public.read_bytes(), row["artifact_id"])
        self.assertEqual(validate_public_tree(release_rows), 120)

    def test_static_page_local_assets_and_ids(self) -> None:
        for page_name in (
            "index.html",
            "state.html",
            "research-memo.html",
            "methodology-crosswalk.html",
            "research-operations.html",
            "production-cycle.html",
            "sql-analysis.html",
            "ad-hoc-analysis.html",
            "state-recovery.html",
            "undergraduate-shift.html",
            "candidate-directory-preflight.html",
            "candidate-directory-changes.html",
            "candidate-year-watchlist.html",
            "medium-priority-review.html",
            "medium-qa-review.html",
            "private-nonprofit-growth.html",
            "qa-review.html",
            "population-trends.html",
            "undocumented-pipeline.html",
            "source-update-triage.html",
            "planning-scenarios.html",
            "freshness-monitor.html",
            "release-readiness.html",
            "research-library.html",
            "publication-handoff.html",
            "data-governance.html",
        ):
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

