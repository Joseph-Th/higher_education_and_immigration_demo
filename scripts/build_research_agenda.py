"""Validate and render the structured research-needs register."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "research_agenda.csv"
OUTPUT = ROOT / "docs" / "RESEARCH_AGENDA.md"

FIELDS = (
    "research_id",
    "priority",
    "question",
    "evidence_trigger",
    "current_ipeds_fit",
    "additional_data_needed",
    "proposed_method",
    "proposed_output",
    "decision_rule",
    "status",
)
PRIORITIES = {"High": 0, "Medium": 1, "Low": 2}


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(f"Research agenda schema mismatch: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise RuntimeError("Research agenda cannot be empty")
    ids = [row["research_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Research agenda IDs must be unique")
    for row in rows:
        if any(not row[field].strip() for field in FIELDS):
            raise RuntimeError(f"Blank research agenda field in {row['research_id']}")
        if row["priority"] not in PRIORITIES:
            raise RuntimeError(f"Unknown priority in {row['research_id']}: {row['priority']}")

    rows.sort(key=lambda row: (PRIORITIES[row["priority"]], row["research_id"]))
    by_priority = {priority: [row for row in rows if row["priority"] == priority] for priority in PRIORITIES}
    lines = [
        "# Research Agenda and Data-Needs Register",
        "",
        "This register turns findings, QA observations, source limitations, and recurring product needs into explicit research questions. It separates questions answerable with the current IPEDS pipeline from questions that require population-specific or partner data.",
        "",
        "## Portfolio priorities",
        "",
        "| ID | Priority | Research question | Current IPEDS fit | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['research_id']} | {row['priority']} | {row['question']} | {row['current_ipeds_fit']} | {row['status']} |"
        )

    lines.extend(["", "## Detailed research cards", ""])
    for priority, group in by_priority.items():
        if not group:
            continue
        lines.extend([f"### {priority} priority", ""])
        for row in group:
            lines.extend(
                [
                    f"#### {row['research_id']} · {row['question']}",
                    "",
                    f"- **Evidence trigger:** {row['evidence_trigger']}",
                    f"- **Current IPEDS fit:** {row['current_ipeds_fit']}",
                    f"- **Additional data needed:** {row['additional_data_needed']}",
                    f"- **Proposed method:** {row['proposed_method']}",
                    f"- **Proposed output:** {row['proposed_output']}",
                    f"- **Decision rule:** {row['decision_rule']}",
                    f"- **Status:** {row['status']}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Governance principles",
            "",
            "1. A new question should name the population, geography, period, denominator, and decision it is intended to support before analysis begins.",
            "2. Source limitations are part of the research question. A convenient dataset is not a reason to collapse distinct populations into one measure.",
            "3. Questions triggered by apparent anomalies enter QA review before they become public findings.",
            "4. Research requiring partner data should begin with a definitions/methodology crosswalk and release-vintage review.",
            "5. The agenda should be re-reviewed after each annual release because a confirmed pattern, revised source, or resolved anomaly can change priority.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Research agenda: {len(rows)} questions")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
