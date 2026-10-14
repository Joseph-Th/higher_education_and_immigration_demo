"""Build a small portfolio casebook for ad hoc analyst requests.

The cases are explicitly simulated management questions. They demonstrate how a
bounded request is clarified, answered from validated outputs, reconciled, and
returned concisely without inventing a requester, SLA, or employment history.
"""

from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
CSV_OUTPUT = DATA / "ad_hoc_analysis_results.csv"
DOC_OUTPUT = ROOT / "docs" / "AD_HOC_ANALYSIS.md"
HTML_OUTPUT = ROOT / "site" / "ad-hoc-analysis.html"

FIELDS = (
    "case_id",
    "business_question",
    "decision_use",
    "primary_answer",
    "response_detail",
    "source_authority",
    "qa_check",
    "status",
)


@dataclass(frozen=True)
class Case:
    case_id: str
    business_question: str
    decision_use: str
    primary_answer: str
    response_detail: str
    source_authority: str
    qa_check: str
    status: str = "PASS"

    def as_row(self) -> dict[str, str]:
        return {field: str(getattr(self, field)) for field in FIELDS}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def signed(value: int) -> str:
    return f"{value:+,}"


def build_cases() -> list[Case]:
    national = read_csv(PROCESSED / "national_year.csv")
    states = read_csv(PROCESSED / "state_year.csv")
    state_change = read_csv(PROCESSED / "state_change_summary.csv")
    controls = read_csv(PROCESSED / "control_year.csv")

    national_by_year = {int(row["year"]): int(row["nonresident_enrollment"]) for row in national}

    # A01: incomplete recovery relative to 2019.
    below = [row for row in state_change if row["recovery_status"] == "Below 2019"]
    shortfalls = sorted(below, key=lambda row: int(row["change_2019_2024"]))
    total_shortfall = sum(int(row["change_2019_2024"]) for row in below)
    top_five_shortfalls = shortfalls[:5]
    top_five_shortfall_total = sum(int(row["change_2019_2024"]) for row in top_five_shortfalls)
    top_five_shortfall_share = round(
        abs(top_five_shortfall_total) / abs(total_shortfall) * 100, 1
    )
    if len(below) != 18:
        raise RuntimeError(f"A01 expected 18 below-baseline geographies, observed {len(below)}")
    if total_shortfall >= 0 or top_five_shortfall_total >= 0:
        raise RuntimeError("A01 shortfall accounting must remain negative")
    a01_detail = ", ".join(
        f"{row['state']} {signed(int(row['change_2019_2024']))}" for row in top_five_shortfalls
    )

    # A02: latest-year state gains, calculated directly from state-year authority.
    state_by_year = {
        (int(row["year"]), row["state"]): int(row["nonresident_enrollment"])
        for row in states
    }
    latest_year = max(int(row["year"]) for row in states)
    prior_year = latest_year - 1
    geographies = sorted(row["state"] for row in states if int(row["year"]) == latest_year)
    latest_changes = [
        (state, state_by_year[(latest_year, state)] - state_by_year[(prior_year, state)])
        for state in geographies
    ]
    latest_changes.sort(key=lambda item: (-item[1], item[0]))
    top_five_gains = latest_changes[:5]
    top_five_gain_total = sum(value for _, value in top_five_gains)
    national_latest_change = national_by_year[latest_year] - national_by_year[prior_year]
    state_latest_change = sum(value for _, value in latest_changes)
    if state_latest_change != national_latest_change:
        raise RuntimeError(
            f"A02 state/national change mismatch: {state_latest_change} != {national_latest_change}"
        )
    top_five_gain_share = round(top_five_gain_total / national_latest_change * 100, 1)
    a02_detail = ", ".join(f"{state} {signed(value)}" for state, value in top_five_gains)

    # A03: decade change by institutional control, independently reconciled to national totals.
    control_by_year = {
        (int(row["year"]), row["control"]): int(row["nonresident_enrollment"])
        for row in controls
    }
    start_year = min(int(row["year"]) for row in controls)
    control_names = sorted({row["control"] for row in controls})
    control_changes = {
        control: control_by_year[(latest_year, control)] - control_by_year[(start_year, control)]
        for control in control_names
    }
    control_change_total = sum(control_changes.values())
    national_decade_change = national_by_year[latest_year] - national_by_year[start_year]
    if control_change_total != national_decade_change:
        raise RuntimeError(
            f"A03 control/national change mismatch: {control_change_total} != {national_decade_change}"
        )
    driver = max(control_changes.items(), key=lambda item: item[1])
    offsets = sorted(
        ((control, value) for control, value in control_changes.items() if control != driver[0]),
        key=lambda item: item[0],
    )

    cases = [
        Case(
            case_id="A01",
            business_question=(
                "Which states/DC are still below their 2019 U.S. nonresident enrollment, "
                "and how concentrated is the remaining shortfall?"
            ),
            decision_use="Prioritize where a follow-up geography review would start.",
            primary_answer=f"{len(below)} states/DC remain below 2019.",
            response_detail=(
                f"Combined shortfall is {signed(total_shortfall)} students. The five largest "
                f"shortfalls ({a01_detail}) account for {top_five_shortfall_share:.1f}% of it."
            ),
            source_authority="data/processed/state_change_summary.csv",
            qa_check=(
                f"Below-baseline rows={len(below)}; shortfall sum={signed(total_shortfall)}; "
                f"top-five share={top_five_shortfall_share:.1f}%"
            ),
        ),
        Case(
            case_id="A02",
            business_question=(
                f"Which states contributed most to the {prior_year}-{latest_year} national increase?"
            ),
            decision_use="Identify the geographies driving the newest annual movement.",
            primary_answer=(
                f"The five largest state gains contributed {signed(top_five_gain_total)} students, "
                f"or {top_five_gain_share:.1f}% of the {signed(national_latest_change)} national gain."
            ),
            response_detail=f"Largest gains: {a02_detail}.",
            source_authority="data/processed/state_year.csv; data/processed/national_year.csv",
            qa_check=(
                f"All 51 state/DC changes sum to the national change: "
                f"{signed(state_latest_change)} = {signed(national_latest_change)}"
            ),
        ),
        Case(
            case_id="A03",
            business_question=(
                f"Which institutional-control sector explains the {start_year}-{latest_year} net increase?"
            ),
            decision_use="Give management a concise structural explanation for the decade result.",
            primary_answer=f"{driver[0]} institutions increased by {driver[1]:,} students.",
            response_detail=(
                f"That gain was partly offset by {offsets[0][0]} {signed(offsets[0][1])} and "
                f"{offsets[1][0]} {signed(offsets[1][1])}, reconciling to the national "
                f"{signed(national_decade_change)} change."
            ),
            source_authority="data/processed/control_year.csv; data/processed/national_year.csv",
            qa_check=(
                f"Control-sector changes sum to national decade change: "
                f"{signed(control_change_total)} = {signed(national_decade_change)}"
            ),
        ),
    ]
    if [case.case_id for case in cases] != ["A01", "A02", "A03"]:
        raise RuntimeError("Ad hoc case IDs/order changed unexpectedly")
    return cases


