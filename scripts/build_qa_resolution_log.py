"""Validate and render analyst dispositions for selected annual QA flags.

The automated latest-release queue identifies records that deserve attention. This
file handles the next step: a manually curated, evidence-backed review sample. It
does not rewrite source data. Instead it records whether outside evidence
corroborates a direction, explains a structural change, or leaves the item
unresolved for institution-specific publication.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
SOURCE = DATA / "qa_resolution_log.csv"
DOC_OUTPUT = ROOT / "docs" / "QA_RESOLUTION_LOG.md"
JSON_OUTPUT = DATA / "qa_resolution_summary.json"

FIELDS = (
    "unitid",
    "institution",
    "reviewed_on",
    "disposition",
    "publication_class",
    "evidence_label",
    "evidence_url",
    "analyst_note",
)
PUBLICATION_CLASSES = {"safe_with_context", "hold_for_confirmation"}


def featured_case(
    rows: list[dict[str, object]],
    *,
    case_type: str,
    publication_class: str,
    disposition: str,
) -> dict[str, object]:
    matches = [
        row
        for row in rows
        if row["publication_class"] == publication_class
        and row["disposition"] == disposition
    ]
    if not matches:
        raise RuntimeError(
            f"Missing required featured QA case: {publication_class}/{disposition}"
        )
    row = max(matches, key=lambda item: abs(int(item["absolute_change"])))
    return {
        "case_type": case_type,
        "unitid": row["unitid"],
        "institution": row["institution"],
        "state": row["state"],
        "absolute_change": row["absolute_change"],
        "disposition": row["disposition"],
        "publication_class": row["publication_class"],
        "evidence_label": row["evidence_label"],
        "evidence_url": row["evidence_url"],
        "analyst_note": row["analyst_note"],
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(f"QA resolution schema mismatch: {reader.fieldnames}")
        reviewed = list(reader)
    if not reviewed:
        raise RuntimeError("QA resolution log cannot be empty")

    queue_rows = read_rows(PROCESSED / "latest_release_institution_review.csv")
    queue = {row["unitid"]: row for row in queue_rows}
    required_top_10 = [
        row["unitid"] for row in queue_rows if row["review_priority"] == "high"
    ][:10]
    seen: set[str] = set()
    joined: list[dict[str, object]] = []
    for row in reviewed:
        unitid = row["unitid"]
        if unitid in seen:
            raise RuntimeError(f"Duplicate QA resolution UNITID: {unitid}")
        seen.add(unitid)
        if unitid not in queue:
            raise RuntimeError(f"QA resolution UNITID not in latest review queue: {unitid}")
        current = queue[unitid]
        if current["review_priority"] != "high":
            raise RuntimeError(f"Reviewed sample must remain high priority: {unitid}")
        if current["institution"] != row["institution"]:
            raise RuntimeError(
                f"Institution name drift for {unitid}: {row['institution']} != {current['institution']}"
            )
        if row["publication_class"] not in PUBLICATION_CLASSES:
            raise RuntimeError(
                f"Unknown publication class for {unitid}: {row['publication_class']}"
            )
        try:
            date.fromisoformat(row["reviewed_on"])
        except ValueError as exc:
            raise RuntimeError(f"Invalid reviewed_on for {unitid}: {row['reviewed_on']}") from exc
        if not row["evidence_url"].startswith("https://"):
            raise RuntimeError(f"Evidence URL must use HTTPS for {unitid}")
        joined.append(
            {
                **row,
                "state": current["state"],
                "absolute_change": int(current["absolute_change"]),
                "review_reasons": current["review_reasons"],
            }
        )

    missing_required = [unitid for unitid in required_top_10 if unitid not in seen]
    if missing_required:
        raise RuntimeError(
            "QA resolution log must cover the ten highest-impact current high-priority "
            f"records; missing UNITIDs: {', '.join(missing_required)}"
        )

    classes = Counter(str(row["publication_class"]) for row in joined)
    dispositions = Counter(str(row["disposition"]) for row in joined)
    case_studies = [
        featured_case(
            joined,
            case_type="unresolved_anomaly",
            publication_class="hold_for_confirmation",
            disposition="unresolved_discontinuity",
        ),
        featured_case(
            joined,
            case_type="corroborated_movement",
            publication_class="safe_with_context",
            disposition="corroborated_direction",
        ),
        featured_case(
            joined,
            case_type="structural_change",
            publication_class="safe_with_context",
            disposition="expected_structural_change",
        ),
    ]
    summary = {
        "reviewed_count": len(joined),
        "safe_with_context": classes["safe_with_context"],
        "hold_for_confirmation": classes["hold_for_confirmation"],
        "dispositions": dict(sorted(dispositions.items())),
        "reviewed_unitids": [row["unitid"] for row in joined],
        "required_top_10_unitids": required_top_10,
        "required_top_10_covered": True,
        "case_studies": case_studies,
        "latest_reviewed_on": max(row["reviewed_on"] for row in joined),
    }
    JSON_OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# QA Resolution Log",
        "",
        "The automated annual review queue is deliberately conservative: it flags large or unusual changes for analyst attention. This log records a manually reviewed sample of the current high-priority queue and the publication decision that follows from the evidence review. The required sample covers the ten highest-impact high-priority records in the current deterministic queue; additional cases may be included when they demonstrate a distinct structural issue.",
        "",
        "A disposition never overwrites IPEDS. `safe_with_context` means outside evidence is strong enough to discuss the direction or structural event with appropriate caveats. `hold_for_confirmation` means the official IPEDS value remains in aggregate calculations but should not drive an institution-specific claim until a directly comparable source is obtained.",
        "",
        "## Review summary",
        "",
        f"- **{len(joined)}** high-priority records manually reviewed.",
        f"- **{classes['safe_with_context']}** are safe to discuss with explicit context.",
        f"- **{classes['hold_for_confirmation']}** remain held for institution-specific interpretation.",
        "- Three representative cases are promoted into the public research memo: an unresolved anomaly, a corroborated movement, and a confirmed structural change.",
        f"- Latest review date: **{summary['latest_reviewed_on']}**.",
        "",
        "## Dispositions",
        "",
        "| Institution | State | Change | Disposition | Publication decision | Evidence |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in joined:
        change = int(row["absolute_change"])
        lines.append(
            f"| {row['institution']} | {row['state']} | {change:+,} | {row['disposition']} | "
            f"{row['publication_class']} | [{row['evidence_label']}]({row['evidence_url']}) |"
        )

    lines.extend(["", "## Analyst notes", ""])
    for row in joined:
        lines.extend(
            [
                f"### {row['institution']} (UNITID {row['unitid']})",
                "",
                f"**Automated trigger:** {str(row['review_reasons']).replace(' | ', '; ')}.",
                "",
                row["analyst_note"],
                "",
                f"**Decision:** `{row['publication_class']}` · **Disposition:** `{row['disposition']}` · **Reviewed:** {row['reviewed_on']}.",
                "",
            ]
        )

    lines.extend(
        [
            "## Review rule",
            "",
            "External institutional counts are not assumed to equal IPEDS `EFNRALT`. Terms such as *international student*, *international student and scholar*, F-1 headcount, SEVIS active record, and students from other countries can use different populations, reference dates, or inclusion rules. Outside sources therefore corroborate context or direction only when their scope supports that use.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(
        "QA resolution log: "
        f"{len(joined)} reviewed; {classes['safe_with_context']} safe_with_context; "
        f"{classes['hold_for_confirmation']} hold_for_confirmation"
    )
    print(f"Wrote {JSON_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
