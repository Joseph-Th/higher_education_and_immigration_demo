"""Generate a concise stakeholder briefing note from validated project outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "docs" / "BRIEFING_NOTE.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed_int(value: int) -> str:
    return f"{value:+,}" if value else "0"


def signed_pct(value: float) -> str:
    return f"{value:+.1f}%" if value else "0.0%"


def main() -> int:
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "latest_update_review.json").read_text(encoding="utf-8"))
    benchmark = read_csv(DATA / "benchmark_audit.csv")
    library = read_csv(DATA / "research_library.csv")

    coverage = findings["coverage"]
    headline = findings["headline"]
    levels = findings["level_decomposition"]
    recovery = findings["recovery"]
    dynamics = findings["institution_dynamics"]["decade"]
    latest = review["national"]
    accounting = review["institution_accounting"]
    queue = review["review_queue"]
    top_gain = review["state_change"]["largest_gains"][0]
    top_decline = review["state_change"]["largest_declines"][0]
    benchmark_passed = sum(row["status"] == "PASS" for row in benchmark)

    if benchmark_passed != len(benchmark):
        raise RuntimeError("Cannot publish briefing note while external benchmark checks fail")
    if latest["undergraduate_change"] + latest["graduate_change"] != latest["absolute_change"]:
        raise RuntimeError("Latest student-level decomposition does not reconcile")
    if (
        accounting["continuing_change"]
        + accounting["entered_enrollment"]
        - accounting["left_enrollment"]
        != latest["absolute_change"]
    ):
        raise RuntimeError("Latest institution accounting does not reconcile")

    start_year = coverage["start_year"]
    end_year = coverage["end_year"]
    prior_year = review["coverage"]["prior_year"]
    status = coverage["latest_data_status"]

    lines = [
        f"# Briefing Note: U.S. Nonresident Enrollment, Fall {end_year}",
        "",
        "**Audience:** research, policy, and communications leadership  ",
        f"**Coverage:** degree-granting institutions in the IPEDS First Look/Digest Title IV universe, 50 states + DC, Fall {start_year}-{end_year}  ",
        f"**Latest data status:** {status.capitalize()}",
        "",
        "## Executive summary",
        "",
        f"Fall {end_year} U.S. nonresident enrollment reached **{headline['latest_nonresident']:,} students**, or **{headline['latest_share_pct']:.2f}%** of total enrollment in the analytic universe. That is **{signed_int(latest['absolute_change'])} students ({signed_pct(latest['pct_change'])})** from {prior_year}.",
        "",
        f"The newest annual movement differs from the longer-run pattern. From {prior_year} to {end_year}, undergraduate U.S. nonresident enrollment changed by **{signed_int(latest['undergraduate_change'])}**, while graduate enrollment changed by **{signed_int(latest['graduate_change'])}**. Across the full {start_year}-{end_year} period, graduate enrollment changed by **{signed_int(levels['graduate_change_students'])}** and undergraduate enrollment by **{signed_int(levels['undergraduate_change_students'])}**, for a net national change of **{signed_int(headline['change_since_2015'])}**.",
        "",
        f"The latest increase is primarily movement at institutions already in the analytic universe. Continuing institutions account for **{signed_int(accounting['continuing_change'])}** of the {prior_year}-{end_year} change, while entry and exit from the analytic universe net to **{signed_int(accounting['entry_exit_net'])}**.",
        "",
        "## What merits attention",
        "",
        f"- **Short-run composition changed.** The {prior_year}-{end_year} increase is undergraduate-led even though the decade-level increase is graduate-led. One year is not enough to establish a new trend, so the next release should test whether this shift persists.",
        f"- **State movement is uneven.** {top_gain['state']} posted the largest latest-year increase (**{signed_int(top_gain['absolute_change'])}**), while {top_decline['state']} posted the largest decline (**{signed_int(top_decline['absolute_change'])}**). Across the post-pandemic comparison, **{recovery['states_at_or_above_baseline']}** states/DC are at or above their {recovery['baseline_year']} level and **{recovery['states_below_baseline']}** remain below it.",
        f"- **Institution-level QA still matters.** The latest-release review contains **{queue['high']} high-priority** and **{queue['medium']} medium-priority** records for analyst review. These flags identify changes that warrant investigation; they are not automatic findings that the source data are wrong.",
        f"- **The national increase is not an artifact of a larger institution universe.** Across {start_year}-{end_year}, {dynamics['continuing_institutions']:,} continuing institutions contribute **{signed_int(dynamics['continuing_change'])}**, while universe entry/exit nets to **{signed_int(dynamics['entry_exit_net'])}**.",
        "",
        "## Questions for the next update",
        "",
        f"1. Does the undergraduate-led movement observed in {end_year} persist in the next Fall Enrollment release, or revert toward the graduate-led pattern seen over {start_year}-{end_year}?",
        f"2. Are the largest state changes broad-based across institutions, or concentrated in a small number of campuses? The current QA queue should be resolved before institution-specific changes are elevated into public narrative.",
        "3. Do complementary population-specific sources show similar or different patterns? IPEDS U.S. nonresident status should not be used as a proxy for undocumented, immigrant-origin, DACA, or foreign-born populations.",
        "4. Have revised IPEDS files or a newer NCES Digest changed any benchmark values or release-status language?",
        "",
        "## Interpretation boundaries",
        "",
        "This analysis supports enrollment monitoring, not causal claims about immigration policy. IPEDS U.S. nonresident status does not identify immigration status or country of origin, and Fall Enrollment is a point-in-time snapshot. State totals describe institution location. Institution structures, UNITIDs, eligibility, and reporting practices can change over time.",
        "",
        "## Evidence and publication status",
        "",
        f"- **{benchmark_passed}/{len(benchmark)}** NCES Digest consistency checks pass.",
        f"- The latest release review contains **{queue['flagged_total']}** reason-coded institution records for triage.",
        f"- The Research Library contains **{len(library)}** maintained external resources spanning primary data, methodology, release monitoring, benchmarks, and related Higher Ed Immigration Portal research.",
        "- A structured population/source crosswalk governs whether IPEDS, SEVIS, CPS immigrant-origin, and ACS-derived undocumented-student measures are directly comparable, contextual only, or a separate data need.",
        "- Exact source archives, hashes, schema checks, QA outputs, and downloadable analysis tables are retained in the repository.",
        "",
        "For full methods and numerical detail, see `docs/METHODOLOGY.md`, `docs/POPULATION_CROSSWALK.md`, `docs/FINDINGS.md`, and `docs/LATEST_UPDATE_REVIEW.md`.",
        "",
    ]

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(
        f"Briefing note: {end_year} total={headline['latest_nonresident']:,}; "
        f"latest change={latest['absolute_change']:+,}; QA high={queue['high']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
