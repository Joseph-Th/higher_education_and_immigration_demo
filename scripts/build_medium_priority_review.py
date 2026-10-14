from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path

from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"

LATEST_REVIEW = PROCESSED / "latest_release_institution_review.csv"
CANDIDATE_CHANGES = DATA / "candidate_directory_change_review.csv"

CSV_OUTPUT = DATA / "medium_priority_review.csv"
DOC_OUTPUT = ROOT / "docs" / "MEDIUM_PRIORITY_REVIEW.md"
HTML_OUTPUT = ROOT / "site" / "medium-priority-review.html"

ROUTE_LABELS = {
    "PERCENTAGE_MOVEMENT": "Percentage movement",
    "ABSOLUTE_MOVEMENT": "Absolute movement",
    "ABSOLUTE_AND_PERCENTAGE": "Absolute + percentage movement",
    "STRUCTURAL_OR_REPORTING": "Structural / reporting context",
}
ROUTE_ORDER = {
    "STRUCTURAL_OR_REPORTING": 1,
    "ABSOLUTE_AND_PERCENTAGE": 2,
    "ABSOLUTE_MOVEMENT": 3,
    "PERCENTAGE_MOVEMENT": 4,
}
BOUNDARY = (
    "Medium-priority flag is a triage signal, not a source correction or publication clearance. "
    "Do not promote an institution-specific movement into narrative without evidence review."
)

