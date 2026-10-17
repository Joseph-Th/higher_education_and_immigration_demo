"""Build an internal category-countermovement diagnostic for high-priority QA.

The high-priority evidence review uses external sources to decide whether an
institution-specific narrative is publishable. This diagnostic answers a
different question from the same IPEDS source rows: when the U.S. nonresident
count changes sharply, how much enrollment simultaneously moves in the
opposite direction across the other mutually exclusive race/ethnicity
categories?

Countermovement is a review signal, not proof of miscoding or reclassification.
It never changes an IPEDS value or a publication disposition on its own.
"""

from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path

from ipeds_status import diagnostic_status_assessment
from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "ipeds"
PROCESSED = DATA / "processed"
QUEUE_PATH = PROCESSED / "latest_release_institution_review.csv"
RESOLUTION_PATH = DATA / "qa_resolution_log.csv"
SCHEMA_AUDIT = DATA / "schema_audit.csv"
CSV_OUTPUT = DATA / "high_priority_category_diagnostic.csv"
DOC_OUTPUT = ROOT / "docs" / "HIGH_PRIORITY_CATEGORY_DIAGNOSTIC.md"
HTML_OUTPUT = ROOT / "site" / "high-priority-category-diagnostic.html"

PRIOR_YEAR = END_YEAR - 1

CATEGORY_LABELS = {
    "EFAIANT": "American Indian / Alaska Native",
    "EFASIAT": "Asian",
    "EFBKAAT": "Black / African American",
    "EFHISPT": "Hispanic / Latino",
    "EFNHPIT": "Native Hawaiian / Pacific Islander",
    "EFWHITT": "White",
    "EF2MORT": "Two or more races",
    "EFUNKNT": "Race / ethnicity unknown",
}
ALL_CATEGORY_FIELDS = (*CATEGORY_LABELS, "EFNRALT")
STATUS_FIELDS = ("EFTOTLT", *ALL_CATEGORY_FIELDS)

FIELDS = (
    "unitid",
    "institution",
    "state",
    "status",
    "publication_class",
    "disposition",
    "source_status_class",
    "source_status_note",
    f"total_{PRIOR_YEAR}",
    f"total_{END_YEAR}",
    f"total_status_{PRIOR_YEAR}",
    f"total_status_{END_YEAR}",
    "total_change",
    f"nonresident_{PRIOR_YEAR}",
    f"nonresident_{END_YEAR}",
    f"nonresident_status_{PRIOR_YEAR}",
    f"nonresident_status_{END_YEAR}",
    "nonresident_change",
    "other_categories_net_change",
    "countermovement_abs",
    "countermovement_pct_of_nonresident_change",
    "largest_counter_category",
    "largest_counter_category_change",
    f"largest_counter_category_status_{PRIOR_YEAR}",
    f"largest_counter_category_status_{END_YEAR}",
    "signal_class",
    "prior_source_enrollment_csv",
    "current_source_enrollment_csv",
    "interpretation_boundary",
)

BOUNDARY = (
    "Countermovement across mutually exclusive IPEDS race/ethnicity categories is an internal QA signal, "
    "not proof of reporting error, miscoding, or student reclassification; publication decisions still require "
    "the evidence review."
)

