"""Build an internal category-countermovement diagnostic for medium-priority QA.

This companion to the medium-priority routing and evidence-review layers stays
inside the official IPEDS source rows.  For each continuing institution it
reconciles the all-student race/ethnicity identity and measures gross movement
in other categories that runs opposite the U.S. nonresident change.

The result is an arithmetic review signal only.  It is not a second risk score,
does not correct IPEDS, and cannot change an evidence-backed publication class.
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
REVIEW_PATH = DATA / "medium_priority_review.csv"
RESOLUTION_PATH = DATA / "medium_qa_resolution_log.csv"
SCHEMA_AUDIT = DATA / "schema_audit.csv"
CSV_OUTPUT = DATA / "medium_priority_category_diagnostic.csv"
DOC_OUTPUT = ROOT / "docs" / "MEDIUM_PRIORITY_CATEGORY_DIAGNOSTIC.md"
HTML_OUTPUT = ROOT / "site" / "medium-priority-category-diagnostic.html"

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
    "review_order",
    "unitid",
    "institution",
    "state",
    "status",
    "review_route",
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
    "not a second risk score and not proof of reporting error, miscoding, or student reclassification; "
    "publication decisions still require the separate evidence review."
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
    review = read_csv(REVIEW_PATH)
    resolutions = read_csv(RESOLUTION_PATH)
    if len(review) != 50:
        raise RuntimeError(f"Expected 50 medium-priority review rows, found {len(review)}")
    if [row["unitid"] for row in review] != [row["unitid"] for row in resolutions]:
        raise RuntimeError("Medium category diagnostic requires resolution rows to match review order")
    by_resolution = {row["unitid"]: row for row in resolutions}

    unitids = {row["unitid"] for row in review}
    prior_filename, prior = source_rows(PRIOR_YEAR, unitids)
    current_filename, current = source_rows(END_YEAR, unitids)

    output: list[dict[str, str]] = []
    for review_row in review:
        unitid = review_row["unitid"]
        resolution = by_resolution[unitid]
        base = {
            "review_order": review_row["review_order"],
            "unitid": unitid,
            "institution": review_row["institution"],
            "state": review_row["state"],
            "status": review_row["status"],
            "review_route": review_row["review_route"],
            "publication_class": resolution["publication_class"],
            "disposition": resolution["disposition"],
            "prior_source_enrollment_csv": prior_filename,
            "current_source_enrollment_csv": current_filename,
            "interpretation_boundary": BOUNDARY,
        }

        if review_row["status"] != "Continuing":
            output.append(
                {
                    **base,
                    f"total_{PRIOR_YEAR}": "",
                    f"total_{END_YEAR}": "",
                    "total_change": "",
                    f"nonresident_{PRIOR_YEAR}": review_row[f"nonresident_{PRIOR_YEAR}"],
                    f"nonresident_{END_YEAR}": review_row[f"nonresident_{END_YEAR}"],
                    "nonresident_change": review_row["absolute_change"],
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
            raise RuntimeError(f"Continuing medium-priority UNITID missing raw all-student row: {unitid}")
        before = prior[unitid]
        after = current[unitid]
        nr_change = int(after["EFNRALT"]) - int(before["EFNRALT"])
        if nr_change != int(review_row["absolute_change"]):
            raise RuntimeError(
                f"Diagnostic nonresident change does not reconcile to medium review for {unitid}: "
                f"{nr_change} != {review_row['absolute_change']}"
            )

        total_change = int(after["EFTOTLT"]) - int(before["EFTOTLT"])
        deltas = {field: int(after[field]) - int(before[field]) for field in CATEGORY_LABELS}
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
    if len(rows) != 50 or len({row["unitid"] for row in rows}) != 50:
        raise RuntimeError("Medium-priority category diagnostic must contain 50 unique UNITIDs")
    if [int(row["review_order"]) for row in rows] != list(range(1, 51)):
        raise RuntimeError("Medium-priority category diagnostic review order changed")
    counts = Counter(row["signal_class"] for row in rows)
    expected_counts = Counter(
        {
            "countermovement_at_least_nr_change": 18,
            "countermovement_at_least_half_nr_change": 9,
            "countermovement_below_half_nr_change": 20,
            "endpoint_status_not_comparable": 2,
            "universe_change_not_comparable": 1,
        }
    )
    if counts != expected_counts:
        raise RuntimeError(f"Medium category signal distribution changed: {counts} != {expected_counts}")
    comparable = sum(counts[key] for key in COUNTERMOVEMENT_SIGNALS)
    if comparable + counts["endpoint_status_not_comparable"] + counts["universe_change_not_comparable"] != len(rows):
        raise RuntimeError(f"Medium category signal coverage is incomplete: {counts}")
    for row in rows:
        if row["status"] == "Continuing":
            if int(row["total_change"]) != int(row["nonresident_change"]) + int(row["other_categories_net_change"]):
                raise RuntimeError(f"Output category identity failed for {row['unitid']}")
        elif row["signal_class"] != "universe_change_not_comparable":
            raise RuntimeError(f"Structural medium row received a composition signal: {row['unitid']}")
    return {
        "row_count": len(rows),
        "comparable_rows": comparable,
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


def route_label(value: str) -> str:
    return value.replace("_", " ").title()


def ranked_comparable(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        (row for row in rows if row["signal_class"] in COUNTERMOVEMENT_SIGNALS),
        key=lambda row: (
            -float(row["countermovement_pct_of_nonresident_change"]),
            -abs(int(row["nonresident_change"])),
            int(row["unitid"]),
        ),
    )


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    lines = [
        "# Medium-Priority IPEDS Category Countermovement Diagnostic",
        "",
        f"This diagnostic adds the same internal source-data arithmetic check used for high-priority QA to all **{summary['row_count']} current medium-priority {PRIOR_YEAR}-{END_YEAR} records**. It remains separate from both the reason-derived routing layer and the evidence-backed publication decision.",
        "",
        "**Interpretation boundary:** countermovement is a review-prioritization signal only. It is not a second risk score, does not prove miscoding or reclassification, does not correct IPEDS, and cannot clear or hold an institution-specific claim by itself.",
        "",
        "## Summary",
        "",
        f"- **{summary['comparable_rows']}** continuing medium-priority rows have a two-year category comparison under the diagnostic R/Z endpoint-status rule.",
        f"- **{summary['strong_countermovement']}** have opposite-category movement at least as large as the absolute U.S. nonresident change.",
        f"- **{summary['material_countermovement']}** have opposite-category movement between 50% and 100% of the U.S. nonresident change.",
        f"- **{summary['limited_countermovement']}** have opposite-category movement below 50% of the U.S. nonresident change.",
        f"- **{summary['status_noncomparable_rows']}** continuing rows are retained but receive no countermovement ratio because an endpoint uses a status outside R/Z.",
        f"- **{summary['universe_change_rows']}** analytic-universe change is retained for complete queue coverage but not forced into a two-year composition comparison.",
        "",
        "## Strongest internal countermovement signals",
        "",
        "| Institution | Route | NR change | NR status | Total change | Opposite-category movement | Ratio | Largest opposite category | Category status | Publication gate |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in ranked_comparable(rows)[:15]:
        largest = row["largest_counter_category"]
        if largest:
            largest += f" ({signed(row['largest_counter_category_change'])})"
        lines.append(
            f"| {row['institution']} | {route_label(row['review_route'])} | {signed(row['nonresident_change'])} | "
            f"{status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}'])} | "
            f"{signed(row['total_change'])} | {int(row['countermovement_abs']):,} | "
            f"{ratio(row['countermovement_pct_of_nonresident_change'])} | {largest or '—'} | "
            f"{status_codes(row[f'largest_counter_category_status_{PRIOR_YEAR}'], row[f'largest_counter_category_status_{END_YEAR}'])} | "
            f"{row['publication_class']} |"
        )
    lines.extend(
        [
            "",
            "## Complete medium-priority diagnostic",
            "",
            "| Order | Institution | State | Route | NR change | NR status | Countermovement | Ratio | Signal | Publication gate |",
            "| ---: | --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['review_order']} | {row['institution']} | {row['state']} | {route_label(row['review_route'])} | "
            f"{signed(row['nonresident_change'])} | "
            f"{status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}'])} | "
            f"{int(row['countermovement_abs']):,} | {ratio(row['countermovement_pct_of_nonresident_change'])} | "
            f"{SIGNAL_LABELS[row['signal_class']]} | {row['publication_class']} |"
            if row["countermovement_abs"]
            else f"| {row['review_order']} | {row['institution']} | {row['state']} | {route_label(row['review_route'])} | "
            f"{signed(row['nonresident_change'])} | "
            f"{status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}'])} | "
            f"— | — | {SIGNAL_LABELS[row['signal_class']]} | {row['publication_class']} |"
        )
    lines.extend(
        [
            "",
            "## Accounting and decision rule",
            "",
            f"For each continuing institution, both endpoint all-student IPEDS rows must reconcile `EFTOTLT` to the nine mutually exclusive race/ethnicity categories including `EFNRALT`, and the change identity must satisfy `total change = nonresident change + net change across all other categories`. A countermovement ratio is calculated only when every endpoint total/category status code is `R` (Reported) or `Z` (Implied zero). Other official status-coded values remain in the source arithmetic but are withheld from the ratio. The diagnostic copies the medium evidence-review publication class only to keep arithmetic and analyst evidence visible together.",
            "",
            "A large ratio changes neither the medium-priority route nor the publication class. Institution-specific discussion still depends on the separate evidence review, and every current disposition must be revalidated after the next complete Fall Enrollment release.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], summary: dict[str, int]) -> None:
    signal_parts = (
        ("strong", "At least 100%", summary["strong_countermovement"], "Opposite-category movement is at least as large as the U.S. nonresident change"),
        ("material", "50% to 100%", summary["material_countermovement"], "Opposite-category movement is material but smaller than the U.S. nonresident change"),
        ("limited", "Below 50%", summary["limited_countermovement"], "Less opposite-category movement inside the same identity"),
        ("withheld", "Status withheld", summary["status_noncomparable_rows"], "Official endpoint statuses fall outside the R/Z ratio rule"),
        ("structural", "Universe change", summary["universe_change_rows"], "Structural entry is not forced into a two-year ratio"),
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
            f"<td>{html.escape(route_label(row['review_route']))}</td>"
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

    status_rows = []
    for row in rows:
        if row["signal_class"] != "endpoint_status_not_comparable":
            continue
        status_rows.append(
            "<tr>"
            f"<td>{html.escape(row['institution'])}</td>"
            f"<td>{html.escape(route_label(row['review_route']))}</td>"
            f"<td>{signed(row['nonresident_change'])}</td>"
            f"<td>{html.escape(status_codes(row[f'nonresident_status_{PRIOR_YEAR}'], row[f'nonresident_status_{END_YEAR}']))}</td>"
            f"<td>{html.escape(status_codes(row[f'total_status_{PRIOR_YEAR}'], row[f'total_status_{END_YEAR}']))}</td>"
            f"<td>{html.escape(row['source_status_note'])}</td>"
            f"<td>{html.escape(row['publication_class'].replace('_', ' ').title())}</td>"
            "</tr>"
        )

    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Internal IPEDS category-countermovement diagnostic for the medium-priority institution QA queue.">
  <meta name="theme-color" content="#10263c">
  <title>Medium-Priority Category Diagnostic | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to medium-priority category diagnostic</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Medium category diagnostic navigation"><a href="index.html">Brief</a><a href="medium-priority-review.html">Medium routing</a><a href="medium-qa-review.html">Evidence review</a><a href="release-readiness.html">Readiness</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Medium-priority internal QA</p><h1>Extend the IPEDS composition check across the full medium-priority queue.</h1><p class="lede">The routing layer says why a medium threshold fired and the evidence layer says what may be published. This diagnostic answers a third, narrower question: how much other-category movement runs opposite the U.S. nonresident change inside the same IPEDS all-student identity?</p><div class="hero-actions"><a class="button button-primary" href="#diagnostic-table">Review diagnostic</a><a class="button button-secondary" href="downloads/medium_priority_category_diagnostic.csv">Download diagnostic CSV</a></div><p class="release-note"><strong>Boundary:</strong> the ratio is not another risk score or a diagnosis. It cannot correct IPEDS, change the reason-derived route, or override the evidence-backed publication decision. Endpoint status codes are checked before a ratio is calculated.</p><div class="handoff-summary"><article><strong>{summary['comparable_rows']}</strong><span>source-status-comparable rows</span></article><article><strong>{summary['strong_countermovement']}</strong><span>countermovement at least as large as NR change</span></article><article><strong>{summary['status_noncomparable_rows']}</strong><span>imputed/status-coded endpoints withheld</span></article><article><strong>{summary['universe_change_rows']}</strong><span>structural row kept non-comparable</span></article></div></div></section>
    <section class="section shell" id="medium-signal-distribution"><div class="section-heading"><p class="eyebrow">Three distinct QA layers</p><h2>Arithmetic sharpens review without becoming a publication gate.</h2><p>Every continuing row first passes the exact category-to-total identity. The distribution partitions all {summary['row_count']} medium-priority rows, while route, source status, and evidence remain separate controls.</p></div><div class="category-signal-visual"><div class="category-signal-bar">{signal_bar}</div><div class="category-signal-legend">{signal_legend}</div></div><div class="category-control-strip"><span><strong>Route</strong> explains why the threshold fired.</span><span><strong>Source status</strong> controls whether a ratio is calculated.</span><span><strong>Evidence</strong> remains the publication authority.</span></div><p class="category-signal-note"><strong>Diagnostic only:</strong> neither a large ratio nor an endpoint-status flag can upgrade severity, rewrite IPEDS, or clear a held institution claim.</p></section>
    <section class="section section-tinted" id="diagnostic-table"><div class="shell"><div class="section-heading"><p class="eyebrow">{summary['comparable_rows']} source-status-comparable medium-priority rows</p><h2>Largest countermovement ratios remain available for audit.</h2><p>The publication column is copied from the separate evidence review for context. R/Z source-status pairs remain visible without turning the arithmetic into a correction or diagnosis.</p></div><details class="evidence-details category-audit-details"><summary>Inspect all {summary['comparable_rows']} comparable medium-priority rows</summary><div class="table-wrap"><table><thead><tr><th>Institution</th><th>Route</th><th>NR change</th><th>NR status</th><th>Total change</th><th>Opposite movement</th><th>Ratio</th><th>Largest opposite category</th><th>Category status</th><th>Publication gate</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div></details></div></section>
    <section class="section shell" id="status-withheld"><div class="section-heading"><p class="eyebrow">{summary['status_noncomparable_rows']} continuing rows withheld by source status</p><h2>Official imputed endpoints stay visible without receiving a composition ratio.</h2><p>These carry-forward-imputed rows still reconcile arithmetically, but an endpoint status outside R/Z means the observed-looking two-year category movement is not used as a countermovement signal.</p></div><div class="table-wrap"><table><thead><tr><th>Institution</th><th>Route</th><th>NR change</th><th>NR status</th><th>Total status</th><th>Status note</th><th>Publication gate</th></tr></thead><tbody>{''.join(status_rows)}</tbody></table></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Control rule</p><h2>Keep the source identity, routing signal, and analyst decision separate.</h2></div><div class="method-grid"><article><h3>Exact source identity</h3><p>Comparable rows must reconcile the nine mutually exclusive IPEDS categories to total enrollment in both endpoint years.</p></article><article><h3>No correction layer</h3><p>The diagnostic never substitutes a reconstructed count for <code>EFNRALT</code> or edits the official series.</p></article><article><h3>No automatic clearance</h3><p>Only the evidence review can support bounded institution-specific discussion; unresolved rows remain held.</p></article><article><h3>Structural boundary</h3><p>The analytic-universe entry is retained for full queue coverage but is not forced into a false two-year composition comparison.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/medium_priority_category_diagnostic.csv">Download diagnostic CSV</a><a class="button button-secondary" href="downloads/medium_priority_category_diagnostic.md">Download diagnostic note</a><a class="button button-secondary" href="medium-qa-review.html">Return to evidence review</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Medium-Priority Category Diagnostic · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
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
        "Medium-priority category diagnostic: "
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