FIELDS = (
    "review_order",
    "unitid",
    "institution",
    "state",
    "control",
    "status",
    f"nonresident_{END_YEAR - 1}",
    f"nonresident_{END_YEAR}",
    "absolute_change",
    "pct_change",
    f"flag_{END_YEAR - 1}",
    f"flag_{END_YEAR}",
    "flag_changed",
    "review_reasons",
    "review_route",
    "candidate_directory_overlap",
    "candidate_change_class",
    "candidate_change_reasons",
    "next_review_step",
    "interpretation_boundary",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def integer(value: str) -> int:
    return int(value) if value.strip() else 0


def signed(value: str | int) -> str:
    number = int(value)
    return f"{number:+,}" if number else "0"


def classify_route(reasons: str) -> str:
    if (
        "analytic-universe membership changed" in reasons
        or "imputation/status flag changed" in reasons
    ):
        return "STRUCTURAL_OR_REPORTING"
    if (
        "absolute change is at least 500 students" in reasons
        and (
            "percentage change is at least 50%" in reasons
            or "percentage change is at least 25%" in reasons
        )
    ):
        return "ABSOLUTE_AND_PERCENTAGE"
    if "absolute change is at least 500 students" in reasons:
        return "ABSOLUTE_MOVEMENT"
    if "percentage change is at least 50%" in reasons:
        return "PERCENTAGE_MOVEMENT"
    raise RuntimeError(f"Unrecognized medium-priority reason combination: {reasons}")


def review_step(route: str) -> str:
    if route == "STRUCTURAL_OR_REPORTING":
        return (
            "Review directory, imputation, or reporting-status evidence and reconcile the row to the next complete release "
            "before institution-specific interpretation."
        )
    if route == "ABSOLUTE_AND_PERCENTAGE":
        return (
            "Inspect multi-year IPEDS history and institution/source context because both count-scale and percentage thresholds fired."
        )
    if route == "ABSOLUTE_MOVEMENT":
        return (
            "Inspect multi-year IPEDS history and source status; verify that the large count movement is not a reporting or structural break."
        )
    if route == "PERCENTAGE_MOVEMENT":
        return (
            "Verify denominator scale and multi-year history before treating the percentage movement as substantive."
        )
    raise RuntimeError(f"Unknown review route: {route}")


def build_rows() -> list[dict[str, str]]:
    latest = [
        row for row in read_csv(LATEST_REVIEW) if row["review_priority"] == "medium"
    ]
    candidate = {row["unitid"]: row for row in read_csv(CANDIDATE_CHANGES)}
    if len(latest) != 50:
        raise RuntimeError(f"Expected 50 current medium-priority rows, found {len(latest)}")
    if len(candidate) != 154:
        raise RuntimeError(f"Expected 154 candidate directory change rows, found {len(candidate)}")

    rows: list[dict[str, str]] = []
    for row in latest:
        candidate_row = candidate.get(row["unitid"])
        route = classify_route(row["review_reasons"])
        rows.append(
            {
                "review_order": "",
                "unitid": row["unitid"],
                "institution": row["institution"],
                "state": row["state"],
                "control": row["control"],
                "status": row["status"],
                f"nonresident_{END_YEAR - 1}": row[f"nonresident_{END_YEAR - 1}"],
                f"nonresident_{END_YEAR}": row[f"nonresident_{END_YEAR}"],
                "absolute_change": row["absolute_change"],
                "pct_change": row["pct_change"],
                f"flag_{END_YEAR - 1}": row[f"flag_{END_YEAR - 1}"],
                f"flag_{END_YEAR}": row[f"flag_{END_YEAR}"],
                "flag_changed": row["flag_changed"],
                "review_reasons": row["review_reasons"],
                "review_route": route,
                "candidate_directory_overlap": "yes" if candidate_row else "no",
                "candidate_change_class": candidate_row["change_class"] if candidate_row else "",
                "candidate_change_reasons": candidate_row["change_reasons"] if candidate_row else "",
                "next_review_step": review_step(route),
                "interpretation_boundary": BOUNDARY,
            }
        )

    rows.sort(
        key=lambda row: (
            ROUTE_ORDER[row["review_route"]],
            -abs(integer(row["absolute_change"])),
            int(row["unitid"]),
        )
    )
    for order, row in enumerate(rows, start=1):
        row["review_order"] = str(order)
    return rows


def validate_rows(rows: list[dict[str, str]]) -> dict[str, int]:
    if len(rows) != 50:
        raise RuntimeError(f"Expected 50 medium-priority rows, found {len(rows)}")
    if len({row["unitid"] for row in rows}) != len(rows):
        raise RuntimeError("Medium-priority review contains duplicate UNITIDs")
    if [int(row["review_order"]) for row in rows] != list(range(1, 51)):
        raise RuntimeError("Medium-priority review_order is not sequential")
    if any(row["interpretation_boundary"] != BOUNDARY for row in rows):
        raise RuntimeError("Medium-priority interpretation boundary changed unexpectedly")

    routes = Counter(row["review_route"] for row in rows)
    expected_routes = Counter(
        {
            "PERCENTAGE_MOVEMENT": 28,
            "ABSOLUTE_MOVEMENT": 11,
            "ABSOLUTE_AND_PERCENTAGE": 8,
            "STRUCTURAL_OR_REPORTING": 3,
        }
    )
    if routes != expected_routes:
        raise RuntimeError(f"Medium-priority route counts changed: {routes}")

    statuses = Counter(row["status"] for row in rows)
    if statuses != Counter({"Continuing": 49, "Entered analytic universe": 1}):
        raise RuntimeError(f"Medium-priority status counts changed: {statuses}")
    controls = Counter(row["control"] for row in rows)
    if controls != Counter({"Public": 24, "Private nonprofit": 22, "Private for-profit": 4}):
        raise RuntimeError(f"Medium-priority control counts changed: {controls}")

    gains = [integer(row["absolute_change"]) for row in rows if integer(row["absolute_change"]) > 0]
    declines = [integer(row["absolute_change"]) for row in rows if integer(row["absolute_change"]) < 0]
    zero = [row for row in rows if integer(row["absolute_change"]) == 0]
    if (len(gains), len(declines), len(zero)) != (25, 23, 2):
        raise RuntimeError("Medium-priority direction counts changed unexpectedly")
    positive_movement = sum(gains)
    negative_movement = -sum(declines)
    if (positive_movement, negative_movement) != (7_806, 9_241):
        raise RuntimeError("Medium-priority movement totals changed unexpectedly")

    overlap = [row for row in rows if row["candidate_directory_overlap"] == "yes"]
    if {row["unitid"] for row in overlap} != {
        "157216",
        "114354",
        "115773",
        "244233",
        "417327",
    }:
        raise RuntimeError("Medium-priority candidate-directory overlap set changed unexpectedly")
    if sum(integer(row[f"nonresident_{END_YEAR}"]) for row in overlap) != 2_443:
        raise RuntimeError("Medium-priority candidate-directory overlap exposure changed unexpectedly")
    if sum(row["flag_changed"] == "yes" for row in rows) != 2:
        raise RuntimeError("Medium-priority flag-transition count changed unexpectedly")

    return {
        "row_count": len(rows),
        "percentage_route": routes["PERCENTAGE_MOVEMENT"],
        "absolute_route": routes["ABSOLUTE_MOVEMENT"],
        "combined_route": routes["ABSOLUTE_AND_PERCENTAGE"],
        "structural_route": routes["STRUCTURAL_OR_REPORTING"],
        "gain_rows": len(gains),
        "decline_rows": len(declines),
        "zero_rows": len(zero),
        "positive_movement": positive_movement,
        "negative_movement": negative_movement,
        "net_movement": positive_movement - negative_movement,
        "gross_movement": positive_movement + negative_movement,
        "candidate_overlap": len(overlap),
        "candidate_overlap_exposure": sum(integer(row[f"nonresident_{END_YEAR}"]) for row in overlap),
        "flag_change_rows": sum(row["flag_changed"] == "yes" for row in rows),
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def rows_by_route(rows: list[dict[str, str]], route: str) -> list[dict[str, str]]:
    return [row for row in rows if row["review_route"] == route]


def top_movement_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: -abs(integer(row["absolute_change"])))[:10]


def overlap_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["candidate_directory_overlap"] == "yes"]