SIGNAL_LABELS = {
    "countermovement_at_least_nr_change": "Countermovement at least as large as the nonresident change",
    "countermovement_at_least_half_nr_change": "Countermovement at least half as large as the nonresident change",
    "countermovement_below_half_nr_change": "Countermovement below half of the nonresident change",
    "endpoint_status_not_comparable": "Endpoint source status is not comparable for countermovement",
    "universe_change_not_comparable": "Analytic-universe change; category comparison not used",
}
COUNTERMOVEMENT_SIGNALS = {
    "countermovement_at_least_nr_change",
    "countermovement_at_least_half_nr_change",
    "countermovement_below_half_nr_change",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def source_filename(year: int) -> str:
    matches = [row for row in read_csv(SCHEMA_AUDIT) if int(row["year"]) == year]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one schema-audit row for {year}, found {len(matches)}")
    return matches[0]["enrollment_csv"]


def source_rows(year: int, unitids: set[str]) -> tuple[str, dict[str, dict[str, int | str]]]:
    filename = source_filename(year)
    path = RAW / str(year) / f"EF{year}A" / filename
    required = {
        "UNITID",
        "EFALEVEL",
        "EFTOTLT",
        *ALL_CATEGORY_FIELDS,
        *(f"X{field}" for field in STATUS_FIELDS),
    }
    result: dict[str, dict[str, int | str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"Missing category diagnostic fields in {path.name}: {sorted(missing)}")
        for row in reader:
            if row["UNITID"] not in unitids or row["EFALEVEL"].strip() != "1":
                continue
            unitid = row["UNITID"]
            if unitid in result:
                raise RuntimeError(f"Duplicate all-student row in {path.name}: {unitid}")
            values: dict[str, int | str] = {
                field: int(row[field]) for field in ("EFTOTLT", *ALL_CATEGORY_FIELDS)
            }
            values.update({f"X{field}": row[f"X{field}"].strip() for field in STATUS_FIELDS})
            category_sum = sum(values[field] for field in ALL_CATEGORY_FIELDS)
            if category_sum != values["EFTOTLT"]:
                raise RuntimeError(
                    f"Race/ethnicity categories do not reconcile to total in {year}/{unitid}: "
                    f"{category_sum} != {values['EFTOTLT']}"
                )
            result[unitid] = values
    return filename, result


def signal_class(countermovement: int, nonresident_change: int) -> tuple[str, str]:
    if nonresident_change == 0:
        return "countermovement_below_half_nr_change", "0.0"
    ratio = 100 * countermovement / abs(nonresident_change)
    if ratio >= 100:
        signal = "countermovement_at_least_nr_change"
    elif ratio >= 50:
        signal = "countermovement_at_least_half_nr_change"
    else:
        signal = "countermovement_below_half_nr_change"
    return signal, f"{ratio:.1f}"


def build_rows() -> list[dict[str, str]]:
    queue = [row for row in read_csv(QUEUE_PATH) if row["review_priority"] == "high"]
    resolutions = read_csv(RESOLUTION_PATH)
    by_resolution = {row["unitid"]: row for row in resolutions}
    queue_ids = [row["unitid"] for row in queue]
    if queue_ids != [row["unitid"] for row in resolutions]:
        raise RuntimeError("Category diagnostic requires the resolution log to match high-priority queue order")

    unitids = set(queue_ids)
    prior_filename, prior = source_rows(PRIOR_YEAR, unitids)
    current_filename, current = source_rows(END_YEAR, unitids)

    output: list[dict[str, str]] = []
    for queue_row in queue:
        unitid = queue_row["unitid"]
        resolution = by_resolution[unitid]
        base = {
            "unitid": unitid,
            "institution": queue_row["institution"],
            "state": queue_row["state"],
            "status": queue_row["status"],
            "publication_class": resolution["publication_class"],
            "disposition": resolution["disposition"],
            "prior_source_enrollment_csv": prior_filename,
            "current_source_enrollment_csv": current_filename,
            "interpretation_boundary": BOUNDARY,
        }
        if queue_row["status"] != "Continuing":
            output.append(
                {
                    **base,
                    f"total_{PRIOR_YEAR}": "",
                    f"total_{END_YEAR}": "",
                    "total_change": "",
                    f"nonresident_{PRIOR_YEAR}": queue_row[f"nonresident_{PRIOR_YEAR}"],
                    f"nonresident_{END_YEAR}": "",
                    "nonresident_change": queue_row["absolute_change"],
                    "other_categories_net_change": "",
                    "countermovement_abs": "",
                    "countermovement_pct_of_nonresident_change": "",
                    "largest_counter_category": "",
                    "largest_counter_category_change": "",
                    f"largest_counter_category_status_{PRIOR_YEAR}": "",
                    f"largest_counter_category_status_{END_YEAR}": "",
                    "source_status_class": "universe_change_not_comparable",
                    "source_status_note": "Analytic-universe change; endpoint source-status comparison withheld.",
                    f"total_status_{PRIOR_YEAR}": "",
                    f"total_status_{END_YEAR}": "",
                    f"nonresident_status_{PRIOR_YEAR}": "",
                    f"nonresident_status_{END_YEAR}": "",
                    "signal_class": "universe_change_not_comparable",
                }
            )
            continue

        if unitid not in prior or unitid not in current:
            raise RuntimeError(f"Continuing high-priority UNITID missing raw all-student row: {unitid}")
        before = prior[unitid]
        after = current[unitid]
        nr_change = int(after["EFNRALT"]) - int(before["EFNRALT"])
        if nr_change != int(queue_row["absolute_change"]):
            raise RuntimeError(
                f"Diagnostic nonresident change does not reconcile to queue for {unitid}: "
                f"{nr_change} != {queue_row['absolute_change']}"
            )
        total_change = int(after["EFTOTLT"]) - int(before["EFTOTLT"])
        deltas = {
            field: int(after[field]) - int(before[field])
            for field in CATEGORY_LABELS
        }
        other_net = sum(deltas.values())
        if total_change != nr_change + other_net:
            raise RuntimeError(f"Category change identity failed for {unitid}")

        status_comparable, status_note = diagnostic_status_assessment(
            before,
            after,
            STATUS_FIELDS,
            prior_year=PRIOR_YEAR,
            current_year=END_YEAR,
        )
        status_values = {
            "source_status_class": (
                "comparable_r_or_z" if status_comparable else "endpoint_status_not_comparable"
            ),
            "source_status_note": status_note,
            f"total_status_{PRIOR_YEAR}": str(before["XEFTOTLT"]),
            f"total_status_{END_YEAR}": str(after["XEFTOTLT"]),
            f"nonresident_status_{PRIOR_YEAR}": str(before["XEFNRALT"]),
            f"nonresident_status_{END_YEAR}": str(after["XEFNRALT"]),
        }

        if not status_comparable:
            output.append(
                {
                    **base,
                    **status_values,
                    f"total_{PRIOR_YEAR}": str(before["EFTOTLT"]),
                    f"total_{END_YEAR}": str(after["EFTOTLT"]),
                    "total_change": str(total_change),
                    f"nonresident_{PRIOR_YEAR}": str(before["EFNRALT"]),
                    f"nonresident_{END_YEAR}": str(after["EFNRALT"]),
                    "nonresident_change": str(nr_change),
                    "other_categories_net_change": str(other_net),
                    "countermovement_abs": "",
                    "countermovement_pct_of_nonresident_change": "",
                    "largest_counter_category": "",
                    "largest_counter_category_change": "",
                    f"largest_counter_category_status_{PRIOR_YEAR}": "",
                    f"largest_counter_category_status_{END_YEAR}": "",
                    "signal_class": "endpoint_status_not_comparable",
                }
            )
            continue

        opposite = [
            (field, change)
            for field, change in deltas.items()
            if change != 0 and ((nr_change > 0 and change < 0) or (nr_change < 0 and change > 0))
        ]
        countermovement = sum(abs(change) for _, change in opposite)
        if opposite:
            largest_field, largest_change = max(opposite, key=lambda item: (abs(item[1]), item[0]))
            largest_label = CATEGORY_LABELS[largest_field]
            largest_value = str(largest_change)
            largest_prior_status = str(before[f"X{largest_field}"])
            largest_current_status = str(after[f"X{largest_field}"])
        else:
            largest_label = ""
            largest_value = ""
            largest_prior_status = ""
            largest_current_status = ""
        signal, ratio = signal_class(countermovement, nr_change)

        output.append(
            {
                **base,
                **status_values,
                f"total_{PRIOR_YEAR}": str(before["EFTOTLT"]),
                f"total_{END_YEAR}": str(after["EFTOTLT"]),
                "total_change": str(total_change),
                f"nonresident_{PRIOR_YEAR}": str(before["EFNRALT"]),
                f"nonresident_{END_YEAR}": str(after["EFNRALT"]),
                "nonresident_change": str(nr_change),
                "other_categories_net_change": str(other_net),
                "countermovement_abs": str(countermovement),
                "countermovement_pct_of_nonresident_change": ratio,
                "largest_counter_category": largest_label,
                "largest_counter_category_change": largest_value,
                f"largest_counter_category_status_{PRIOR_YEAR}": largest_prior_status,
                f"largest_counter_category_status_{END_YEAR}": largest_current_status,
                "signal_class": signal,
            }
        )
    return output


def validate_rows(rows: list[dict[str, str]]) -> dict[str, int]:
    if len(rows) != 27 or len({row["unitid"] for row in rows}) != 27:
        raise RuntimeError("High-priority category diagnostic must contain 27 unique UNITIDs")
    counts = Counter(row["signal_class"] for row in rows)
    expected = {
        "countermovement_at_least_nr_change": 8,
        "countermovement_at_least_half_nr_change": 3,
        "countermovement_below_half_nr_change": 14,
        "universe_change_not_comparable": 2,
    }
    if dict(counts) != expected:
        raise RuntimeError(f"Unexpected category diagnostic signal distribution: {dict(counts)}")
    if counts["endpoint_status_not_comparable"] != 0:
        raise RuntimeError(f"Unexpected high-priority endpoint-status holds: {counts}")
    for row in rows:
        if row["status"] == "Continuing":
            total = int(row["total_change"])
            nr = int(row["nonresident_change"])
            other = int(row["other_categories_net_change"])
            if total != nr + other:
                raise RuntimeError(f"Output category identity failed for {row['unitid']}")
    return {
        "row_count": len(rows),
        "comparable_rows": sum(counts[key] for key in COUNTERMOVEMENT_SIGNALS),
        "status_noncomparable_rows": counts["endpoint_status_not_comparable"],
        "strong_countermovement": counts["countermovement_at_least_nr_change"],
        "material_countermovement": counts["countermovement_at_least_half_nr_change"],
        "limited_countermovement": counts["countermovement_below_half_nr_change"],
        "universe_change_rows": counts["universe_change_not_comparable"],
    }


def signed(value: str) -> str:
    return f"{int(value):+,}" if value else "—"


def ratio(value: str) -> str:
    return f"{float(value):.1f}%" if value else "—"


def status_codes(prior: str, current: str) -> str:
    return f"{prior}→{current}" if prior and current else "—"


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def ranked_comparable(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    comparable = [row for row in rows if row["signal_class"] in COUNTERMOVEMENT_SIGNALS]
    return sorted(
        comparable,
        key=lambda row: (
            -float(row["countermovement_pct_of_nonresident_change"]),
            -abs(int(row["nonresident_change"])),
            int(row["unitid"]),
        ),
    )


def write_markdown(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    lines = [
        "# High-Priority IPEDS Category Countermovement Diagnostic",
        "",
        f"This diagnostic adds an internal source-data check to the {summary['row_count']}-record high-priority {PRIOR_YEAR}-{END_YEAR} QA queue. For each continuing institution it reconciles the all-student IPEDS total to the mutually exclusive race/ethnicity categories, then measures how much of the other-category movement runs opposite the U.S. nonresident change.",
        "",
        "**Interpretation boundary:** countermovement is a review signal only. It can reflect real demographic turnover, reporting practice, classification changes, or a mixture of those mechanisms. It does not prove miscoding, does not correct IPEDS, and does not change the evidence-backed publication class by itself.",
        "",
        "## Summary",
        "",
        f"- **{summary['comparable_rows']}** continuing high-priority rows have a two-year category comparison.",
        f"- **{summary['strong_countermovement']}** have gross opposite-category movement at least as large as the absolute U.S. nonresident change.",
        f"- **{summary['material_countermovement']}** have opposite-category movement between 50% and 100% of the U.S. nonresident change.",
        f"- **{summary['limited_countermovement']}** have opposite-category movement below 50% of the U.S. nonresident change.",
        f"- **{summary['status_noncomparable_rows']}** continuing rows are withheld from the ratio because endpoint status codes fall outside the diagnostic R/Z rule.",
        f"- **{summary['universe_change_rows']}** analytic-universe exits are retained in the 27-row coverage but are not given a two-year category comparison.",
        "",
        "## Strongest internal countermovement signals",
        "",
        "| Institution | NR change | NR status | Total change | Opposite-category movement | Ratio to NR change | Largest opposite category | Category status | Publication gate |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in ranked_comparable(rows)[:10]:
        largest = row["largest_counter_category"]
        if largest:
            largest += f" ({signed(row['largest_counter_category_change'])})"
        lines.append(
            f"| {row['institution']} | {signed(row['nonresident_change'])} | {status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}'])} | {signed(row['total_change'])} | "
            f"{int(row['countermovement_abs']):,} | {ratio(row['countermovement_pct_of_nonresident_change'])} | "
            f"{largest or '—'} | "
            f"{status_codes(row[f'largest_counter_category_status_{PRIOR_YEAR}'], row[f'largest_counter_category_status_{END_YEAR}'])} | "
            f"{row['publication_class']} |"
        )

    lines.extend(
        [
            "",
            "## Complete diagnostic",
            "",
            "| Institution | Status | NR change | NR status | Other-category net change | Countermovement ratio | Signal | Publication gate |",
            "| --- | --- | ---: | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['institution']} | {row['status']} | {signed(row['nonresident_change'])} | "
            f"{status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}'])} | "
            f"{signed(row['other_categories_net_change'])} | {ratio(row['countermovement_pct_of_nonresident_change'])} | "
            f"{SIGNAL_LABELS[row['signal_class']]} | {row['publication_class']} |"
        )

    lines.extend(
        [
            "",
            "## Accounting rule",
            "",
            f"For each continuing institution, the {PRIOR_YEAR} and {END_YEAR} all-student IPEDS rows are checked separately so that `EFTOTLT` equals the sum of American Indian/Alaska Native, Asian, Black/African American, Hispanic/Latino, Native Hawaiian/Pacific Islander, White, Two or more races, Race/ethnicity unknown, and `EFNRALT`. The change identity must then satisfy `total change = nonresident change + net change across all other categories`. A countermovement ratio is calculated only when every endpoint total/category status code is `R` (Reported) or `Z` (Implied zero); other official status-coded values remain visible but are withheld from ratio comparison.",
            "",
            "Gross countermovement sums only category changes that move opposite the sign of the U.S. nonresident change. Because ordinary enrollment turnover can also create countermovement, the ratio is intentionally diagnostic rather than dispositive.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    signal_parts = (
        ("strong", "At least 100%", summary["strong_countermovement"], "Opposite-category movement is at least as large as the U.S. nonresident change"),
        ("material", "50% to 100%", summary["material_countermovement"], "Opposite-category movement is material but smaller than the U.S. nonresident change"),
        ("limited", "Below 50%", summary["limited_countermovement"], "Less opposite-category movement inside the same identity"),
        ("structural", "Universe change", summary["universe_change_rows"], "Structural exits are not forced into a two-year ratio"),
    )
    signal_bar = "".join(
        f'<i class="{css}" style="flex:{count}" title="{html.escape(label)}: {count}"></i>'
        for css, label, count, _ in signal_parts
    )
    signal_legend = "".join(
        f'<article data-category-signal="{css}"><span><i class="{css}"></i>{html.escape(label)}</span><strong>{count}</strong><small>{html.escape(note)}</small></article>'
        for css, label, count, note in signal_parts
    )
    table_rows = []
    for row in ranked_comparable(rows):
        largest = row["largest_counter_category"]
        if largest:
            largest = f"{largest} ({signed(row['largest_counter_category_change'])})"
        largest_status = status_codes(
            row[f"largest_counter_category_status_{PRIOR_YEAR}"],
            row[f"largest_counter_category_status_{END_YEAR}"],
        )
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(row['institution'])}</td>"
            f"<td>{signed(row['nonresident_change'])}</td>"
            f"<td>{html.escape(status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}']))}</td>"
            f"<td>{signed(row['total_change'])}</td>"
            f"<td>{int(row['countermovement_abs']):,}</td>"
            f"<td>{ratio(row['countermovement_pct_of_nonresident_change'])}</td>"
            f"<td>{html.escape(largest or '—')}</td>"
            f"<td>{html.escape(largest_status)}</td>"
            f"<td>{html.escape(row['publication_class'].replace('_', ' ').title())}</td>"
            "</tr>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Internal IPEDS category-countermovement diagnostic for the high-priority institution QA queue.">
  <meta name="theme-color" content="#10263c">
  <title>High-Priority Category Diagnostic | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to category diagnostic</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Category diagnostic navigation"><a href="index.html">Brief</a><a href="qa-review.html">QA review</a><a href="release-readiness.html">Readiness</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">High-priority internal QA</p><h1>Check whether a nonresident movement stands alone inside the IPEDS category identity.</h1><p class="lede">The evidence review asks whether outside sources support a narrative. This companion diagnostic stays inside IPEDS: it measures opposite movement across the other mutually exclusive race/ethnicity categories while preserving every source value and publication decision.</p><div class="hero-actions"><a class="button button-primary" href="#diagnostic-table">Review diagnostic</a><a class="button button-secondary" href="downloads/high_priority_category_diagnostic.csv">Download diagnostic CSV</a></div><p class="release-note"><strong>Boundary:</strong> countermovement is a QA signal, not proof of miscoding or reclassification. Real enrollment turnover can produce the same arithmetic pattern; the evidence-backed QA review remains the publication gate.</p><div class="handoff-summary"><article><strong>{summary['comparable_rows']}</strong><span>continuing rows compared</span></article><article><strong>{summary['strong_countermovement']}</strong><span>countermovement at least as large as NR change</span></article><article><strong>{summary['material_countermovement']}</strong><span>countermovement at least half as large</span></article><article><strong>{summary['universe_change_rows']}</strong><span>universe exits kept out of this comparison</span></article></div></div></section>
    <section class="section shell" id="signal-distribution"><div class="section-heading"><p class="eyebrow">How to read the signal</p><h2>The ratio prioritizes investigation; it does not diagnose the cause.</h2><p>Each continuing row first passes an exact category-to-total reconciliation in both years. The distribution below partitions all {summary['row_count']} high-priority rows without changing their separate evidence-backed publication decisions.</p></div><div class="category-signal-visual"><div class="category-signal-bar">{signal_bar}</div><div class="category-signal-legend">{signal_legend}</div></div><p class="category-signal-note"><strong>Diagnostic only:</strong> a large countermovement ratio can arise from real enrollment turnover. It is not evidence by itself that IPEDS was miscoded or reclassified.</p></section>
    <section class="section section-tinted" id="diagnostic-table"><div class="shell"><div class="section-heading"><p class="eyebrow">{summary['comparable_rows']} source-status-comparable high-priority rows</p><h2>Largest countermovement ratios remain available for audit.</h2><p>The institution-level arithmetic is intentionally subordinate to the evidence review. Source-status pairs remain exposed without turning this diagnostic into a correction or publication gate.</p></div><details class="evidence-details category-audit-details"><summary>Inspect all {summary['comparable_rows']} comparable high-priority rows</summary><div class="table-wrap"><table><thead><tr><th>Institution</th><th>NR change</th><th>NR status</th><th>Total change</th><th>Opposite movement</th><th>Ratio</th><th>Largest opposite category</th><th>Category status</th><th>Publication gate</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div></details></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Control rule</p><h2>Arithmetic can sharpen the review without becoming a correction layer.</h2></div><div class="method-grid"><article><h3>Exact identity</h3><p>Every comparable source row must reconcile the nine mutually exclusive IPEDS categories to total enrollment before a signal is calculated.</p></article><article><h3>Separate authority</h3><p>This diagnostic reads the same official IPEDS source rows but never substitutes a reconstructed count for <code>EFNRALT</code>.</p></article><article><h3>External evidence still matters</h3><p>Institution fact books, census reports, and source-status context remain necessary to distinguish reporting changes from substantive enrollment change.</p></article><article><h3>Next release</h3><p>Rebuild the diagnostic from the next complete Fall Enrollment package rather than carrying any current ratio forward.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/high_priority_category_diagnostic.csv">Download diagnostic CSV</a><a class="button button-secondary" href="downloads/high_priority_category_diagnostic.md">Download diagnostic note</a><a class="button button-secondary" href="qa-review.html">Return to evidence review</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>High-Priority Category Diagnostic · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
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
        "High-priority category diagnostic: "
        f"rows={summary['row_count']}; comparable={summary['comparable_rows']}; "
        f"strong={summary['strong_countermovement']}; material={summary['material_countermovement']}; "
        f"limited={summary['limited_countermovement']}; status_noncomparable={summary['status_noncomparable_rows']}; "
        f"universe_change={summary['universe_change_rows']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
