"""Build a reproducible review packet for the newest IPEDS release.

The purpose of this script is triage, not automated error detection. It compares
the latest year with the immediately preceding year, decomposes the national
change, and assigns review priority using explicit thresholds. A flagged record
means "review this change" rather than "the source value is wrong."
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from project_config import END_YEAR, LATEST_DATA_STATUS, START_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
JSON_OUTPUT = DATA / "latest_update_review.json"
CSV_OUTPUT = PROCESSED / "latest_release_institution_review.csv"
DOC_OUTPUT = ROOT / "docs" / "LATEST_UPDATE_REVIEW.md"

PRIORITY_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"Cannot write empty review output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_int(value: int) -> str:
    return f"{value:+,}" if value else "0"


def pct_change(new: int, old: int) -> float | None:
    if old == 0:
        return None
    return (new - old) / old * 100.0


def raise_priority(current: str, candidate: str) -> str:
    return candidate if PRIORITY_RANK[candidate] > PRIORITY_RANK[current] else current


def main() -> int:
    prior_year = END_YEAR - 1
    institution_rows = read_rows(PROCESSED / "institution_year.csv")
    national_rows = read_rows(PROCESSED / "national_year.csv")
    state_rows = read_rows(PROCESSED / "state_year.csv")

    national = {int(row["year"]): row for row in national_rows}
    if prior_year not in national or END_YEAR not in national:
        raise RuntimeError(f"Missing national rows for {prior_year}/{END_YEAR}")

    history: dict[str, dict[int, dict[str, str]]] = {}
    for row in institution_rows:
        history.setdefault(row["unitid"], {})[int(row["year"])] = row

    prior_ids = {unitid for unitid, years in history.items() if prior_year in years}
    latest_ids = {unitid for unitid, years in history.items() if END_YEAR in years}
    all_ids = sorted(prior_ids | latest_ids)

    review_rows: list[dict] = []
    flag_transitions: Counter[str] = Counter()

    for unitid in all_ids:
        years = history[unitid]
        prior = years.get(prior_year)
        latest = years.get(END_YEAR)
        if prior is not None and latest is not None:
            status = "Continuing"
        elif latest is not None:
            status = "Entered analytic universe"
        else:
            status = "Left analytic universe"

        prior_nr = 0 if prior is None else int(prior["nonresident_enrollment"])
        latest_nr = 0 if latest is None else int(latest["nonresident_enrollment"])
        change = latest_nr - prior_nr
        change_pct = pct_change(latest_nr, prior_nr)
        label_row = latest if latest is not None else prior
        assert label_row is not None

        prior_flag = "" if prior is None else prior["nonresident_imputation_flag"]
        latest_flag = "" if latest is None else latest["nonresident_imputation_flag"]
        flag_changed = prior is not None and latest is not None and prior_flag != latest_flag
        if prior is not None and latest is not None:
            flag_transitions[f"{prior_flag or '(blank)'} -> {latest_flag or '(blank)'}"] += 1

        historical_years = range(max(START_YEAR, prior_year - 3), prior_year)
        historical_values = [
            int(years[year]["nonresident_enrollment"])
            for year in historical_years
            if year in years
        ]
        recent_historical_max = max(historical_values, default=0)
        historical_discontinuity = (
            status == "Continuing"
            and (
                (prior_nr == 0 and latest_nr >= 500 and recent_historical_max >= 500)
                or (latest_nr == 0 and prior_nr >= 500 and recent_historical_max >= 500)
            )
        )

        priority = "none"
        reasons: list[str] = []

        if status != "Continuing":
            priority = raise_priority(priority, "low")
            reasons.append("analytic-universe membership changed")
            if max(prior_nr, latest_nr) >= 100:
                priority = raise_priority(priority, "medium")
                reasons.append("universe entry/exit involves at least 100 students")

        abs_change = abs(change)
        if abs_change >= 1000:
            priority = raise_priority(priority, "high")
            reasons.append("absolute change is at least 1,000 students")
        elif abs_change >= 500:
            priority = raise_priority(priority, "medium")
            reasons.append("absolute change is at least 500 students")
        elif abs_change >= 250:
            priority = raise_priority(priority, "low")
            reasons.append("absolute change is at least 250 students")

        if prior_nr >= 100 and change_pct is not None:
            abs_pct = abs(change_pct)
            if abs_pct >= 100:
                priority = raise_priority(priority, "high")
                reasons.append("percentage change is at least 100% from a baseline of 100+")
            elif abs_pct >= 50:
                priority = raise_priority(priority, "medium")
                reasons.append("percentage change is at least 50% from a baseline of 100+")
            elif abs_pct >= 25:
                priority = raise_priority(priority, "low")
                reasons.append("percentage change is at least 25% from a baseline of 100+")

        if historical_discontinuity:
            priority = raise_priority(priority, "high")
            reasons.append("zero/nonzero discontinuity conflicts with recent history")

        material_flag_change = flag_changed and ({prior_flag, latest_flag} - {"R", "Z"})
        if material_flag_change:
            priority = raise_priority(priority, "medium")
            reasons.append("imputation/status flag changed to or from a non-R/Z code")

        review_rows.append(
            {
                "unitid": unitid,
                "institution": label_row["institution"],
                "state": label_row["state"],
                "control": label_row["control"],
                "status": status,
                f"nonresident_{prior_year}": "" if prior is None else prior_nr,
                f"nonresident_{END_YEAR}": "" if latest is None else latest_nr,
                "absolute_change": change,
                "pct_change": "" if change_pct is None else round(change_pct, 2),
                f"flag_{prior_year}": prior_flag,
                f"flag_{END_YEAR}": latest_flag,
                "flag_changed": "yes" if flag_changed else "no",
                "recent_historical_max": recent_historical_max,
                "review_priority": priority,
                "review_reasons": " | ".join(reasons),
            }
        )

    review_rows.sort(
        key=lambda row: (
            -PRIORITY_RANK[row["review_priority"]],
            -abs(int(row["absolute_change"])),
            row["institution"],
        )
    )
    write_rows(CSV_OUTPUT, review_rows)

    prior_national = national[prior_year]
    latest_national = national[END_YEAR]
    national_change = int(latest_national["nonresident_enrollment"]) - int(
        prior_national["nonresident_enrollment"]
    )
    national_pct = pct_change(
        int(latest_national["nonresident_enrollment"]),
        int(prior_national["nonresident_enrollment"]),
    )
    undergraduate_change = int(latest_national["undergraduate_nonresident"]) - int(
        prior_national["undergraduate_nonresident"]
    )
    graduate_change = int(latest_national["graduate_nonresident"]) - int(
        prior_national["graduate_nonresident"]
    )
    if undergraduate_change + graduate_change != national_change:
        raise RuntimeError("Latest-year student-level changes do not reconcile to national change")

    continuing = [row for row in review_rows if row["status"] == "Continuing"]
    entered = [row for row in review_rows if row["status"] == "Entered analytic universe"]
    left = [row for row in review_rows if row["status"] == "Left analytic universe"]
    continuing_change = sum(int(row["absolute_change"]) for row in continuing)
    entered_enrollment = sum(int(row[f"nonresident_{END_YEAR}"] or 0) for row in entered)
    left_enrollment = sum(int(row[f"nonresident_{prior_year}"] or 0) for row in left)
    if continuing_change + entered_enrollment - left_enrollment != national_change:
        raise RuntimeError("Latest-year institution accounting does not reconcile to national change")

    states_by_year = {
        (int(row["year"]), row["state"]): row for row in state_rows
    }
    state_changes = []
    for state in sorted({row["state"] for row in state_rows}):
        prior_state = states_by_year[(prior_year, state)]
        latest_state = states_by_year[(END_YEAR, state)]
        old = int(prior_state["nonresident_enrollment"])
        new = int(latest_state["nonresident_enrollment"])
        state_changes.append(
            {
                "state": state,
                "prior": old,
                "latest": new,
                "absolute_change": new - old,
                "pct_change": round(pct_change(new, old) or 0.0, 1),
            }
        )
    if sum(row["absolute_change"] for row in state_changes) != national_change:
        raise RuntimeError("Latest-year state changes do not reconcile to national change")

    priority_counts = Counter(row["review_priority"] for row in review_rows)
    flagged = [row for row in review_rows if row["review_priority"] != "none"]
    historical_discontinuities = [
        row
        for row in review_rows
        if "zero/nonzero discontinuity" in row["review_reasons"]
    ]

    summary = {
        "coverage": {
            "prior_year": prior_year,
            "latest_year": END_YEAR,
            "latest_data_status": LATEST_DATA_STATUS,
        },
        "national": {
            "prior_nonresident": int(prior_national["nonresident_enrollment"]),
            "latest_nonresident": int(latest_national["nonresident_enrollment"]),
            "absolute_change": national_change,
            "pct_change": round(national_pct or 0.0, 1),
            "undergraduate_change": undergraduate_change,
            "graduate_change": graduate_change,
        },
        "institution_accounting": {
            "prior_institutions": len(prior_ids),
            "latest_institutions": len(latest_ids),
            "continuing_institutions": len(continuing),
            "entered_institutions": len(entered),
            "left_institutions": len(left),
            "continuing_change": continuing_change,
            "entered_enrollment": entered_enrollment,
            "left_enrollment": left_enrollment,
            "entry_exit_net": entered_enrollment - left_enrollment,
        },
        "state_change": {
            "largest_gains": sorted(
                state_changes, key=lambda row: row["absolute_change"], reverse=True
            )[:8],
            "largest_declines": sorted(
                state_changes, key=lambda row: row["absolute_change"]
            )[:8],
        },
        "review_queue": {
            "high": priority_counts["high"],
            "medium": priority_counts["medium"],
            "low": priority_counts["low"],
            "flagged_total": len(flagged),
            "historical_discontinuities": len(historical_discontinuities),
            "top_items": flagged[:15],
        },
        "flag_transitions": dict(sorted(flag_transitions.items())),
    }
    JSON_OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    top_gains = summary["state_change"]["largest_gains"][:5]
    top_declines = summary["state_change"]["largest_declines"][:5]
    top_review = summary["review_queue"]["top_items"][:10]
    lines = [
        "# Latest Release Review",
        "",
        f"This review compares Fall {prior_year} with Fall {END_YEAR} ({LATEST_DATA_STATUS}). It is generated by `scripts/build_update_review.py` from the normalized IPEDS institution-year data.",
        "",
        "A review flag is a **triage signal, not a finding that the source is wrong**. Large changes can reflect real enrollment movement, reporting changes, mergers/reorganizations, classification changes, or data-quality issues that require source review.",
        "",
        "## National update",
        "",
        f"U.S. nonresident enrollment increased from **{int(prior_national['nonresident_enrollment']):,}** to **{int(latest_national['nonresident_enrollment']):,}**, a change of **{fmt_int(national_change)} ({national_pct:+.1f}%)**.",
        "",
        f"The composition of the newest increase differs from the decade-level pattern: undergraduate U.S. nonresident enrollment changed by **{fmt_int(undergraduate_change)}**, while graduate enrollment changed by **{fmt_int(graduate_change)}**. The two components reconcile exactly to the national change.",
        "",
        "## Institution accounting",
        "",
        f"- **{len(continuing):,}** institutions appear in both endpoint years and contribute **{fmt_int(continuing_change)}** students.",
        f"- **{len(entered):,}** institutions entered the analytic universe with **{entered_enrollment:,}** U.S. nonresident students in {END_YEAR}.",
        f"- **{len(left):,}** institutions left the analytic universe after reporting **{left_enrollment:,}** U.S. nonresident students in {prior_year}.",
        f"- Universe entry/exit therefore nets to **{fmt_int(entered_enrollment - left_enrollment)}**.",
        "",
        "## Largest state changes",
        "",
        f"| State | {prior_year} | {END_YEAR} | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in top_gains:
        lines.append(
            f"| {row['state']} | {row['prior']:,} | {row['latest']:,} | {fmt_int(row['absolute_change'])} |"
        )
    for row in top_declines:
        lines.append(
            f"| {row['state']} | {row['prior']:,} | {row['latest']:,} | {fmt_int(row['absolute_change'])} |"
        )

    lines.extend(
        [
            "",
            "## QA triage queue",
            "",
            f"The explicit review rules currently produce **{priority_counts['high']} high-priority**, **{priority_counts['medium']} medium-priority**, and **{priority_counts['low']} low-priority** institution records.",
            "",
            "High priority is assigned for an absolute change of at least 1,000 students, a change of at least 100% from a baseline of 100 or more, or a zero/nonzero discontinuity that conflicts with recent history. Medium and low priorities use progressively smaller thresholds. Nonstandard imputation/status transitions and analytic-universe entry/exit are also surfaced.",
            "",
            "| Priority | Institution | State | Change | Review reason |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in top_review:
        markdown_reason = str(row["review_reasons"]).replace(" | ", "; ")
        lines.append(
            f"| {row['review_priority']} | {row['institution']} | {row['state']} | {fmt_int(int(row['absolute_change']))} | {markdown_reason} |"
        )

    lines.extend(
        [
            "",
            "## Example requiring analyst judgment",
            "",
        ]
    )
    if historical_discontinuities:
        example = historical_discontinuities[0]
        unitid = example["unitid"]
        recent = sorted(
            (
                year,
                int(history[unitid][year]["nonresident_enrollment"]),
                history[unitid][year]["nonresident_imputation_flag"],
            )
            for year in history[unitid]
            if prior_year - 2 <= year <= END_YEAR
        )
        trend = ", ".join(f"{year}: {value:,} ({flag})" for year, value, flag in recent)
        lines.append(
            f"**{example['institution']} (UNITID {unitid})** is automatically flagged because its endpoint pattern conflicts with recent history. The selected IPEDS values are {trend}. The {prior_year} value is marked as reported (`R`), not imputed. This packet does not discard or rewrite the value; it identifies the discontinuity for source/methodology review before publication."
        )
    else:
        lines.append("No zero/nonzero historical discontinuities met the current threshold.")

    lines.extend(
        [
            "",
            "## Files for review",
            "",
            f"- `data/processed/latest_release_institution_review.csv`: institution-level {prior_year}-{END_YEAR} comparison with priority and reason fields.",
            "- `data/latest_update_review.json`: machine-readable summary used by the public brief.",
            "- `data/qa_report.json`: structural and arithmetic pipeline checks.",
            "- `data/benchmark_audit.csv`: external NCES Digest consistency audit.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Latest release review: {prior_year}-{END_YEAR} change {national_change:+,}; "
        f"queue high={priority_counts['high']} medium={priority_counts['medium']} "
        f"low={priority_counts['low']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {JSON_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
