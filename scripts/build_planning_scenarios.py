"""Build a small planning-scenario and variance-analysis portfolio artifact.

This is not a predictive model. It demonstrates a common analyst workflow:
construct a transparent planning baseline from historical data, backtest it
against a known actual, and present several data-derived forward scenarios.
"""

from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIONAL_PATH = ROOT / "data" / "processed" / "national_year.csv"
CSV_OUTPUT = ROOT / "data" / "planning_scenarios.csv"
DOC_OUTPUT = ROOT / "docs" / "PLANNING_SCENARIOS.md"
HTML_OUTPUT = ROOT / "site" / "planning-scenarios.html"

FIELDS = (
    "case_id",
    "case_type",
    "case_label",
    "basis_period",
    "method",
    "annual_rate_pct",
    "base_year",
    "base_value",
    "target_year",
    "planned_value",
    "actual_value",
    "variance",
    "variance_pct",
    "decision_use",
    "status",
)


@dataclass(frozen=True)
class Scenario:
    case_id: str
    case_type: str
    case_label: str
    basis_period: str
    method: str
    annual_rate_pct: float
    base_year: int
    base_value: int
    target_year: int
    planned_value: int
    actual_value: int | None
    variance: int | None
    variance_pct: float | None
    decision_use: str
    status: str = "PASS"

    def as_row(self) -> dict[str, str]:
        return {
            "case_id": self.case_id,
            "case_type": self.case_type,
            "case_label": self.case_label,
            "basis_period": self.basis_period,
            "method": self.method,
            "annual_rate_pct": f"{self.annual_rate_pct:.2f}",
            "base_year": str(self.base_year),
            "base_value": str(self.base_value),
            "target_year": str(self.target_year),
            "planned_value": str(self.planned_value),
            "actual_value": "" if self.actual_value is None else str(self.actual_value),
            "variance": "" if self.variance is None else str(self.variance),
            "variance_pct": "" if self.variance_pct is None else f"{self.variance_pct:.2f}",
            "decision_use": self.decision_use,
            "status": self.status,
        }


def load_national() -> dict[int, int]:
    with NATIONAL_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    values = {int(row["year"]): int(row["nonresident_enrollment"]) for row in rows}
    if sorted(values) != list(range(2015, 2025)):
        raise RuntimeError("Planning scenarios require the complete 2015-2024 national series")
    return values


def cagr(values: dict[int, int], start: int, end: int) -> float:
    if end <= start:
        raise ValueError("CAGR end year must be after start year")
    return (values[end] / values[start]) ** (1 / (end - start)) - 1


def build_scenarios() -> list[Scenario]:
    values = load_national()

    # Backtest: what a simple end-of-2023 baseline based on the 2021-2023 CAGR
    # would have implied for 2024. This demonstrates forecast-vs-actual variance.
    backtest_rate = cagr(values, 2021, 2023)
    backtest_plan = round(values[2023] * (1 + backtest_rate))
    backtest_actual = values[2024]
    backtest_variance = backtest_actual - backtest_plan
    backtest_variance_pct = backtest_variance / backtest_plan * 100

    # Forward planning cases are transparent scenario anchors, not predictions.
    low_rate = cagr(values, 2019, 2024)
    base_rate = values[2024] / values[2023] - 1
    high_rate = cagr(values, 2022, 2024)

    scenarios = [
        Scenario(
            case_id="BT01",
            case_type="BACKTEST",
            case_label="2024 planning-baseline backtest",
            basis_period="2021-2023",
            method="Apply the 2021-2023 CAGR to the 2023 actual",
            annual_rate_pct=backtest_rate * 100,
            base_year=2023,
            base_value=values[2023],
            target_year=2024,
            planned_value=backtest_plan,
            actual_value=backtest_actual,
            variance=backtest_variance,
            variance_pct=backtest_variance_pct,
            decision_use="Show how a simple historical-growth baseline can miss the realized result and why variance review matters.",
        ),
        Scenario(
            case_id="PS01",
            case_type="PLANNING_SCENARIO",
            case_label="Long-run recovery pace",
            basis_period="2019-2024",
            method="Apply the 2019-2024 CAGR to the 2024 actual",
            annual_rate_pct=low_rate * 100,
            base_year=2024,
            base_value=values[2024],
            target_year=2025,
            planned_value=round(values[2024] * (1 + low_rate)),
            actual_value=None,
            variance=None,
            variance_pct=None,
            decision_use="Lower planning case anchored to the full post-2019 recovery period.",
        ),
        Scenario(
            case_id="PS02",
            case_type="PLANNING_SCENARIO",
            case_label="Latest-year pace",
            basis_period="2023-2024",
            method="Apply the latest observed year-over-year growth rate to the 2024 actual",
            annual_rate_pct=base_rate * 100,
            base_year=2024,
            base_value=values[2024],
            target_year=2025,
            planned_value=round(values[2024] * (1 + base_rate)),
            actual_value=None,
            variance=None,
            variance_pct=None,
            decision_use="Middle planning case anchored to the newest annual movement.",
        ),
        Scenario(
            case_id="PS03",
            case_type="PLANNING_SCENARIO",
            case_label="Recent two-year recovery pace",
            basis_period="2022-2024",
            method="Apply the 2022-2024 CAGR to the 2024 actual",
            annual_rate_pct=high_rate * 100,
            base_year=2024,
            base_value=values[2024],
            target_year=2025,
            planned_value=round(values[2024] * (1 + high_rate)),
            actual_value=None,
            variance=None,
            variance_pct=None,
            decision_use="Upper planning case anchored to the recent recovery window.",
        ),
    ]

    if [row.case_id for row in scenarios] != ["BT01", "PS01", "PS02", "PS03"]:
        raise RuntimeError("Planning scenario IDs/order changed unexpectedly")
    if not (scenarios[1].planned_value < scenarios[2].planned_value < scenarios[3].planned_value):
        raise RuntimeError("Planning scenario ordering is not low < middle < high")
    if scenarios[0].variance != values[2024] - scenarios[0].planned_value:
        raise RuntimeError("Backtest variance does not reconcile")
    return scenarios


