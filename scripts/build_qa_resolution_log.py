"""Validate and render analyst dispositions for the high-priority annual QA queue.

The automated latest-release queue identifies records that deserve attention. This
file handles the next step: a manually curated, evidence-backed review of every
current high-priority record. It
does not rewrite source data. Instead it records whether outside evidence
corroborates a direction, explains a structural change, or leaves the item
unresolved for institution-specific publication.
"""

from __future__ import annotations

import csv
import html
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
HTML_OUTPUT = ROOT / "site" / "qa-review.html"

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


def decision_label(value: object) -> str:
    return {
        "safe_with_context": "Safe with context",
        "hold_for_confirmation": "Hold for confirmation",
    }.get(str(value), str(value).replace("_", " ").title())


def disposition_label(value: object) -> str:
    return str(value).replace("_", " ").capitalize()


def write_html(joined: list[dict[str, object]], summary: dict[str, object]) -> None:
    table_rows = []
    for row in joined:
        change = int(row["absolute_change"])
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['institution']))}</td>"
            f"<td>{html.escape(str(row['state']))}</td>"
            f"<td>{change:+,}</td>"
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
            f"<p><strong>{int(count)}</strong><br>high-priority records.</p></article>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Evidence-backed disposition review of every high-priority institution flag in the latest IPEDS release queue.">
  <meta name="theme-color" content="#10263c">
  <title>Institution QA Review | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to institution QA review</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="QA review navigation"><a href="index.html">Brief</a><a href="private-nonprofit-growth.html">Private nonprofit</a><a href="publication-handoff.html">Handoff</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Latest-release analyst review</p><h1>Every high-priority institution flag now has an evidence-backed publication decision.</h1><p class="lede">The automated queue identifies unusual 2023–2024 institution movements. The analyst layer reviews all {int(summary['high_priority_total'])} high-priority records without changing source values, then separates records that are safe to discuss with context from records that remain held for institution-specific interpretation.</p><div class="hero-actions"><a class="button button-primary" href="#dispositions">Review dispositions</a><a class="button button-secondary" href="downloads/qa_resolution_log.csv">Download resolution log</a></div><p class="release-note"><strong>Boundary:</strong> a flag is a request for review, not an error label. Aggregate IPEDS values remain authoritative even when an institution-specific narrative claim is held.</p><div class="handoff-summary"><article><strong>{int(summary['reviewed_count'])}/{int(summary['high_priority_total'])}</strong><span>high-priority records reviewed</span></article><article><strong>{int(summary['safe_with_context'])}</strong><span>safe with explicit context</span></article><article><strong>{int(summary['hold_for_confirmation'])}</strong><span>held for confirmation</span></article><article><strong>{float(summary['coverage_pct']):.0f}%</strong><span>high-priority queue coverage</span></article></div></div></section>
    <section class="section shell" id="dispositions"><div class="section-heading"><p class="eyebrow">Disposition pattern</p><h2>Most unusual movements remain intentionally gated.</h2><p>Outside evidence can corroborate direction, scale, or a structural event, but broader international-student counts are not assumed to equal IPEDS U.S. nonresident enrollment. The distribution below shows the analyst outcome across the complete high-priority queue.</p></div><div class="method-grid">{''.join(disposition_cards)}</div></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading"><p class="eyebrow">Complete high-priority queue</p><h2>Publication decisions remain attached to the institution record.</h2><p>Each row preserves the current IPEDS movement, the analyst disposition, the publication gate, and the external evidence used to evaluate whether an institution-specific interpretation is defensible.</p></div><div class="table-wrap"><table><thead><tr><th>Institution</th><th>State</th><th>2023–2024 change</th><th>Disposition</th><th>Publication decision</th><th>Evidence</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Interpretation rule</p><h2>Evidence can clear a narrative claim without rewriting the source data.</h2></div><div class="method-grid"><article><h3>Safe with context</h3><p>External evidence supports the direction, approximate scale, or structural event strongly enough for bounded discussion.</p></article><article><h3>Hold for confirmation</h3><p>The IPEDS value remains in aggregates, but the institution-specific movement should not be explained as substantive change without a directly comparable source.</p></article><article><h3>Scope control</h3><p>International, F-1, SEVIS, and institution-defined global counts may use different populations or dates from IPEDS U.S. nonresident enrollment.</p></article><article><h3>Internal composition check</h3><p>The companion category diagnostic measures opposite movement inside the IPEDS race/ethnicity identity. It prioritizes review but cannot change a publication decision by itself.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/qa_resolution_log.csv">Download resolution CSV</a><a class="button button-secondary" href="downloads/qa_resolution_log.md">Download review notes</a><a class="button button-secondary" href="high-priority-category-diagnostic.html">Open category diagnostic</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Institution QA Review · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


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
    required_high_priority = [
        row["unitid"] for row in queue_rows if row["review_priority"] == "high"
    ]
    required_top_10 = required_high_priority[:10]
    reviewed_order = [row["unitid"] for row in reviewed]
    if reviewed_order != required_high_priority:
        raise RuntimeError(
            "QA resolution log must match the current high-priority queue order exactly"
        )
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

    missing_required = [unitid for unitid in required_high_priority if unitid not in seen]
    if missing_required:
        raise RuntimeError(
            "QA resolution log must cover every current high-priority "
            f"records; missing UNITIDs: {', '.join(missing_required)}"
        )
    unexpected = [unitid for unitid in seen if unitid not in set(required_high_priority)]
    if unexpected:
        raise RuntimeError(
            "QA resolution log contains records outside the current high-priority queue: "
            + ", ".join(sorted(unexpected))
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
        "high_priority_total": len(required_high_priority),
        "coverage_pct": round(100 * len(joined) / len(required_high_priority), 1),
        "safe_with_context": classes["safe_with_context"],
        "hold_for_confirmation": classes["hold_for_confirmation"],
        "dispositions": dict(sorted(dispositions.items())),
        "reviewed_unitids": [row["unitid"] for row in joined],
        "required_high_priority_unitids": required_high_priority,
        "required_high_priority_covered": True,
        "required_top_10_unitids": required_top_10,
        "required_top_10_covered": True,
        "case_studies": case_studies,
        "latest_reviewed_on": max(row["reviewed_on"] for row in joined),
    }
    JSON_OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# QA Resolution Log",
        "",
        "The automated annual review queue is deliberately conservative: it flags large or unusual changes for analyst attention. This log records the evidence-backed publication decision for every record in the current high-priority queue. The review layer does not change IPEDS values; it determines whether an institution-specific interpretation is supportable.",
        "",
        "A disposition never overwrites IPEDS. `safe_with_context` means outside evidence is strong enough to discuss the direction or structural event with appropriate caveats. `hold_for_confirmation` means the official IPEDS value remains in aggregate calculations but should not drive an institution-specific claim until a directly comparable source is obtained.",
        "",
        "## Review summary",
        "",
        f"- **{len(joined)}/{len(required_high_priority)}** high-priority records manually reviewed (**{summary['coverage_pct']:.0f}% coverage**).",
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
    write_html(joined, summary)
    print(
        "QA resolution log: "
        f"{len(joined)}/{len(required_high_priority)} reviewed; "
        f"{classes['safe_with_context']} safe_with_context; "
        f"{classes['hold_for_confirmation']} hold_for_confirmation"
    )
    print(f"Wrote {JSON_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
