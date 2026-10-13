"""Run a read-only SQL portfolio query pack over validated analysis outputs.

The SQLite database exists only in memory and is rebuilt from canonical processed
CSVs on every run. The SQL layer is therefore a query/QA demonstration, not a
second analytical authority.
"""

from __future__ import annotations

import csv
import html
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
QUERY_PACK = ROOT / "sql" / "portfolio_queries.sql"
AUDIT_OUTPUT = DATA / "sql_analysis_audit.csv"
DOC_OUTPUT = ROOT / "docs" / "SQL_ANALYSIS.md"
HTML_OUTPUT = ROOT / "site" / "sql-analysis.html"

QUERY_MARKER = re.compile(r"^-- QUERY: ([A-Z0-9]+) \| (.+?) \| (.+)$")
EXPECTED_QUERY_IDS = ("Q01", "Q02", "Q03", "Q04", "Q05", "Q06")
FORBIDDEN_SQL = re.compile(
    r"\b(ATTACH|DETACH|PRAGMA|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|VACUUM)\b",
    flags=re.IGNORECASE,
)

AUDIT_FIELDS = (
    "query_id",
    "title",
    "skills",
    "row_count",
    "check_name",
    "expected_value",
    "observed_value",
    "status",
    "notes",
)


@dataclass(frozen=True)
class QuerySpec:
    query_id: str
    title: str
    skills: str
    sql: str


TABLE_SPECS = {
    "national_year": {
        "path": PROCESSED / "national_year.csv",
        "columns": (
            "year", "institution_count", "total_enrollment", "nonresident_enrollment",
            "nonresident_share_pct", "yoy_nonresident_pct", "undergraduate_total",
            "undergraduate_nonresident", "graduate_total", "graduate_nonresident",
        ),
        "ddl": """
            CREATE TABLE national_year (
                year INTEGER PRIMARY KEY,
                institution_count INTEGER NOT NULL,
                total_enrollment INTEGER NOT NULL,
                nonresident_enrollment INTEGER NOT NULL,
                nonresident_share_pct REAL NOT NULL,
                yoy_nonresident_pct REAL,
                undergraduate_total INTEGER NOT NULL,
                undergraduate_nonresident INTEGER NOT NULL,
                graduate_total INTEGER NOT NULL,
                graduate_nonresident INTEGER NOT NULL
            )
        """,
    },
    "state_year": {
        "path": PROCESSED / "state_year.csv",
        "columns": (
            "year", "state", "institution_count", "total_enrollment",
            "nonresident_enrollment", "nonresident_share_pct", "undergraduate_total",
            "undergraduate_nonresident", "graduate_total", "graduate_nonresident",
        ),
        "ddl": """
            CREATE TABLE state_year (
                year INTEGER NOT NULL,
                state TEXT NOT NULL,
                institution_count INTEGER NOT NULL,
                total_enrollment INTEGER NOT NULL,
                nonresident_enrollment INTEGER NOT NULL,
                nonresident_share_pct REAL NOT NULL,
                undergraduate_total INTEGER NOT NULL,
                undergraduate_nonresident INTEGER NOT NULL,
                graduate_total INTEGER NOT NULL,
                graduate_nonresident INTEGER NOT NULL,
                PRIMARY KEY (year, state)
            )
        """,
    },
    "control_year": {
        "path": PROCESSED / "control_year.csv",
        "columns": (
            "year", "control", "institution_count", "total_enrollment",
            "nonresident_enrollment", "nonresident_share_pct",
            "undergraduate_nonresident", "graduate_nonresident",
        ),
        "ddl": """
            CREATE TABLE control_year (
                year INTEGER NOT NULL,
                control TEXT NOT NULL,
                institution_count INTEGER NOT NULL,
                total_enrollment INTEGER NOT NULL,
                nonresident_enrollment INTEGER NOT NULL,
                nonresident_share_pct REAL NOT NULL,
                undergraduate_nonresident INTEGER NOT NULL,
                graduate_nonresident INTEGER NOT NULL,
                PRIMARY KEY (year, control)
            )
        """,
    },
    "institutions_latest": {
        "path": PROCESSED / f"institutions_{END_YEAR}.csv",
        "columns": (
            "year", "unitid", "institution", "state", "control", "total_enrollment",
            "nonresident_enrollment", "nonresident_share_pct", "undergraduate_total",
            "undergraduate_nonresident", "graduate_total", "graduate_nonresident",
            "nonresident_imputation_flag", "total_imputation_flag",
            "source_enrollment_csv", "source_directory_csv",
        ),
        "ddl": """
            CREATE TABLE institutions_latest (
                year INTEGER NOT NULL,
                unitid INTEGER PRIMARY KEY,
                institution TEXT NOT NULL,
                state TEXT NOT NULL,
                control TEXT NOT NULL,
                total_enrollment INTEGER NOT NULL,
                nonresident_enrollment INTEGER NOT NULL,
                nonresident_share_pct REAL NOT NULL,
                undergraduate_total INTEGER,
                undergraduate_nonresident INTEGER,
                graduate_total INTEGER,
                graduate_nonresident INTEGER,
                nonresident_imputation_flag TEXT NOT NULL,
                total_imputation_flag TEXT NOT NULL,
                source_enrollment_csv TEXT NOT NULL,
                source_directory_csv TEXT NOT NULL
            )
        """,
    },
    "institution_change": {
        "path": PROCESSED / "institution_change_summary.csv",
        "columns": (
            "unitid", "institution", "state", "status", "control_2015",
            "control_2024", "nonresident_2015", "nonresident_2024", "absolute_change",
        ),
        "ddl": """
            CREATE TABLE institution_change (
                unitid INTEGER PRIMARY KEY,
                institution TEXT NOT NULL,
                state TEXT NOT NULL,
                status TEXT NOT NULL,
                control_2015 TEXT,
                control_2024 TEXT,
                nonresident_2015 INTEGER,
                nonresident_2024 INTEGER,
                absolute_change INTEGER NOT NULL
            )
        """,
    },
}