def write_csv(cases: list[Case]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(case.as_row() for case in cases)


def write_markdown(cases: list[Case]) -> None:
    lines = [
        "# Ad Hoc Analysis Casebook", "",
        "This is an explicit **portfolio simulation** of three bounded analyst requests. The questions are constructed to demonstrate request clarification, source selection, calculation, QA, and concise response. They are not client requests, organizational SLAs, or claims of employment history.", "",
        "## Working pattern", "",
        "1. Clarify the business question, population, geography, and vintage.",
        "2. Select the smallest validated authority needed to answer it.",
        "3. Calculate only the metrics needed for the decision question.",
        "4. Reconcile the result to an independent total or accounting identity where possible.",
        "5. Return a short answer with the interpretation boundary still visible.", "",
    ]
    for case in cases:
        lines.extend([
            f"## {case.case_id}: {case.business_question}", "",
            f"**Decision use:** {case.decision_use}", "",
            f"**Answer:** {case.primary_answer}", "",
            case.response_detail, "",
            f"**Source authority:** `{case.source_authority}`", "",
            f"**QA:** {case.qa_check} (**{case.status}**)", "",
        ])
    lines.extend([
        "## Reproduction", "",
        "```bash", "python scripts/build_ad_hoc_analysis.py", "```", "",
        "The generated CSV is a compact reviewer/audit surface. The underlying processed CSVs remain the analytical authorities.", "",
    ])
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(cases: list[Case]) -> None:
    cards = []
    for case in cases:
        cards.append(f"""
          <article class="handoff-card" data-case-id="{html.escape(case.case_id)}">
            <div class="handoff-card-head"><span>{html.escape(case.case_id)}</span><span class="handoff-status handoff-status-ready">{html.escape(case.status)}</span></div>
            <p class="case-kicker">Simulated ad hoc request</p>
            <h2>{html.escape(case.business_question)}</h2>
            <dl class="handoff-meta">
              <div><dt>Decision use</dt><dd>{html.escape(case.decision_use)}</dd></div>
              <div><dt>Answer</dt><dd><strong>{html.escape(case.primary_answer)}</strong> {html.escape(case.response_detail)}</dd></div>
              <div><dt>Authority</dt><dd><code>{html.escape(case.source_authority)}</code></dd></div>
              <div><dt>QA</dt><dd>{html.escape(case.qa_check)}</dd></div>
            </dl>
          </article>""")

    HTML_OUTPUT.write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Three simulated ad hoc analyst requests answered and reconciled from validated IPEDS outputs.">
  <meta name="theme-color" content="#10263c">
  <title>Ad Hoc Analysis | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to ad hoc cases</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a>
      <nav aria-label="Ad hoc analysis navigation"><a href="index.html">Brief</a><a href="sql-analysis.html">SQL</a><a href="research-memo.html">Memo</a><a href="data-governance.html">Governance</a></nav>
    </div>
  </header>
  <main id="main">
    <section class="handoff-hero">
      <div class="shell">
        <p class="eyebrow">Ad hoc analyst cases</p>
        <h1>Answer the small management question, then show the check.</h1>
        <p class="lede">Three bounded request scenarios demonstrate a practical analyst workflow: clarify the question, choose the authority, calculate the minimum useful answer, reconcile it, and deliver a concise response.</p>
        <div class="hero-actions"><a class="button button-primary" href="#casebook">Review cases</a><a class="button button-secondary" href="downloads/ad_hoc_analysis_results.csv">Download case results</a></div>
        <p class="release-note"><strong>Portfolio boundary:</strong> these are constructed request scenarios, not real client requests, organizational SLAs, or employment-history claims.</p>
        <div class="handoff-summary">
          <article><strong>{len(cases)}</strong><span>simulated requests</span></article>
          <article><strong>{sum(case.status == 'PASS' for case in cases)}/{len(cases)}</strong><span>QA checks passed</span></article>
          <article><strong>0</strong><span>invented requesters</span></article>
          <article><strong>0</strong><span>invented deadlines</span></article>
        </div>
      </div>
    </section>
    <section class="section section-tinted" id="casebook">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">Casebook</p><h2>Request → calculation → QA → response</h2><p>Each answer stays small enough to review quickly while retaining a visible source and reconciliation trail.</p></div>
        <div class="handoff-grid">{''.join(cards)}</div>
      </div>
    </section>
    <section class="section shell">
      <div class="section-heading compact"><p class="eyebrow">Working pattern</p><h2>A repeatable path for one-off analysis</h2></div>
      <div class="method-grid">
        <article><h3>1. Clarify</h3><p>Confirm the population, geography, comparison period, and decision question before calculating.</p></article>
        <article><h3>2. Select authority</h3><p>Use the smallest validated table that directly answers the request instead of rebuilding the entire project.</p></article>
        <article><h3>3. Reconcile</h3><p>Check state sums, control-sector sums, or concentration arithmetic against an independent total.</p></article>
        <article><h3>4. Deliver</h3><p>Return the answer first, then the small amount of evidence needed for the reader to trust and reuse it correctly.</p></article>
      </div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/ad_hoc_analysis_results.csv">Download result CSV</a><a class="button button-secondary" href="downloads/ad_hoc_analysis.md">Download casebook notes</a></div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Ad Hoc Analysis · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""", encoding="utf-8")


def main() -> int:
    cases = build_cases()
    write_csv(cases)
    write_markdown(cases)
    write_html(cases)
    print(f"Ad hoc analysis: {len(cases)} simulated cases; {sum(case.status == 'PASS' for case in cases)}/{len(cases)} checks PASS")
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
