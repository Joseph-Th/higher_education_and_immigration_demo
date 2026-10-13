"""Validate a live recurring-research production-cycle coordination log.

The tracked CSV is intentionally an empty public template. A completed partner log
may contain operational or partner-confidential information and therefore belongs
outside the public repository unless a separate release review explicitly approves
it.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "data" / "production_cycle_log_template.csv"
REPORT_REGISTER = ROOT / "data" / "recurring_report_register.csv"
STAGE_REGISTER = ROOT / "data" / "production_cycle_register.csv"

FIELDS = (
    "cycle_id",
    "report_id",
    "stage_id",
    "record_id",
    "record_type",
    "owner_role",
    "opened_date",
    "materiality",
    "issue_or_question",
    "evidence_requested",
    "evidence_received",
    "decision",
    "disclosure_requirement",
    "status",
    "closed_date",
    "notes",
)

RECORD_TYPES = {
    "stage_evidence",
    "question",
    "discrepancy",
    "decision",
    "approval",
    "archive",
}
MATERIALITIES = {"not_applicable", "low", "medium", "high"}
STATUSES = {"OPEN", "BLOCKED", "RESOLVED", "APPROVED", "HELD", "CLOSED"}
TERMINAL_STATUSES = {"RESOLVED", "APPROVED", "HELD", "CLOSED"}
ACTIVE_STATUSES = {"OPEN", "BLOCKED"}
CORE_REQUIRED = (
    "cycle_id",
    "report_id",
    "stage_id",
    "record_id",
    "record_type",
    "owner_role",
    "opened_date",
    "materiality",
    "status",
)


def _authority_ids(path: Path, key: str) -> set[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row[key] for row in csv.DictReader(handle)}


def _parse_iso_date(value: str, label: str, record_id: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Invalid ISO date for {label} in production-cycle record {record_id}: {value}"
        ) from exc


def validate_log_rows(rows: list[dict[str, str]], *, allow_empty: bool = True) -> list[dict[str, str]]:
    if not rows and not allow_empty:
        raise RuntimeError("Production-cycle log must contain at least one record")

    report_ids = _authority_ids(REPORT_REGISTER, "report_id")
    stage_ids = _authority_ids(STAGE_REGISTER, "stage_id")
    seen: set[tuple[str, str]] = set()
    cycle_reports: dict[str, str] = {}

    for row in rows:
        if None in row:
            raise RuntimeError("Production-cycle log row contains extra CSV columns")
        null_fields = [field for field in FIELDS if row.get(field) is None]
        if null_fields:
            raise RuntimeError(
                "Production-cycle log row is missing CSV columns: " + ", ".join(null_fields)
            )

        record_id = row.get("record_id") or "<missing>"
        missing = [field for field in CORE_REQUIRED if not (row.get(field) or "").strip()]
        if missing:
            raise RuntimeError(
                f"Missing required production-cycle fields in {record_id}: {', '.join(missing)}"
            )
        cycle_id = row["cycle_id"]
        prior_report = cycle_reports.setdefault(cycle_id, row["report_id"])
        if prior_report != row["report_id"]:
            raise RuntimeError(
                f"Production cycle {cycle_id} mixes report IDs: {prior_report} and {row['report_id']}"
            )
        key = (row["cycle_id"], row["record_id"])
        if key in seen:
            raise RuntimeError(
                f"Duplicate production-cycle record_id within cycle {row['cycle_id']}: {row['record_id']}"
            )
        seen.add(key)

        if row["report_id"] not in report_ids:
            raise RuntimeError(f"Unknown recurring report_id in {record_id}: {row['report_id']}")
        if row["stage_id"] not in stage_ids:
            raise RuntimeError(f"Unknown production stage_id in {record_id}: {row['stage_id']}")
        if row["record_type"] not in RECORD_TYPES:
            raise RuntimeError(f"Invalid record_type in {record_id}: {row['record_type']}")
        if row["materiality"] not in MATERIALITIES:
            raise RuntimeError(f"Invalid materiality in {record_id}: {row['materiality']}")
        if row["status"] not in STATUSES:
            raise RuntimeError(f"Invalid status in {record_id}: {row['status']}")
        if row["record_type"] == "discrepancy" and row["materiality"] == "not_applicable":
            raise RuntimeError(f"Discrepancy record requires materiality in {record_id}")

        opened = _parse_iso_date(row["opened_date"], "opened_date", record_id)
        closed_value = row.get("closed_date", "").strip()
        if row["status"] in TERMINAL_STATUSES and not closed_value:
            raise RuntimeError(f"Terminal status requires closed_date in {record_id}")
        if row["status"] in ACTIVE_STATUSES and closed_value:
            raise RuntimeError(f"Active status cannot have closed_date in {record_id}")
        if closed_value:
            closed = _parse_iso_date(closed_value, "closed_date", record_id)
            if closed < opened:
                raise RuntimeError(f"closed_date precedes opened_date in {record_id}")

        if row["status"] in TERMINAL_STATUSES and not (
            row.get("evidence_received", "").strip() or row.get("decision", "").strip()
        ):
            raise RuntimeError(f"Terminal status requires evidence or decision in {record_id}")
        if (
            row["record_type"] == "discrepancy"
            and row["status"] in TERMINAL_STATUSES
            and not row.get("decision", "").strip()
        ):
            raise RuntimeError(f"Closed discrepancy requires a decision in {record_id}")
        if row["status"] in {"APPROVED", "HELD"} and not row.get("decision", "").strip():
            raise RuntimeError(f"Approval/hold status requires a decision in {record_id}")

    return rows


def read_log(path: Path, *, allow_empty: bool = True) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(
                f"Production-cycle log schema mismatch: {reader.fieldnames} != {FIELDS}"
            )
        rows = list(reader)
    return validate_log_rows(rows, allow_empty=allow_empty)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="CSV log to validate; defaults to the tracked blank template",
    )
    parser.add_argument(
        "--require-records",
        action="store_true",
        help="Fail if the supplied log has no records",
    )
    args = parser.parse_args()
    path = args.path if args.path.is_absolute() else Path.cwd() / args.path
    rows = read_log(path, allow_empty=not args.require_records)
    print(
        f"Production-cycle log validation PASS: {len(rows)} record{'s' if len(rows) != 1 else ''}; "
        f"{len(FIELDS)} fields"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