INTEGER_COLUMNS = {
    "year", "institution_count", "total_enrollment", "nonresident_enrollment",
    "undergraduate_total", "undergraduate_nonresident", "graduate_total",
    "graduate_nonresident", "unitid", "nonresident_2015", "nonresident_2024",
    "absolute_change",
}
REAL_COLUMNS = {"nonresident_share_pct", "yoy_nonresident_pct"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_queries(path: Path = QUERY_PACK) -> list[QuerySpec]:
    specs: list[QuerySpec] = []
    current_meta: tuple[str, str, str] | None = None
    current_sql: list[str] = []

    def flush() -> None:
        nonlocal current_meta, current_sql
        if current_meta is None:
            return
        sql = "\n".join(current_sql).strip()
        if not sql.endswith(";"):
            raise RuntimeError(f"SQL query {current_meta[0]} must end with a semicolon")
        if FORBIDDEN_SQL.search(sql):
            raise RuntimeError(f"SQL query {current_meta[0]} contains a non-read-only statement")
        if not sql.upper().startswith(("SELECT", "WITH")):
            raise RuntimeError(f"SQL query {current_meta[0]} must start with SELECT or WITH")
        specs.append(QuerySpec(*current_meta, sql))
        current_meta = None
        current_sql = []

    for line in path.read_text(encoding="utf-8").splitlines():
        marker = QUERY_MARKER.match(line)
        if marker:
            flush()
            current_meta = (marker.group(1), marker.group(2), marker.group(3))
            continue
        if current_meta is None:
            if line.strip():
                raise RuntimeError("SQL query pack contains text before the first QUERY marker")
            continue
        current_sql.append(line)
    flush()

    ids = tuple(spec.query_id for spec in specs)
    if ids != EXPECTED_QUERY_IDS:
        raise RuntimeError(f"SQL query IDs/order mismatch: {ids} != {EXPECTED_QUERY_IDS}")
    if len({spec.query_id for spec in specs}) != len(specs):
        raise RuntimeError("SQL query IDs must be unique")
    return specs


def convert_value(column: str, value: str) -> Any:
    if value == "":
        return None
    if column in INTEGER_COLUMNS:
        return int(value)
    if column in REAL_COLUMNS:
        return float(value)
    return value


def build_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    for table_name, spec in TABLE_SPECS.items():
        connection.execute(str(spec["ddl"]))
        path = Path(spec["path"])
        columns = tuple(spec["columns"])
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != columns:
                raise RuntimeError(
                    f"SQL source schema mismatch for {table_name}: {reader.fieldnames} != {columns}"
                )
            source_rows = list(reader)
        placeholders = ", ".join("?" for _ in columns)
        column_sql = ", ".join(columns)
        values = [
            tuple(convert_value(column, row[column]) for column in columns)
            for row in source_rows
        ]
        connection.executemany(
            f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholders})", values
        )
    connection.execute("PRAGMA query_only = ON")
    return connection


