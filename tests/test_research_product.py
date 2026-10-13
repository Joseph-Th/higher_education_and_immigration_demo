from __future__ import annotations

import csv
import hashlib
import html as html_module
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
        self.assertEqual(len(handoff), 11)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"N01", "N05", "S01", "Q01", "M01", "B01"}.issubset(set(ids)))
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
        q01 = next(row for row in handoff if row["claim_id"] == "Q01")
        resolution = json.loads((ROOT / "data" / "qa_resolution_summary.json").read_text(encoding="utf-8"))
        self.assertIn(str(resolution["reviewed_count"]), q01["public_copy"])
        self.assertEqual(q01["publication_status"], "READY WITH CLAIM-LEVEL HOLDS")
        rendered = (ROOT / "docs" / "PUBLICATION_HANDOFF.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "publication-handoff.html").read_text(encoding="utf-8")
        for row in handoff:
            self.assertIn(row["claim_id"], rendered)
            self.assertIn(row["public_copy"], rendered)
            self.assertIn(html_module.escape(row["public_copy"]), html)
        self.assertIn("does **not** represent the Presidents' Alliance's internal publication workflow", rendered)

    def test_public_release_register_enforces_allowlisted_publication(self) -> None:
        release_rows = read_public_release_register()
        self.assertEqual(len(release_rows), 35)
        ids = [row["artifact_id"] for row in release_rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["release_decision"] == "PUBLIC" for row in release_rows))
        self.assertTrue(all(row["person_level_data"] == "No" for row in release_rows))
        self.assertTrue(all(row["immigration_status_data"] == "No" for row in release_rows))
        self.assertTrue(all(not row["source_path"].startswith("data/raw/") for row in release_rows))
        self.assertTrue(all(row["public_path"].startswith("site/downloads/") for row in release_rows))
        pairs = expand_public_release_pairs(release_rows)
        self.assertEqual(len(pairs), 85)
        self.assertEqual(validate_public_tree(release_rows), 85)

        rendered = (ROOT / "docs" / "DATA_GOVERNANCE.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "data-governance.html").read_text(encoding="utf-8")
        self.assertIn("Expanded public download files:** 85", rendered)
        self.assertIn("restricted by default", rendered)
        self.assertIn("Public by design does not mean publish everything.", html)
        self.assertIn("85</strong><span>expanded public download files", html)

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
        self.assertEqual(validate_public_tree(release_rows), 85)

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
        self.assertIn("crosswalk complete", r04["status"].lower())
        rendered = (ROOT / "docs" / "RESEARCH_AGENDA.md").read_text(encoding="utf-8")
        for row in agenda:
            self.assertIn(row["research_id"], rendered)
            self.assertIn(row["question"], rendered)

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
        self.assertEqual(len(log), 11)
        self.assertEqual(len({row["unitid"] for row in log}), len(log))
        self.assertEqual(summary["reviewed_count"], len(log))
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
        self.assertGreaterEqual(summary["safe_with_context"], 2)
        self.assertGreaterEqual(summary["hold_for_confirmation"], 1)
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
        rendered = (ROOT / "docs" / "QA_RESOLUTION_LOG.md").read_text(encoding="utf-8")
        for row in log:
            self.assertIn(row["institution"], rendered)
            self.assertIn(row["evidence_url"], rendered)
        self.assertEqual(self.site_data["qa_resolution_summary"], summary)

    def test_research_memo_tracks_validated_outputs(self) -> None:
        memo = (ROOT / "docs" / "RESEARCH_MEMO.md").read_text(encoding="utf-8")
        html = (ROOT / "site" / "research-memo.html").read_text(encoding="utf-8")
        headline = self.findings["headline"]
        latest = self.update_review["national"]
        cases = self.site_data["qa_resolution_summary"]["case_studies"]
        self.assertIn(f"{headline['latest_nonresident']:,}", memo)
        self.assertIn(f"{latest['absolute_change']:+,}", memo)
        self.assertIn("not yet evidence of a durable trend change", memo)
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
        self.assertEqual(len(pairs), 85)
        for source, public, row in pairs:
            self.assertEqual(source.read_bytes(), public.read_bytes(), row["artifact_id"])
        self.assertEqual(validate_public_tree(release_rows), 85)

    def test_static_page_local_assets_and_ids(self) -> None:
        for page_name in (
            "index.html",
            "state.html",
            "research-memo.html",
            "methodology-crosswalk.html",
            "research-operations.html",
            "production-cycle.html",
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

