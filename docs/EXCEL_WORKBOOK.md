# Excel Review Workbook

`deliverables/ipeds_portfolio_analysis.xlsx` is the spreadsheet-facing version of the portfolio analysis. It is designed to demonstrate practical Excel/CSV research work in addition to the reproducible Python and web layers.

## Authority boundary

The workbook is a **downstream presentation artifact**. It does not define the project's source data or analytical results. The tracked CSV/JSON outputs produced by the validated pipeline remain authoritative. This prevents an edited spreadsheet cell from silently becoming a second source of truth.

The public build copies the tracked workbook byte-for-byte to `site/downloads/ipeds_portfolio_analysis.xlsx`.

## Workbook structure

### Executive Summary

- Formula-linked 2024 headline metrics.
- 2023-2024 and 2015-2024 change calculations.
- Graduate and undergraduate change decomposition.
- Formula-derived state recovery counts and largest gain/shortfall.
- State dropdown with `INDEX`/`MATCH` lookups into the state table.
- Plain-language interpretation boundary for the IPEDS U.S. nonresident category.

### National Trend

- 2015-2024 national enrollment series.
- Total, undergraduate, and graduate U.S. nonresident counts.
- Year-over-year change.
- Formula QA column checking that undergraduate plus graduate counts reconcile to the national total.
- National trend chart.

### State Review

- One row for each of the 50 states plus DC.
- 2015, 2019, and 2024 U.S. nonresident counts.
- Long-run and post-2019 changes and percentages.
- Recovery classification and 2024 enrollment share.
- Formula recalculation of 2019-2024 absolute change with `PASS`/`REVIEW` reconciliation.
- Conditional formatting to make gains, declines, and recovery status easy to scan.

### Institution Control

- Public, private nonprofit, and private for-profit series by year.
- Total and U.S. nonresident enrollment.
- Undergraduate/graduate composition.
- Formula reconciliation of level components to total U.S. nonresident enrollment.

### QA & Benchmark

- Latest-release high/medium/low review counts.
- Formula reconciliation of national change to undergraduate plus graduate change.
- Continuing-institution and analytic-universe entry/exit accounting.
- Full 24-row NCES Digest benchmark audit.
- Illustrative high-priority institution records from the latest-release QA queue.

### Source Library

- Structured metadata for the 11 maintained NCES and Higher Ed Immigration Portal resources.
- Publisher, resource type, scope, update pattern, project role, URL, review date, and status note.

## Workbook QA

The portfolio workbook was checked for formula errors and visually inspected before being added to the repository. Repository validation additionally verifies that:

- the XLSX ZIP container is internally valid;
- all six expected worksheets are present in order;
- worksheet XML contains formulas;
- the current 2024 headline value is present; and
- the public download is an exact byte-for-byte copy of the tracked deliverable.

The workbook's tracked SHA-256 at this release is `55dd866ff168945d7b683681d7ea294d7e31b5a1daef9fc378a5c38608afe2b5`.

## Annual maintenance

After a new IPEDS year has passed schema audit, QA, benchmark review, and narrative review, refresh the workbook from the newly validated outputs. Recheck formulas, lookup ranges, conditional formatting, chart ranges, and source metadata before replacing the tracked workbook. The workbook should never be used to override a result produced by the analytical pipeline.
