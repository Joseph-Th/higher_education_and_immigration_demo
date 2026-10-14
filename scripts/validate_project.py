"""Rebuild and validate the complete offline research product in one command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(label: str, command: list[str]) -> None:
    print(f"\n== {label} ==")
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(f"{label} failed with exit code {result.returncode}")


def main() -> int:
    steps = [
        ("Compile Python", [PYTHON, "-m", "compileall", "-q", "scripts", "tests"]),
        ("Cross-year schema audit", [PYTHON, "scripts/audit_ipeds_schema.py"]),
        ("Build normalized analysis", [PYTHON, "scripts/build_analysis.py"]),
        ("Build SQL analysis", [PYTHON, "scripts/build_sql_analysis.py"]),
        ("Build ad hoc analysis casebook", [PYTHON, "scripts/build_ad_hoc_analysis.py"]),
        ("Build state recovery analysis", [PYTHON, "scripts/build_state_recovery_analysis.py"]),
        ("Build undergraduate shift baseline", [PYTHON, "scripts/build_undergraduate_shift_baseline.py"]),
        ("Build planning scenarios", [PYTHON, "scripts/build_planning_scenarios.py"]),
        ("Build freshness monitor", [PYTHON, "scripts/build_freshness_monitor.py"]),
        ("Build latest-release review", [PYTHON, "scripts/build_update_review.py"]),
        ("Build QA resolution log", [PYTHON, "scripts/build_qa_resolution_log.py"]),
        ("Build private nonprofit growth analysis", [PYTHON, "scripts/build_private_nonprofit_analysis.py"]),
        ("Build research library", [PYTHON, "scripts/build_research_library.py"]),
        ("Build source update triage", [PYTHON, "scripts/build_source_update_triage.py"]),
        ("Build undocumented pipeline context", [PYTHON, "scripts/build_undocumented_pipeline.py"]),
        ("Build population crosswalk", [PYTHON, "scripts/build_population_crosswalk.py"]),
        ("Build population trend comparison", [PYTHON, "scripts/build_population_trends.py"]),
        ("Build recurring report register", [PYTHON, "scripts/build_recurring_report_register.py"]),
        ("Validate production cycle log template", [PYTHON, "scripts/validate_production_cycle_log.py"]),
        ("Build production cycle", [PYTHON, "scripts/build_production_cycle.py"]),
        ("Build research agenda", [PYTHON, "scripts/build_research_agenda.py"]),
        ("Summarize findings", [PYTHON, "scripts/summarize_findings.py"]),
        ("External publication benchmark", [PYTHON, "scripts/validate_benchmarks.py"]),
        ("Build state profiles", [PYTHON, "scripts/build_state_profiles.py"]),
        ("Build stakeholder briefing note", [PYTHON, "scripts/build_briefing_note.py"]),
        ("Build research memo", [PYTHON, "scripts/build_research_memo.py"]),
        ("Build publication handoff", [PYTHON, "scripts/build_publication_handoff.py"]),
        ("Build release readiness", [PYTHON, "scripts/build_release_readiness.py"]),
        ("Build data governance", [PYTHON, "scripts/build_data_governance.py"]),
        ("Build public site data", [PYTHON, "scripts/build_site_data.py"]),
        (
            "Research-product tests",
            [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-v"],
        ),
    ]
    for label, command in steps:
        run(label, command)
    print("\nVALIDATION PASS: reproducible research product is internally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

