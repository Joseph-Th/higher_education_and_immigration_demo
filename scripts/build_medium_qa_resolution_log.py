"""Validate and publish evidence-backed decisions for the medium-priority QA queue."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE = DATA / "medium_qa_resolution_log.csv"
MEDIUM_REVIEW = DATA / "medium_priority_review.csv"
SUMMARY_OUTPUT = DATA / "medium_qa_resolution_summary.json"
DOC_OUTPUT = ROOT / "docs" / "MEDIUM_QA_RESOLUTION_LOG.md"
HTML_OUTPUT = ROOT / "site" / "medium-qa-review.html"

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
SAFE_UNITIDS = {"110635", "127820", "129941", "139755", "145637", "146427", "151111", "174428", "186867", "187897", "228459", "228769", "230782", "243780"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def decision_label(value: object) -> str:
    return {
        "safe_with_context": "Safe with context",
        "hold_for_confirmation": "Hold for confirmation",
    }.get(str(value), str(value).replace("_", " ").title())


def disposition_label(value: object) -> str:
    return str(value).replace("_", " ").capitalize()


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    source_rows = read_rows(SOURCE)
    review_rows = read_rows(MEDIUM_REVIEW)
    if len(review_rows) != 50:
        raise RuntimeError(f"Expected 50 medium-priority review rows, found {len(review_rows)}")
    if not source_rows or tuple(source_rows[0].keys()) != FIELDS:
        raise RuntimeError("Medium QA resolution log schema mismatch")

    review_by_unitid = {row["unitid"]: row for row in review_rows}
    source_unitids = [row["unitid"] for row in source_rows]
    review_unitids = [row["unitid"] for row in review_rows]
    if source_unitids != review_unitids:
        missing = sorted(set(review_unitids) - set(source_unitids))
        extra = sorted(set(source_unitids) - set(review_unitids))
        raise RuntimeError(
            "Medium QA resolution coverage/order mismatch; "
            f"missing={missing}, extra={extra}, ordered_match={source_unitids == review_unitids}"
        )

    joined: list[dict[str, object]] = []
    for resolution in source_rows:
        if any(not resolution[field].strip() for field in FIELDS):
            raise RuntimeError(f"Blank medium QA resolution field for UNITID {resolution['unitid']}")
        if resolution["publication_class"] not in PUBLICATION_CLASSES:
            raise RuntimeError(
                f"Unsupported publication class for UNITID {resolution['unitid']}: "
                f"{resolution['publication_class']}"
            )
        if not resolution["evidence_url"].startswith("https://"):
            raise RuntimeError(f"Medium QA evidence URL must use HTTPS: {resolution['unitid']}")
        try:
            date.fromisoformat(resolution["reviewed_on"])
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid reviewed_on date for UNITID {resolution['unitid']}: {resolution['reviewed_on']}"
            ) from exc

        review = review_by_unitid[resolution["unitid"]]
        if resolution["institution"] != review["institution"]:
            raise RuntimeError(
                f"Institution name mismatch for UNITID {resolution['unitid']}: "
                f"{resolution['institution']} != {review['institution']}"
            )
        joined.append(
            {
                **resolution,
                "state": review["state"],
                "control": review["control"],
                "absolute_change": int(review["absolute_change"]),
                "pct_change": review["pct_change"],
                "review_route": review["review_route"],
                "candidate_directory_overlap": review["candidate_directory_overlap"],
                "candidate_change_class": review["candidate_change_class"],
            }
        )

    safe_unitids = {
        str(row["unitid"])
        for row in joined
        if row["publication_class"] == "safe_with_context"
    }
    if safe_unitids != SAFE_UNITIDS:
        raise RuntimeError(
            f"Medium QA safe-with-context set changed: {sorted(safe_unitids)} != {sorted(SAFE_UNITIDS)}"
        )
    class_counts = Counter(str(row["publication_class"]) for row in joined)
    if class_counts != Counter({"safe_with_context": 14, "hold_for_confirmation": 36}):
        raise RuntimeError(f"Unexpected medium QA publication classes: {class_counts}")
    if any(
        row["publication_class"] == "safe_with_context"
        and row["disposition"] not in {"corroborated_external_count", "corroborated_direction", "expected_structural_change"}
        for row in joined
    ):
        raise RuntimeError("Safe medium QA rows must be corroborated counts/directions or documented structural changes")

    summary: dict[str, object] = {
        "medium_priority_total": len(review_rows),
        "reviewed_count": len(joined),
        "coverage_pct": round(len(joined) / len(review_rows) * 100, 1),
        "required_medium_priority_covered": len(joined) == len(review_rows),
        "safe_with_context": class_counts["safe_with_context"],
        "hold_for_confirmation": class_counts["hold_for_confirmation"],
        "dispositions": dict(Counter(str(row["disposition"]) for row in joined)),
        "candidate_overlap_reviewed": sum(
            row["candidate_directory_overlap"] == "yes" for row in joined
        ),
        "safe_unitids": sorted(SAFE_UNITIDS, key=int),
    }
    return joined, summary


def write_summary(summary: dict[str, object]) -> None:
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def write_markdown(rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    lines = [
        "# Medium-Priority QA Resolution Log",
        "",
        f"All **{summary['reviewed_count']}/{summary['medium_priority_total']} current medium-priority institution flags** now have an evidence-backed analyst disposition. The review preserves the official IPEDS values and separates bounded institution-specific discussion from records that still require directly comparable confirmation.",
        "",
        f"- **Safe with context:** {summary['safe_with_context']}",
        f"- **Held for confirmation:** {summary['hold_for_confirmation']}",
        f"- **Candidate-directory overlaps reviewed:** {summary['candidate_overlap_reviewed']}",
        f"- **Coverage:** {summary['coverage_pct']:.0f}%",
        "",
        "`safe_with_context` is deliberately narrow. It means external evidence supports the latest count scale, the observed direction, or a documented structural discontinuity strongly enough for bounded discussion. It does **not** mean an institution-defined international population is identical to IPEDS U.S. nonresident enrollment, and it never rewrites the IPEDS source value.",
        "",
        "## Complete medium-priority queue",
        "",
        "| Institution | State | 2023-2024 change | Route | Disposition | Publication class | Evidence |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['institution']} | {row['state']} | {int(row['absolute_change']):+,} | "
            f"{str(row['review_route']).replace('_', ' ').title()} | {disposition_label(row['disposition'])} | "
            f"{decision_label(row['publication_class'])} | [{row['evidence_label']}]({row['evidence_url']}) |"
        )
    lines.extend(
        [
            "",
            "## Analyst notes",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            [
                f"### {row['institution']} · UNITID {row['unitid']}",
                "",
                f"- **Decision:** {decision_label(row['publication_class'])}",
                f"- **Disposition:** {disposition_label(row['disposition'])}",
                f"- **Reviewed:** {row['reviewed_on']}",
                f"- **Evidence:** [{row['evidence_label']}]({row['evidence_url']})",
                f"- **Analyst note:** {row['analyst_note']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Publication and next-release boundary",
            "",
            "Held rows remain in all official aggregate calculations but are excluded from uncaveated institution-specific explanatory narrative. Safe rows may be discussed only within the limitation recorded above. Neither class is a correction to IPEDS.",
            "",
            "Every disposition is specific to the current 2023-2024 review. When the complete 2025 Fall Enrollment package arrives, the annual thresholds, structural context, and outside evidence must be re-evaluated. A current `safe_with_context` decision is not standing approval for the next release.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['institution']))}</td>"
            f"<td>{html.escape(str(row['state']))}</td>"
            f"<td>{int(row['absolute_change']):+,}</td>"
            f"<td>{html.escape(str(row['review_route']).replace('_', ' ').title())}</td>"
            f"<td>{html.escape(disposition_label(row['disposition']))}</td>"
            f"<td>{html.escape(decision_label(row['publication_class']))}</td>"
            f"<td><a href=\"{html.escape(str(row['evidence_url']), quote=True)}\" target=\"_blank\" rel=\"noopener\">{html.escape(str(row['evidence_label']))}</a></td>"
            "</tr>"
        )

    disposition_cards = []
    for disposition, count in sorted(
        dict(summary["dispositions"]).items(), key=lambda item: (-int(item[1]), item[0])
    ):
        disposition_cards.append(
            f"<article><h3>{html.escape(disposition_label(disposition))}</h3>"
            f"<p><strong>{int(count)}</strong><br>medium-priority records.</p></article>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Evidence-backed analyst dispositions for every medium-priority institution flag in the latest IPEDS release queue.">
  <meta name="theme-color" content="#10263c">
  <title>Medium-Priority QA Review | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to medium-priority QA review</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Medium QA evidence navigation"><a href="index.html">Brief</a><a href="medium-priority-review.html">Medium routing</a><a href="qa-review.html">High-priority QA</a><a href="candidate-year-watchlist.html">Next-release watchlist</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Medium-priority evidence review</p><h1>Every medium-priority flag now has an evidence-backed publication decision.</h1><p class="lede">The 50-row routing queue has been reviewed against institution-level public context. Fourteen records have enough corroboration for bounded discussion; 36 remain held because the outside source is non-comparable, incomplete, structural only, or otherwise insufficient to explain the IPEDS movement.</p><div class="hero-actions"><a class="button button-primary" href="#decisions">Review decisions</a><a class="button button-secondary" href="downloads/medium_qa_resolution_log.csv">Download resolution log</a></div><p class="release-note"><strong>Boundary:</strong> evidence can clear a bounded narrative claim without rewriting IPEDS. Current decisions must be revalidated on the next complete Fall Enrollment release.</p><div class="handoff-summary"><article><strong>{int(summary['reviewed_count'])}/{int(summary['medium_priority_total'])}</strong><span>medium-priority records reviewed</span></article><article><strong>{int(summary['safe_with_context'])}</strong><span>safe with explicit context</span></article><article><strong>{int(summary['hold_for_confirmation'])}</strong><span>held for confirmation</span></article><article><strong>{float(summary['coverage_pct']):.0f}%</strong><span>medium-priority queue coverage</span></article></div></div></section>
    <section class="section shell" id="decisions"><div class="section-heading"><p class="eyebrow">Disposition pattern</p><h2>Most medium signals remain intentionally gated after evidence review.</h2><p>A public international-student page is not automatically comparable to IPEDS U.S. nonresident enrollment. The analyst decision distinguishes exact or close count corroboration and documented structural discontinuities from sources that use a different population or do not publish the needed endpoints.</p></div><div class="method-grid">{''.join(disposition_cards)}</div></section>
    <section class="section section-tinted" id="complete-queue"><div class="shell"><div class="section-heading"><p class="eyebrow">Complete medium-priority queue</p><h2>Each routing signal now has a publication decision and evidence source.</h2><p>The route still describes why the deterministic threshold fired. The publication decision is a separate analyst layer and never changes the source value or current priority.</p></div><div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>Change</th><th>Route</th><th>Disposition</th><th>Publication decision</th><th>Evidence</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Interpretation rule</p><h2>Current evidence is not standing approval for a future release.</h2></div><div class="method-grid"><article><h3>Safe with context</h3><p>Independent evidence supports the count scale, direction, or a documented structural event strongly enough for bounded discussion.</p></article><article><h3>Hold for confirmation</h3><p>The official IPEDS value remains in aggregates, but an institution-specific explanation is not independently established.</p></article><article><h3>Scope control</h3><p>F-1, OPT, international-office, online-global, and institution-defined populations may not equal IPEDS U.S. nonresident enrollment.</p></article><article><h3>Next release</h3><p>All 50 rows are re-evaluated after the complete next Fall Enrollment build; no current disposition is inherited automatically.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/medium_qa_resolution_log.csv">Download resolution CSV</a><a class="button button-secondary" href="downloads/medium_qa_resolution_log.md">Download review notes</a><a class="button button-secondary" href="medium-priority-category-diagnostic.html">Review category diagnostic</a><a class="button button-secondary" href="medium-priority-review.html">Review routing layer</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Medium-Priority QA Review · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    joined, summary = build_rows()
    write_summary(summary)
    write_markdown(joined, summary)
    write_html(joined, summary)
    print(
        "Medium-priority QA resolution: "
        f"reviewed={summary['reviewed_count']}/{summary['medium_priority_total']}; "
        f"safe={summary['safe_with_context']}; held={summary['hold_for_confirmation']}"
    )
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