def execute_queries(
    connection: sqlite3.Connection, specs: list[QuerySpec]
) -> dict[str, list[dict[str, Any]]]:
    results: dict[str, list[dict[str, Any]]] = {}
    for spec in specs:
        cursor = connection.execute(spec.sql)
        rows = [dict(row) for row in cursor.fetchall()]
        if not rows:
            raise RuntimeError(f"SQL query {spec.query_id} returned no rows")
        results[spec.query_id] = rows
    return results


def expected_checks() -> dict[str, tuple[str, str, str]]:
    national = read_csv(PROCESSED / "national_year.csv")
    states = read_csv(PROCESSED / "state_year.csv")
    controls = read_csv(PROCESSED / "control_year.csv")
    institutions = read_csv(PROCESSED / f"institutions_{END_YEAR}.csv")
    changes = read_csv(PROCESSED / "institution_change_summary.csv")

    latest = next(row for row in national if int(row["year"]) == END_YEAR)
    prior = next(row for row in national if int(row["year"]) == END_YEAR - 1)
    latest_change = int(latest["nonresident_enrollment"]) - int(prior["nonresident_enrollment"])

    state_endpoints: dict[str, dict[int, int]] = {}
    for row in states:
        year = int(row["year"])
        if year in {2019, END_YEAR}:
            state_endpoints.setdefault(row["state"], {})[year] = int(row["nonresident_enrollment"])
    recovered = sum(
        values[END_YEAR] >= values[2019]
        for values in state_endpoints.values()
        if 2019 in values and END_YEAR in values
    )

    control_endpoints: dict[str, dict[int, int]] = {}
    for row in controls:
        year = int(row["year"])
        if year in {2015, END_YEAR}:
            control_endpoints.setdefault(row["control"], {})[year] = int(row["nonresident_enrollment"])
    top_control, top_values = max(
        control_endpoints.items(), key=lambda item: item[1][END_YEAR] - item[1][2015]
    )
    top_control_change = top_values[END_YEAR] - top_values[2015]

    top_institution = max(
        institutions,
        key=lambda row: (int(row["nonresident_enrollment"]), -int(row["unitid"])),
    )
    continuing_change = sum(
        int(row["absolute_change"]) for row in changes if row["status"].startswith("Continuing")
    )
    entry_exit_change = sum(
        int(row["absolute_change"]) for row in changes if not row["status"].startswith("Continuing")
    )
    national_change = int(latest["nonresident_enrollment"]) - int(
        next(row for row in national if int(row["year"]) == 2015)["nonresident_enrollment"]
    )

    return {
        "Q01": ("latest annual change", str(latest_change), "Latest SQL LAG difference matches canonical national CSV"),
        "Q02": ("states/DC at or above 2019", str(recovered), "SQL recovery classification matches canonical state CSV"),
        "Q03": ("largest control-group decade increase", f"{top_control}|{top_control_change}", "SQL control ranking matches canonical control CSV"),
        "Q04": ("largest latest-year institution", f"{top_institution['institution']}|{top_institution['nonresident_enrollment']}", "SQL institution ranking matches canonical institution CSV"),
        "Q05": ("institution-universe change accounting", f"{continuing_change}|{entry_exit_change}|{national_change}", "SQL continuing/entry-exit accounting reconciles to the national decade change"),
        "Q06": ("maximum state-to-national reconciliation delta", "0", "Every SQL state sum exactly matches the national CSV"),
    }


def observed_check(query_id: str, rows: list[dict[str, Any]]) -> str:
    if query_id == "Q01":
        latest = next(row for row in rows if int(row["year"]) == END_YEAR)
        return str(int(latest["annual_change"]))
    if query_id == "Q02":
        return str(sum(row["recovery_status"] == "AT_OR_ABOVE_2019" for row in rows))
    if query_id == "Q03":
        top = min(rows, key=lambda row: int(row["decade_change_rank"]))
        return f"{top['control']}|{int(top['decade_change'])}"
    if query_id == "Q04":
        top = min(rows, key=lambda row: int(row["institution_rank"]))
        return f"{top['institution']}|{int(top['nonresident_enrollment'])}"
    if query_id == "Q05":
        by_group = {row["movement_group"]: row for row in rows}
        continuing = int(by_group["Continuing institutions"]["net_change"])
        entry_exit = int(by_group["Universe entry/exit"]["net_change"])
        national = int(rows[0]["national_net_change"])
        return f"{continuing}|{entry_exit}|{national}"
    if query_id == "Q06":
        maximum = max(
            max(abs(int(row["nonresident_delta"])), abs(int(row["total_delta"])))
            for row in rows
        )
        return str(maximum)
    raise RuntimeError(f"No SQL audit check defined for {query_id}")