def write_csv(scenarios: list[Scenario]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(row.as_row() for row in scenarios)


def signed(value: int) -> str:
    return f"{value:+,}"


def write_markdown(scenarios: list[Scenario]) -> None:
    backtest = scenarios[0]
    forward = scenarios[1:]
    low, middle, high = forward
    range_width = high.planned_value - low.planned_value
    lines = [
        "# Planning Scenarios and Variance Review",
        "",
        "This is a **portfolio planning exercise, not a predictive forecast**. It demonstrates how an analyst can create a transparent baseline, compare a known actual with that baseline, and present multiple forward planning cases without claiming statistical certainty.",
        "",
        "## Backtest: forecast vs. actual",
        "",
        f"Using the 2021-2023 CAGR ({backtest.annual_rate_pct:.2f}%) as a simple end-of-2023 planning baseline would have implied **{backtest.planned_value:,}** U.S. nonresident students in 2024. The observed 2024 total was **{backtest.actual_value:,}**, a variance of **{signed(backtest.variance or 0)}** ({backtest.variance_pct:.2f}%).",
        "",
        "The point is not that this baseline should have been used. The point is that even a transparent growth-rate assumption can materially miss the actual result, so reporting should show both the assumption and the variance.",
        "",
        "## 2025 planning cases",
        "",
        "| Case | Historical basis | Annual rate | 2025 planning value |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in forward:
        lines.append(
            f"| {row.case_label} | {row.basis_period} | {row.annual_rate_pct:.2f}% | {row.planned_value:,} |"
        )
    lines.extend([
        "",
        f"The data-derived range is **{low.planned_value:,} to {high.planned_value:,}**, a spread of **{range_width:,}** students. The latest-year pace produces the middle case of **{middle.planned_value:,}**.",
        "",
        "These are scenario anchors for planning discussion. No 2025 actual is available in this project, and the cases do not incorporate policy, visa, institution-specific, economic, or other causal drivers.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/build_planning_scenarios.py",
        "```",
        "",
        "The canonical historical authority remains `data/processed/national_year.csv`. The scenario CSV is a downstream analytical support artifact.",
        "",
    ])
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(scenarios: list[Scenario]) -> None:
    backtest = scenarios[0]
    forward = scenarios[1:]
    low, middle, high = forward
    range_width = high.planned_value - low.planned_value
    cards = []
    for row in forward:
        cards.append(f"""
          <article class="handoff-card" data-scenario-id="{html.escape(row.case_id)}">
            <div class="handoff-card-head"><span>{html.escape(row.case_id)}</span><span class="handoff-status handoff-status-ready">SCENARIO</span></div>
            <p class="case-kicker">{html.escape(row.basis_period)} basis</p>
            <h2>{html.escape(row.case_label)}</h2>
            <div class="scenario-value">{row.planned_value:,}</div>
            <dl class="handoff-meta">
              <div><dt>Annual rate</dt><dd>{row.annual_rate_pct:.2f}%</dd></div>
              <div><dt>Method</dt><dd>{html.escape(row.method)}</dd></div>
              <div><dt>Decision use</dt><dd>{html.escape(row.decision_use)}</dd></div>
            </dl>
          </article>""")

    HTML_OUTPUT.write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Transparent planning scenarios and a forecast-vs-actual backtest built from validated IPEDS national enrollment data.">
  <meta name="theme-color" content="#10263c">
  <title>Planning Scenarios | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to planning scenarios</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a>
      <nav aria-label="Planning scenario navigation"><a href="index.html">Brief</a><a href="ad-hoc-analysis.html">Ad hoc</a><a href="sql-analysis.html">SQL</a><a href="data-governance.html">Governance</a></nav>
    </div>
  </header>
  <main id="main">
    <section class="handoff-hero">
      <div class="shell">
        <p class="eyebrow">Planning and variance support</p>
        <h1>Use historical growth as a planning assumption, not a promise.</h1>
        <p class="lede">A backtest shows how a simple historical-growth baseline can miss the realized result. Three forward cases then give management a transparent range for planning discussion.</p>
        <div class="hero-actions"><a class="button button-primary" href="#backtest">Review variance</a><a class="button button-secondary" href="downloads/planning_scenarios.csv">Download scenario table</a></div>
        <p class="release-note"><strong>Boundary:</strong> this is a portfolio planning exercise, not a predictive model or a claim about the unavailable 2025 IPEDS actual.</p>
        <div class="handoff-summary">
          <article><strong>{backtest.variance_pct:.1f}%</strong><span>2024 variance vs. backtest baseline</span></article>
          <article><strong>{low.planned_value:,}</strong><span>2025 lower planning case</span></article>
          <article><strong>{middle.planned_value:,}</strong><span>2025 middle planning case</span></article>
          <article><strong>{high.planned_value:,}</strong><span>2025 upper planning case</span></article>
        </div>
      </div>
    </section>
    <section class="section shell" id="backtest">
      <div class="section-heading"><p class="eyebrow">Backtest</p><h2>Forecast vs. actual makes the assumption error visible.</h2><p>A 2021-2023 CAGR baseline would have overshot the observed 2024 total.</p></div>
      <div class="method-grid">
        <article><h3>Planning baseline</h3><p><strong>{backtest.planned_value:,}</strong><br>{backtest.annual_rate_pct:.2f}% 2021-2023 CAGR applied to the 2023 actual.</p></article>
        <article><h3>2024 actual</h3><p><strong>{backtest.actual_value:,}</strong><br>Validated national authority.</p></article>
        <article><h3>Variance</h3><p><strong>{signed(backtest.variance or 0)}</strong><br>{backtest.variance_pct:.2f}% versus the planning baseline.</p></article>
        <article><h3>Management use</h3><p>Show the assumption beside the realized result and investigate why actual growth differed before carrying a baseline forward.</p></article>
      </div>
    </section>
    <section class="section section-tinted" id="scenarios">
      <div class="shell">
        <div class="section-heading"><p class="eyebrow">2025 planning cases</p><h2>Three transparent historical anchors, one bounded range.</h2><p>The range is {low.planned_value:,} to {high.planned_value:,}, a spread of {range_width:,} students. These cases are inputs to planning discussion, not predictions.</p></div>
        <div class="handoff-grid">{''.join(cards)}</div>
      </div>
    </section>
    <section class="section shell">
      <div class="section-heading compact"><p class="eyebrow">Use correctly</p><h2>What this does and does not establish</h2></div>
      <div class="method-grid">
        <article><h3>Does</h3><p>Demonstrates baseline construction, forecast-vs-actual variance, sensitivity ranges, and concise management framing.</p></article>
        <article><h3>Does not</h3><p>Estimate causal effects or incorporate policy, visa, economic, institution-specific, or macroeconomic drivers.</p></article>
        <article><h3>Authority</h3><p><code>data/processed/national_year.csv</code> remains the historical analytical authority.</p></article>
        <article><h3>Next actual</h3><p>When a future release arrives, replace scenario-only discussion with an actual-versus-plan variance review.</p></article>
      </div>
      <div class="memo-actions"><a class="button button-primary" href="downloads/planning_scenarios.csv">Download scenario CSV</a><a class="button button-secondary" href="downloads/planning_scenarios.md">Download scenario notes</a></div>
    </section>
  </main>
  <footer><div class="shell footer-inner"><span>Planning Scenarios · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""", encoding="utf-8")


def main() -> int:
    scenarios = build_scenarios()
    write_csv(scenarios)
    write_markdown(scenarios)
    write_html(scenarios)
    print(
        "Planning scenarios: "
        f"backtest variance={scenarios[0].variance:+,} ({scenarios[0].variance_pct:.2f}%); "
        f"2025 range={scenarios[1].planned_value:,}-{scenarios[3].planned_value:,}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
