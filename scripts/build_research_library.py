"""Validate structured source metadata and generate the current Research Library."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "research_library.csv"
OUTPUT = ROOT / "docs" / "RESEARCH_LIBRARY.md"

REQUIRED_FIELDS = (
    "resource_id",
    "title",
    "publisher",
    "resource_type",
    "scope",
    "update_pattern",
    "project_role",
    "url",
    "last_checked",
    "status_note",
)


def main() -> int:
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_FIELDS:
            raise RuntimeError(
                f"Research library schema mismatch: {reader.fieldnames} != {REQUIRED_FIELDS}"
            )
        rows = list(reader)

    if not rows:
        raise RuntimeError("Research library cannot be empty")
    ids = [row["resource_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Research library resource_id values must be unique")

    for row in rows:
        if any(not row[field].strip() for field in REQUIRED_FIELDS):
            raise RuntimeError(f"Blank research-library field in {row['resource_id']}")
        parsed = urlparse(row["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError(f"Research library URL must be HTTPS: {row['url']}")
        date.fromisoformat(row["last_checked"])

    last_checked = max(date.fromisoformat(row["last_checked"]) for row in rows)
    lines = [
        "# Research Library",
        "",
        "This compact library records the external sources used to collect, interpret, validate, and maintain the project. The CSV in `data/research_library.csv` is the structured source; this document is generated from it.",
        "",
        f"**Latest recorded source review:** {last_checked.isoformat()}",
        "",
        "| Resource | Type | Update pattern | Project role | Last checked |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| [{row['title']}]({row['url']}) | {row['resource_type']} | "
            f"{row['update_pattern']} | {row['project_role']} | {row['last_checked']} |"
        )

    lines.extend(
        [
            "",
            "## Resource notes",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['title']}",
                "",
                f"- **Publisher:** {row['publisher']}",
                f"- **Scope:** {row['scope']}",
                f"- **Project use:** {row['project_role']}",
                f"- **Status note:** {row['status_note']}",
                "",
            ]
        )

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Research library: {len(rows)} resources; latest review {last_checked.isoformat()}")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