def build_audit(
    specs: list[QuerySpec], results: dict[str, list[dict[str, Any]]]
) -> list[dict[str, str]]:
    expected = expected_checks()
    audit: list[dict[str, str]] = []
    for spec in specs:
        check_name, expected_value, notes = expected[spec.query_id]
        observed = observed_check(spec.query_id, results[spec.query_id])
        status = "PASS" if observed == expected_value else "FAIL"
        audit.append({
            "query_id": spec.query_id,
            "title": spec.title,
            "skills": spec.skills,
            "row_count": str(len(results[spec.query_id])),
            "check_name": check_name,
            "expected_value": expected_value,
            "observed_value": observed,
            "status": status,
            "notes": notes,
        })
    failures = [row["query_id"] for row in audit if row["status"] != "PASS"]
    if failures:
        raise RuntimeError(f"SQL analysis audit failed: {failures}")
    return audit


def write_audit(rows: list[dict[str, str]]) -> None:
    with AUDIT_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, Any]], limit: int = 5) -> list[str]:
    shown = rows[:limit]
    columns = list(shown[0])
    output = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in shown:
        output.append("| " + " | ".join("" if row[column] is None else str(row[column]) for column in columns) + " |")
    return output


def render_outputs(
    specs: list[QuerySpec], results: dict[str, list[dict[str, Any]]], audit: list[dict[str, str]]
) -> None:
    markdown = [
        "# SQL Analysis and Reconciliation", "",
        "This layer demonstrates read-only SQL analysis over the project's validated processed CSVs. `scripts/build_sql_analysis.py` rebuilds an in-memory SQLite database on every run, loads five canonical CSV tables, executes the public query pack in `sql/portfolio_queries.sql`, and compares each query's result with an independently calculated value from the source CSVs. No SQLite database is stored or published.", "",
        f"**Queries executed:** {len(specs)}",
        f"**Query checks passed:** {sum(row['status'] == 'PASS' for row in audit)}/{len(audit)}",
        f"**Source tables loaded:** {len(TABLE_SPECS)}", "**Stored database artifacts:** 0", "",
        "## Query audit", "", "| Query | Purpose | Skills | Rows | Check | Status |", "| --- | --- | --- | ---: | --- | --- |",
    ]
    audit_by_id = {row["query_id"]: row for row in audit}
    for spec in specs:
        row = audit_by_id[spec.query_id]
        markdown.append(f"| {spec.query_id} | {spec.title} | {spec.skills} | {row['row_count']} | {row['check_name']}: `{row['observed_value']}` | {row['status']} |")
    for spec in specs:
        row = audit_by_id[spec.query_id]
        markdown.extend(["", f"## {spec.query_id}: {spec.title}", "", f"**SQL skills:** {spec.skills}", "", f"**Independent check:** {row['check_name']} = `{row['observed_value']}` ({row['status']})", "", *markdown_table(results[spec.query_id])])
        if len(results[spec.query_id]) > 5:
            markdown.append(f"\n_First 5 of {len(results[spec.query_id])} result rows shown._")
    markdown.extend(["", "## Reproduction", "", "```bash", "python scripts/build_sql_analysis.py", "```", "", "The SQL query pack is intentionally SELECT-only. The builder rejects data-definition or data-mutation statements so the SQL layer cannot rewrite the validated source tables.", ""])
    DOC_OUTPUT.write_text("\n".join(markdown), encoding="utf-8")

    cards = []
    for spec in specs:
        row = audit_by_id[spec.query_id]
        cards.append(f"""
            <article class="handoff-card" data-query-id="{html.escape(spec.query_id)}">
              <div class="handoff-card-head"><span>{html.escape(spec.query_id)}</span><span class="handoff-status handoff-status-ready">{html.escape(row['status'])}</span></div>
              <p class="case-kicker">{html.escape(spec.skills)}</p>
              <h2>{html.escape(spec.title)}</h2>
              <dl class="handoff-meta">
                <div><dt>Rows returned</dt><dd>{html.escape(row['row_count'])}</dd></div>
                <div><dt>Independent check</dt><dd>{html.escape(row['check_name'])}</dd></div>
                <div><dt>Observed</dt><dd>{html.escape(row['observed_value'])}</dd></div>
                <div><dt>Why it matters</dt><dd>{html.escape(row['notes'])}</dd></div>
              </dl>
            </article>""")
    audit_rows = "".join(f"<tr><td>{html.escape(row['query_id'])}</td><td>{html.escape(row['check_name'])}</td><td>{html.escape(row['expected_value'])}</td><td>{html.escape(row['observed_value'])}</td><td>{html.escape(row['status'])}</td></tr>" for row in audit)
    HTML_OUTPUT.write_text(f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Read-only SQLite analysis and reconciliation queries over validated IPEDS portfolio outputs."><meta name="theme-color" content="#10263c"><title>SQL Analysis | Higher Education Data Brief</title><link rel="stylesheet" href="styles.css"></head>
<body>
  <a class="skip-link" href="#main">Skip to SQL analysis</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="SQL analysis navigation"><a href="index.html">Brief</a><a href="research-memo.html">Memo</a><a href="publication-handoff.html">Handoff</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">SQL analysis</p><h1>Query the validated outputs, then reconcile the answers.</h1><p class="lede">Six read-only SQLite queries demonstrate common analyst patterns including joins, grouping, conditional aggregation, CTEs, ranking, and window functions. Every query has an independent check against the canonical CSV outputs.</p><div class="hero-actions"><a class="button button-primary" href="#query-catalog">Review SQL checks</a><a class="button button-secondary" href="downloads/portfolio_queries.sql">Download query pack</a></div><p class="release-note"><strong>Authority boundary:</strong> SQLite is rebuilt in memory from validated CSV outputs and is never stored or treated as a second source of truth.</p><div class="handoff-summary"><article><strong>{len(specs)}</strong><span>read-only queries</span></article><article><strong>{sum(row['status'] == 'PASS' for row in audit)}/{len(audit)}</strong><span>independent checks passed</span></article><article><strong>{len(TABLE_SPECS)}</strong><span>source tables loaded</span></article><article><strong>0</strong><span>stored database artifacts</span></article></div></div></section>
    <section class="section section-tinted" id="query-catalog"><div class="shell"><div class="section-heading"><p class="eyebrow">Query catalog</p><h2>Business-style questions with reproducible SQL</h2><p>The query pack is public and SELECT-only. The builder rejects mutation/DDL statements and stops the build if any reconciliation check fails.</p></div><div class="handoff-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Independent checks</p><h2>SQL results are compared with the CSV authorities</h2><p>Expected values are calculated directly from the validated source CSVs rather than copied from the SQL results.</p></div><div class="table-wrap"><table><thead><tr><th>Query</th><th>Check</th><th>Expected</th><th>Observed</th><th>Status</th></tr></thead><tbody>{audit_rows}</tbody></table></div><div class="memo-actions"><a class="button button-primary" href="downloads/sql_analysis_audit.csv">Download audit CSV</a><a class="button button-secondary" href="downloads/sql_analysis.md">Download SQL notes</a></div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Implementation boundary</p><h2>SQL adds a second way to interrogate the data, not a second authority</h2></div><div class="method-grid"><article><h3>Canonical inputs</h3><p>National, state, control, latest-institution, and institution-change CSVs remain the validated analytical outputs.</p></article><article><h3>Ephemeral database</h3><p>The SQLite database exists only for one build process and is recreated from source on every run.</p></article><article><h3>Read-only query pack</h3><p>The parser accepts only SELECT/WITH queries and rejects mutation, schema-change, attachment, and PRAGMA statements.</p></article><article><h3>Independent reconciliation</h3><p>Each query is checked against values calculated separately from the CSV sources before publication.</p></article></div></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>SQL Analysis · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body></html>
""", encoding="utf-8")


def main() -> int:
    specs = read_queries()
    connection = build_connection()
    try:
        results = execute_queries(connection, specs)
    finally:
        connection.close()
    audit = build_audit(specs, results)
    write_audit(audit)
    render_outputs(specs, results, audit)
    print(f"SQL analysis: {len(specs)} queries; {sum(row['status'] == 'PASS' for row in audit)}/{len(audit)} checks PASS")
    print(f"Wrote {AUDIT_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