def pct_display(row: dict[str, str]) -> str:
    return f"{float(row['pct_change']):+.1f}%" if row["pct_change"] else "—"


def route_label(route: str) -> str:
    return ROUTE_LABELS[route]


def candidate_signal(row: dict[str, str]) -> str:
    if row["candidate_directory_overlap"] != "yes":
        return "—"
    return f"{row['candidate_change_class'].replace('_', ' ').capitalize()}: {row['candidate_change_reasons'].replace(';', '; ')}"


def write_markdown(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    lines = [
        "# Medium-Priority Institution QA Triage",
        "",
        f"This review routes all **{summary['row_count']} current medium-priority {END_YEAR - 1}-{END_YEAR} institution flags** using only the reason codes already produced by the annual QA rules. It does not create a second risk score, resolve the records, or change source values.",
        "",
        "## What the queue represents",
        "",
        f"- **Percentage-movement route:** {summary['percentage_route']} rows",
        f"- **Absolute-movement route:** {summary['absolute_route']} rows",
        f"- **Absolute + percentage route:** {summary['combined_route']} rows",
        f"- **Structural/reporting route:** {summary['structural_route']} rows",
        f"- **Candidate-directory overlap:** {summary['candidate_overlap']} rows representing {summary['candidate_overlap_exposure']:,} current-year U.S. nonresident students",
        "",
        f"The queue is mixed-direction: {summary['gain_rows']} gain rows contribute **+{summary['positive_movement']:,}**, {summary['decline_rows']} decline rows contribute **-{summary['negative_movement']:,}**, and {summary['zero_rows']} rows have zero enrollment change. Net movement across the medium queue is **{summary['net_movement']:+,}** against **{summary['gross_movement']:,}** of gross absolute movement. These totals describe the flagged subset only and are not a national trend estimate.",
        "",
        "## Review routes",
        "",
        "| Route | Rows | What triggered the route | Review action |",
        "| --- | ---: | --- | --- |",
        f"| Structural / reporting context | {summary['structural_route']} | Analytic-universe change or non-R/Z imputation/status transition | Review structural/reporting evidence before interpreting movement |",
        f"| Absolute + percentage movement | {summary['combined_route']} | At least 500 students plus a percentage threshold | Inspect multi-year history and source/institution context |",
        f"| Absolute movement | {summary['absolute_route']} | At least 500 students without a medium-level percentage trigger | Inspect multi-year history and source status |",
        f"| Percentage movement | {summary['percentage_route']} | At least 50% from a 100+ baseline without a 500-student change | Verify denominator scale and multi-year history |",
        "",
        "## Largest medium-priority movements",
        "",
        "| Institution | State | Change | Percent | Route | Candidate directory overlap |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in top_movement_rows(rows):
        lines.append(
            f"| {row['institution']} | {row['state']} | {signed(row['absolute_change'])} | {pct_display(row)} | {route_label(row['review_route'])} | {'Yes' if row['candidate_directory_overlap'] == 'yes' else 'No'} |"
        )

    lines.extend(
        [
            "",
            "## Structural / reporting-context rows",
            "",
            "These three records require structural or reporting-context review before any institution-specific interpretation. Their presence does not establish an error.",
            "",
            "| Institution | Status | Change | Flags | Reason |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in rows_by_route(rows, "STRUCTURAL_OR_REPORTING"):
        lines.append(
            f"| {row['institution']} | {row['status']} | {signed(row['absolute_change'])} | {row[f'flag_{END_YEAR - 1}'] or '—'} → {row[f'flag_{END_YEAR}'] or '—'} | {row['review_reasons'].replace(' | ', '; ')} |"
        )

    lines.extend(
        [
            "",
            "## Medium-priority rows that also changed in the candidate directory",
            "",
            f"The {summary['candidate_overlap']} cross-signal overlaps should be reviewed with both the latest enrollment movement and candidate directory continuity visible. Their current {END_YEAR} U.S. nonresident enrollment sums to **{summary['candidate_overlap_exposure']:,}**.",
            "",
            "| Institution | State | Change | Review route | Candidate directory signal |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in overlap_rows(rows):
        lines.append(
            f"| {row['institution']} | {row['state']} | {signed(row['absolute_change'])} | {route_label(row['review_route'])} | {candidate_signal(row)} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            f"**{BOUNDARY}**",
            "",
            "The four routes describe why the existing medium-priority threshold fired and what evidence to inspect next. They are not severity grades. A candidate-directory overlap does not upgrade a row to high priority, and no medium row receives a publication disposition from this artifact.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    top_html = []
    for row in top_movement_rows(rows):
        top_html.append(
            "<tr>"
            f"<td>{html.escape(row['institution'])}</td>"
            f"<td>{html.escape(row['state'])}</td>"
            f"<td>{signed(row['absolute_change'])}</td>"
            f"<td>{html.escape(pct_display(row))}</td>"
            f"<td>{html.escape(route_label(row['review_route']))}</td>"
            f"<td>{'Yes' if row['candidate_directory_overlap'] == 'yes' else 'No'}</td>"
            "</tr>"
        )

    structural_html = []
    for row in rows_by_route(rows, "STRUCTURAL_OR_REPORTING"):
        flags = f"{row[f'flag_{END_YEAR - 1}'] or '—'} → {row[f'flag_{END_YEAR}'] or '—'}"
        structural_html.append(
            "<tr>"
            f"<td>{html.escape(row['institution'])}</td>"
            f"<td>{html.escape(row['status'])}</td>"
            f"<td>{signed(row['absolute_change'])}</td>"
            f"<td>{html.escape(flags)}</td>"
            f"<td>{html.escape(row['review_reasons'].replace(' | ', '; '))}</td>"
            "</tr>"
        )

    overlap_html = []
    for row in overlap_rows(rows):
        overlap_html.append(
            "<tr>"
            f"<td>{html.escape(row['institution'])}</td>"
            f"<td>{html.escape(row['state'])}</td>"
            f"<td>{signed(row['absolute_change'])}</td>"
            f"<td>{html.escape(route_label(row['review_route']))}</td>"
            f"<td>{html.escape(candidate_signal(row))}</td>"
            "</tr>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Medium-priority institution QA triage for the latest IPEDS release, using existing reason codes and candidate-directory overlap without inventing a new risk score.">
  <meta name="theme-color" content="#10263c">
  <title>Medium-Priority QA Triage | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to medium-priority QA triage</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Medium-priority QA navigation"><a href="index.html">Brief</a><a href="qa-review.html">High-priority QA</a><a href="candidate-year-watchlist.html">Next-release watchlist</a><a href="release-readiness.html">Release readiness</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell">
      <p class="eyebrow">Medium-priority institution QA</p>
      <h1>The 50-row medium queue is now routed without pretending it is resolved.</h1>
      <p class="lede">The review uses the annual QA reason codes already in the project to separate magnitude, percentage, and structural/reporting signals. It adds review actions and candidate-directory overlap without changing source values or creating a second risk score.</p>
      <div class="hero-actions"><a class="button button-primary" href="#routes">Review the four routes</a><a class="button button-secondary" href="downloads/medium_priority_review.csv">Download full review</a></div>
      <p class="release-note"><strong>Boundary:</strong> {html.escape(BOUNDARY)}</p>
      <div class="handoff-summary">
        <article><strong>{summary['row_count']}</strong><span>current medium-priority rows</span></article>
        <article><strong>{summary['percentage_route']}</strong><span>percentage-movement route</span></article>
        <article><strong>{summary['structural_route']}</strong><span>structural / reporting-context rows</span></article>
        <article><strong>{summary['candidate_overlap']}</strong><span>candidate-directory overlaps</span></article>
      </div>
    </div></section>

    <section class="section shell" id="routes">
      <div class="section-heading"><p class="eyebrow">Review taxonomy</p><h2>Four routes describe the signal; none is a severity grade.</h2><p>The existing medium-priority threshold remains authoritative. This layer only makes the next analyst action explicit and reproducible.</p></div>
      <div class="method-grid">
        <article><h3>Structural / reporting</h3><p><strong>{summary['structural_route']} rows</strong><br>Universe membership or non-R/Z reporting-status transitions require structural evidence before interpretation.</p></article>
        <article><h3>Absolute + percentage</h3><p><strong>{summary['combined_route']} rows</strong><br>Both count-scale and percentage thresholds fired; inspect history and institution/source context together.</p></article>
        <article><h3>Absolute movement</h3><p><strong>{summary['absolute_route']} rows</strong><br>At least 500 students changed without a medium-level percentage trigger.</p></article>
        <article><h3>Percentage movement</h3><p><strong>{summary['percentage_route']} rows</strong><br>At least 50% from a 100+ baseline without a 500-student change; denominator scale matters.</p></article>
      </div>
    </section>

    <section class="section section-tinted"><div class="shell">
      <div class="section-heading"><p class="eyebrow">Queue accounting</p><h2>Mixed directions are another reason not to read the queue as a trend.</h2><p>{summary['gain_rows']} gain rows contribute +{summary['positive_movement']:,}; {summary['decline_rows']} decline rows contribute -{summary['negative_movement']:,}; {summary['zero_rows']} rows have zero enrollment change. Net movement is {summary['net_movement']:+,} across {summary['gross_movement']:,} of gross absolute movement. Those totals describe the flagged subset only.</p></div>
      <div class="handoff-summary">
        <article><strong>{summary['gain_rows']}</strong><span>gain rows</span></article>
        <article><strong>{summary['decline_rows']}</strong><span>decline rows</span></article>
        <article><strong>{summary['gross_movement']:,}</strong><span>gross absolute movement</span></article>
        <article><strong>{summary['net_movement']:+,}</strong><span>net across medium rows</span></article>
      </div>
    </div></section>

    <section class="section shell" id="largest-movements">
      <div class="section-heading"><p class="eyebrow">Largest medium signals</p><h2>The ten largest count movements span multiple review routes.</h2><p>Size alone does not resolve the record. Candidate-directory overlap is shown as context for the eventual next-release reconciliation.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>Change</th><th>Percent</th><th>Review route</th><th>Candidate overlap</th></tr></thead><tbody>{''.join(top_html)}</tbody></table></div>
    </section>

    <section class="section section-tinted" id="structural-reporting"><div class="shell">
      <div class="section-heading"><p class="eyebrow">Structural / reporting context</p><h2>Three medium rows are not ordinary movement-only cases.</h2><p>Two rows have a non-R/Z reporting-status transition and one entered the analytic universe. These signals require structural review before institution-specific interpretation; they do not establish a source error.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Institution</th><th>Status</th><th>Change</th><th>Flags</th><th>Reason</th></tr></thead><tbody>{''.join(structural_html)}</tbody></table></div>
    </div></section>

    <section class="section shell" id="candidate-overlap">
      <div class="section-heading"><p class="eyebrow">Cross-signal overlap</p><h2>Five medium rows also changed in the candidate directory.</h2><p>These rows represent {summary['candidate_overlap_exposure']:,} current-year U.S. nonresident students. The overlap means enrollment and directory continuity should be reviewed together; it does not upgrade the current priority or clear the record for narrative use.</p></div>
      <div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>Change</th><th>Review route</th><th>Candidate directory signal</th></tr></thead><tbody>{''.join(overlap_html)}</tbody></table></div>
    </section>

    <section class="section section-tinted"><div class="shell">
      <div class="section-heading compact"><p class="eyebrow">Operating rule</p><h2>Route the evidence need, not the conclusion.</h2></div>
      <div class="method-grid">
        <article><h3>No automatic correction</h3><p>The IPEDS values remain authoritative unless the source pipeline itself is shown to be wrong.</p></article>
        <article><h3>No automatic clearance</h3><p>Medium-priority rows receive no publication class from this routing layer.</p></article>
        <article><h3>No new risk score</h3><p>The route comes directly from the reasons that already triggered the medium threshold.</p></article>
        <article><h3>Next release</h3><p>Reapply the annual rules after the complete {END_YEAR + 1} build and reconcile any candidate-directory signal at the same time.</p></article>
      </div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/medium_priority_review.csv">Download review CSV</a><a class="button button-secondary" href="downloads/medium_priority_review.md">Download review note</a><a class="button button-secondary" href="qa-review.html">High-priority review</a><a class="button button-secondary" href="candidate-year-watchlist.html">Candidate-year watchlist</a></div>
    </div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Medium-Priority QA Triage · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows = build_rows()
    summary = validate_rows(rows)
    write_csv(rows)
    write_markdown(rows, summary)
    write_html(rows, summary)
    print(
        "Medium-priority QA triage: "
        f"rows={summary['row_count']}; percentage={summary['percentage_route']}; "
        f"absolute={summary['absolute_route']}; combined={summary['combined_route']}; "
        f"structural={summary['structural_route']}; candidate_overlap={summary['candidate_overlap']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
