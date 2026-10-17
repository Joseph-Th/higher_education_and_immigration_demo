"""Browser-level publication smoke test for the generated static research brief.

This lane is deliberately separate from validate_project.py because it requires
Playwright plus an installed Chromium runtime. It never uses the public internet:
the script serves site/ from an ephemeral localhost port and validates the built
artifact that would be deployed.
"""

from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - explicit environment failure path
    raise SystemExit(
        "Playwright is required for browser QA. Install requirements-dev.txt first."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SITE_DATA = json.loads((SITE / "data" / "site_data.json").read_text(encoding="utf-8"))
MEDIUM_QA_SUMMARY = json.loads(
    (ROOT / "data" / "medium_qa_resolution_summary.json").read_text(encoding="utf-8")
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def expected_int(value: int) -> str:
    return f"{value:,}"


def check_downloads(base_url: str) -> None:
    paths = (
        "downloads/national_year.csv",
        "downloads/state_change_summary.csv",
        "downloads/control_year.csv",
        "downloads/institution_change_summary.csv",
        "downloads/latest_release_institution_review.csv",
        "downloads/latest_update_review.md",
        "downloads/qa_resolution_log.csv",
        "downloads/qa_resolution_log.md",
        "downloads/high_priority_category_diagnostic.csv",
        "downloads/high_priority_category_diagnostic.md",
        "downloads/research_memo.md",
        "downloads/research_brief.pdf",
        "downloads/research_library.csv",
        "downloads/research_library.md",
        "downloads/publication_handoff.csv",
        "downloads/publication_handoff.md",
        "downloads/public_release_register.csv",
        "downloads/data_governance.md",
        "downloads/research_agenda.md",
        "downloads/research_agenda.csv",
        "downloads/source_update_triage.csv",
        "downloads/source_update_triage.md",
        "downloads/undocumented_pipeline_comparison.csv",
        "downloads/undocumented_pipeline_context.md",
        "downloads/population_crosswalk.csv",
        "downloads/population_crosswalk.md",
        "downloads/recurring_report_register.csv",
        "downloads/recurring_report_register.md",
        "downloads/production_cycle_register.csv",
        "downloads/production_cycle.md",
        "downloads/production_cycle_log_template.csv",
        "downloads/portfolio_queries.sql",
        "downloads/sql_analysis_audit.csv",
        "downloads/sql_analysis.md",
        "downloads/ad_hoc_analysis_results.csv",
        "downloads/ad_hoc_analysis.md",
        "downloads/state_recovery_analysis.csv",
        "downloads/state_recovery_analysis.md",
        "downloads/undergraduate_shift_baseline.csv",
        "downloads/undergraduate_shift_baseline.md",
        "downloads/private_nonprofit_growth.csv",
        "downloads/private_nonprofit_growth.md",
        "downloads/population_trend_comparison.csv",
        "downloads/population_trend_comparison.md",
        "downloads/planning_scenarios.csv",
        "downloads/planning_scenarios.md",
        "downloads/release_monitor_snapshot.json",
        "downloads/candidate_directory_preflight.json",
        "downloads/candidate_directory_preflight.md",
        "downloads/candidate_directory_change_review.csv",
        "downloads/candidate_directory_change_review.md",
        "downloads/candidate_year_qa_watchlist.csv",
        "downloads/candidate_year_qa_watchlist.md",
        "downloads/medium_priority_review.csv",
        "downloads/medium_priority_review.md",
        "downloads/medium_qa_resolution_log.csv",
        "downloads/medium_qa_resolution_log.md",
        "downloads/medium_priority_category_diagnostic.csv",
        "downloads/medium_priority_category_diagnostic.md",
        "downloads/freshness_monitor.csv",
        "downloads/freshness_monitor.md",
        "downloads/release_readiness.csv",
        "downloads/release_readiness.md",
        "downloads/briefing_note.md",
        "downloads/ipeds_portfolio_analysis.xlsx",
        "downloads/management_briefing_deck.pptx",
        "downloads/state_profile_index.csv",
        "downloads/state_profiles/AZ.md",
        "downloads/benchmark_audit.csv",
    )
    for path in paths:
        with urlopen(f"{base_url}/{path}", timeout=10) as response:
            payload = response.read()
            if response.status != 200 or not payload:
                raise AssertionError(f"Download failed: {path}")


def inspect_viewport(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )

    response = page.goto(base_url, wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Page load failed at {width}px")
    page.wait_for_function(
        "document.querySelector('#metric-total').textContent.trim() !== '—'"
    )

    expected_total = expected_int(SITE_DATA["headline"]["latest_nonresident"])
    if page.locator("#metric-total").inner_text().strip() != expected_total:
        raise AssertionError("Rendered headline total does not match site_data.json")
    update = SITE_DATA["latest_update_review"]
    shift = SITE_DATA["undergraduate_shift_summary"]
    if page.locator("#metric-latest-change").inner_text().strip() != f"+{expected_int(update['national']['absolute_change'])}":
        raise AssertionError("Rendered latest-year change does not match site_data.json")
    if page.locator("#metric-undergrad-change").inner_text().strip() != f"+{expected_int(update['national']['undergraduate_change'])}":
        raise AssertionError("Rendered undergraduate change does not match site_data.json")
    breadth = page.locator("#metric-undergrad-breadth").inner_text().strip()
    if f"{shift['positive_states']} of {shift['geographies']}" not in breadth:
        raise AssertionError("Rendered undergraduate state breadth does not match site_data.json")
    if page.locator("#state-select option").count() != 51:
        raise AssertionError("State explorer does not contain all 50 states plus DC")
    page.locator("#state-select").select_option("CA")
    profile_link = page.locator("#state-profile-link")
    if profile_link.get_attribute("href") != "state.html?state=CA":
        raise AssertionError("State profile link did not follow state selection")
    if "California" not in profile_link.inner_text():
        raise AssertionError("State profile link label did not follow state selection")
    if page.locator("#institution-table tr").count() != 10:
        raise AssertionError("Institution table does not contain the expected 10 rows")
    if page.locator("#benchmark-table tr").count() != 4:
        raise AssertionError("Benchmark table does not contain the expected 4 rows")
    if page.locator("#review-package .review-card").count() != 3:
        raise AssertionError("Homepage reviewer path must contain exactly three primary cards")
    if page.locator("#downloads .download-list a").count() != 6:
        raise AssertionError("Homepage reviewer package must remain limited to six primary artifacts")

    chart_ids = (
        "national-chart",
        "level-chart",
        "state-chart",
        "recovery-chart",
        "control-change-chart",
        "dynamics-chart",
        "update-change-chart",
    )
    for chart_id in chart_ids:
        if page.locator(f"#{chart_id} svg").count() != 1:
            raise AssertionError(f"Chart did not render: {chart_id}")

    dynamics = SITE_DATA["institution_dynamics"]["decade"]
    continuing_text = page.locator("#dynamics-continuing-count").inner_text().strip()
    if continuing_text != expected_int(dynamics["continuing_institutions"]):
        raise AssertionError("Institution dynamics count does not match site data")

    resolution = SITE_DATA["qa_resolution_summary"]
    medium_resolution = SITE_DATA["medium_qa_resolution_summary"]
    if page.locator("#resolution-reviewed").inner_text().strip() != f"{resolution['reviewed_count']}/{resolution['high_priority_total']}":
        raise AssertionError("QA resolution reviewed count does not match site data")
    if page.locator("#resolution-safe").inner_text().strip() != expected_int(resolution["safe_with_context"]):
        raise AssertionError("QA resolution safe count does not match site data")
    if page.locator("#resolution-held").inner_text().strip() != expected_int(resolution["hold_for_confirmation"]):
        raise AssertionError("QA resolution held count does not match site data")
    if page.locator("#medium-resolution-reviewed").inner_text().strip() != f"{medium_resolution['reviewed_count']}/{medium_resolution['medium_priority_total']}":
        raise AssertionError("Medium QA resolution reviewed count does not match site data")
    if page.locator("#medium-resolution-safe").inner_text().strip() != expected_int(medium_resolution["safe_with_context"]):
        raise AssertionError("Medium QA resolution safe count does not match site data")
    if page.locator("#medium-resolution-held").inner_text().strip() != expected_int(medium_resolution["hold_for_confirmation"]):
        raise AssertionError("Medium QA resolution held count does not match site data")
    total_holds = resolution["hold_for_confirmation"] + medium_resolution["hold_for_confirmation"]
    if page.locator("#total-resolution-held").inner_text().strip() != expected_int(total_holds):
        raise AssertionError("Total institution claim hold count does not match site data")
    if page.locator("#qa-case-studies .qa-case-card").count() != 3:
        raise AssertionError("National brief does not render the three analyst case studies")
    rendered_cases = page.locator("#qa-case-studies .qa-case-card h3").all_inner_texts()
    expected_cases = [case["institution"] for case in resolution["case_studies"]]
    if rendered_cases != expected_cases:
        raise AssertionError("National brief analyst case studies do not match site data")

    page.evaluate(
        "document.documentElement.style.scrollBehavior='auto'; "
        "document.querySelector('#downloads').scrollIntoView()"
    )
    anchor_geometry = page.evaluate(
        "({sectionTop: document.querySelector('#downloads').getBoundingClientRect().top, "
        "headerBottom: document.querySelector('.site-header').getBoundingClientRect().bottom})"
    )
    if anchor_geometry["sectionTop"] < anchor_geometry["headerBottom"]:
        raise AssertionError(
            f"Sticky header obscures anchored section at {width}px: "
            f"sectionTop={anchor_geometry['sectionTop']}, headerBottom={anchor_geometry['headerBottom']}"
        )

    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    if overflow > 1:
        raise AssertionError(f"Page-level horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Browser errors: " + " | ".join(errors))
    context.close()


def inspect_medium_priority_category_diagnostic(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/medium-priority-category-diagnostic.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Medium-priority category diagnostic failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("47", "18", "2", "1"):
        if expected not in summary:
            raise AssertionError(f"Medium category diagnostic summary is missing {expected}")
    table = page.locator("#diagnostic-table tbody")
    if table.locator("tr").count() != 47:
        raise AssertionError("Medium category diagnostic does not render all 47 source-status-comparable rows")
    table_text = table.inner_text()
    for expected in (
        "Ana G. Mendez University",
        "Walden University",
        "Chaffey College",
        "University of California-Berkeley",
    ):
        if expected not in table_text:
            raise AssertionError(f"Medium category diagnostic table is missing {expected}")
    if "America Evangelical University" not in table_text or "Z→R" not in table_text:
        raise AssertionError("Medium category diagnostic does not expose category status transitions")
    withheld = page.locator("#status-withheld tbody")
    if withheld.locator("tr").count() != 2:
        raise AssertionError("Medium category diagnostic does not render both source-status-withheld rows")
    withheld_text = withheld.inner_text()
    for expected in (
        "City College-Hollywood",
        "City College-Altamonte Springs",
        "R→P",
        "Imputed using Carry Forward",
    ):
        if expected not in withheld_text:
            raise AssertionError(f"Medium category status-withheld table is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text().lower()
    if "not another risk score or a diagnosis" not in boundary:
        raise AssertionError("Medium category diagnostic is missing its non-diagnostic boundary")
    if page.locator('a[href="downloads/medium_priority_category_diagnostic.csv"]').count() != 2:
        raise AssertionError("Medium category diagnostic CSV links are missing")
    if page.locator('a[href="downloads/medium_priority_category_diagnostic.md"]').count() != 1:
        raise AssertionError("Medium category diagnostic Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Medium category diagnostic horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Medium category diagnostic browser errors: " + " | ".join(errors))
    context.close()


def inspect_private_nonprofit_growth(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/private-nonprofit-growth.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Private nonprofit growth page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("+82,825", "+83,792", "729", "34.5%"):
        if expected not in summary:
            raise AssertionError(f"Private nonprofit growth summary is missing {expected}")
    concentration = page.locator("#concentration").inner_text()
    for expected in ("65.5%", "137,578", "54,753", "Broadly distributed beyond the top 10"):
        if expected not in concentration:
            raise AssertionError(f"Private nonprofit concentration section is missing {expected}")
    if page.locator("#concentration .nonprofit-concentration-row").count() != 4:
        raise AssertionError("Private nonprofit concentration visual does not render all four checkpoints")
    if page.locator("#leading-contributors .nonprofit-contributor-row").count() != 10:
        raise AssertionError("Private nonprofit contributor visual does not render the top 10")
    page.locator("#leading-contributors details.nonprofit-audit-details").evaluate("el => el.open = true")
    table = page.locator("#leading-contributors tbody")
    if table.locator("tr").count() != 10:
        raise AssertionError("Private nonprofit page does not render the ten leading contributors")
    first = table.locator("tr").first.inner_text()
    if "Trine University-Regional/Non-Traditional Campuses" not in first or "+9,167" not in first or "Safe with context" not in first:
        raise AssertionError("Private nonprofit leading-contributor row does not match validated output")
    table_text = table.inner_text()
    if "University of the Cumberlands" not in table_text or "Safe with context" not in table_text:
        raise AssertionError("Private nonprofit ranking does not preserve the Cumberlands QA clearance")
    if "Not high-priority in latest release queue" not in table_text:
        raise AssertionError("Private nonprofit ranking does not preserve non-high-priority QA context")
    if "Entered endpoint sector universe" not in table_text:
        raise AssertionError("Private nonprofit ranking does not disclose endpoint-sector entry")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "at least 50% of gross positive movement" not in boundary:
        raise AssertionError("Private nonprofit page is missing its concentration decision rule")
    if page.locator('a[href="downloads/private_nonprofit_growth.csv"]').count() != 2:
        raise AssertionError("Private nonprofit CSV links are missing")
    if page.locator('a[href="downloads/private_nonprofit_growth.md"]').count() != 1:
        raise AssertionError("Private nonprofit Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Private nonprofit horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Private nonprofit browser errors: " + " | ".join(errors))
    context.close()


def inspect_qa_review(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/qa-review.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"QA review page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    resolution = SITE_DATA["qa_resolution_summary"]
    for expected in (
        "27/27",
        str(resolution["safe_with_context"]),
        str(resolution["hold_for_confirmation"]),
        "100%",
    ):
        if expected not in summary:
            raise AssertionError(f"QA review summary is missing {expected}")
    table = page.locator(".section-tinted tbody")
    if table.locator("tr").count() != 27:
        raise AssertionError("QA review page does not render all 27 high-priority records")
    table_text = table.inner_text()
    for expected in ("Webster University", "Reformed University", "Safe with context", "Hold for confirmation"):
        if expected not in table_text:
            raise AssertionError(f"QA review table is missing {expected}")
    if table.locator('a[target="_blank"]').count() != 27:
        raise AssertionError("QA review table does not expose evidence for every high-priority record")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "request for review, not an error label" not in boundary:
        raise AssertionError("QA review page is missing its flag interpretation boundary")
    if page.locator('a[href="downloads/qa_resolution_log.csv"]').count() != 2:
        raise AssertionError("QA review CSV links are missing")
    if page.locator('a[href="downloads/qa_resolution_log.md"]').count() != 1:
        raise AssertionError("QA review Markdown link is missing")
    if page.locator('a[href="high-priority-category-diagnostic.html"]').count() != 1:
        raise AssertionError("QA review category-diagnostic link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"QA review horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("QA review browser errors: " + " | ".join(errors))
    context.close()


def inspect_high_priority_category_diagnostic(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/high-priority-category-diagnostic.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"High-priority category diagnostic failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("25", "8", "3", "2"):
        if expected not in summary:
            raise AssertionError(f"Category diagnostic summary is missing {expected}")
    table = page.locator("#diagnostic-table tbody")
    if table.locator("tr").count() != 25:
        raise AssertionError("Category diagnostic does not render all 25 comparable continuing rows")
    table_text = table.inner_text()
    for expected in (
        "Polk State College",
        "Anderson University",
        "University of the Cumberlands",
        "Community College of Rhode Island",
    ):
        if expected not in table_text:
            raise AssertionError(f"Category diagnostic table is missing {expected}")
    if "Oakwood University" not in table_text or "R→Z" not in table_text:
        raise AssertionError("Category diagnostic does not expose Oakwood's R→Z source-status transition")
    boundary = page.locator(".handoff-hero .release-note").inner_text().lower()
    if "not proof of miscoding or reclassification" not in boundary:
        raise AssertionError("Category diagnostic is missing its non-diagnostic interpretation boundary")
    if page.locator('a[href="downloads/high_priority_category_diagnostic.csv"]').count() != 2:
        raise AssertionError("Category diagnostic CSV links are missing")
    if page.locator('a[href="downloads/high_priority_category_diagnostic.md"]').count() != 1:
        raise AssertionError("Category diagnostic Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Category diagnostic horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Category diagnostic browser errors: " + " | ".join(errors))
    context.close()


def inspect_state_recovery(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/state-recovery.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"State recovery page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("33", "18", "27", "+71,079"):
        if expected not in summary:
            raise AssertionError(f"State recovery summary is missing {expected}")
    if page.locator("#largest-movements .recovery-movement-row").count() != 16:
        raise AssertionError("State recovery visual does not render eight gains and eight shortfalls")
    visual_text = page.locator("#largest-movements .recovery-movement-grid").inner_text()
    for expected in ("IL", "+14,464", "CA", "-33,282", "Graduate", "Public"):
        if expected not in visual_text:
            raise AssertionError(f"State recovery visual is missing {expected}")
    page.locator("#largest-movements details.recovery-audit-details").evaluate("el => el.open = true")
    tables = page.locator("#largest-movements tbody")
    if tables.count() != 2 or tables.nth(0).locator("tr").count() != 8 or tables.nth(1).locator("tr").count() != 8:
        raise AssertionError("State recovery page does not render both eight-state comparison tables")
    if "+14,464" not in tables.nth(0).locator("tr").first.inner_text() or "Illinois" not in tables.nth(0).locator("tr").first.inner_text():
        raise AssertionError("State recovery gain table does not begin with the validated Illinois result")
    if "-33,282" not in tables.nth(1).locator("tr").first.inner_text() or "California" not in tables.nth(1).locator("tr").first.inner_text():
        raise AssertionError("State recovery shortfall table does not begin with the validated California result")
    headers = [text.strip().lower() for text in page.locator("#largest-movements th").all_inner_texts()]
    if "control driver" not in headers:
        raise AssertionError("State recovery tables do not expose the institutional-control decomposition")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "accounting, not causal attribution" not in boundary or "not automatically a campus opening or closure" not in boundary:
        raise AssertionError("State recovery page is missing its interpretation boundary")
    if page.locator('a[href="downloads/state_recovery_analysis.csv"]').count() != 2:
        raise AssertionError("State recovery CSV links are missing")
    if page.locator('a[href="downloads/state_recovery_analysis.md"]').count() != 1:
        raise AssertionError("State recovery Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"State recovery horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("State recovery browser errors: " + " | ".join(errors))
    context.close()


def inspect_undergraduate_shift(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/undergraduate-shift.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Undergraduate shift page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("+31,592", "45/51", "3", "20.6%"):
        if expected not in summary:
            raise AssertionError(f"Undergraduate shift summary is missing {expected}")
    if page.locator("#annual-context .shift-history-row").count() != 9:
        raise AssertionError("Undergraduate shift annual visual does not contain all nine intervals")
    if page.locator("#annual-context .shift-history-row.latest").count() != 1:
        raise AssertionError("Undergraduate shift annual visual does not identify the latest baseline interval")
    if page.locator("#annual-context tbody tr").count() != 9:
        raise AssertionError("Undergraduate shift annual context does not contain all nine intervals")
    if page.locator("#state-breadth .shift-state-bar-row").count() != 12:
        raise AssertionError("Undergraduate shift state visual does not contain six gains and six declines")
    breadth_text = page.locator("#state-breadth .shift-breadth-summary").inner_text()
    if "45 increased" not in breadth_text or "6 declined" not in breadth_text:
        raise AssertionError("Undergraduate shift state breadth visual does not show the 45/6 split")
    page.locator("#state-breadth details.shift-audit-details").evaluate("el => el.open = true")
    tables = page.locator("#state-breadth tbody")
    if tables.count() != 2 or tables.nth(0).locator("tr").count() != 10 or tables.nth(1).locator("tr").count() != 6:
        raise AssertionError("Undergraduate shift state tables do not contain 10 gains and 6 declines")
    first_gain = tables.nth(0).locator("tr").first.inner_text()
    if "Florida" not in first_gain or "+6,418" not in first_gain:
        raise AssertionError("Undergraduate shift gain table does not begin with the validated Florida result")
    first_decline = tables.nth(1).locator("tr").first.inner_text()
    if "California" not in first_decline or "-1,490" not in first_decline:
        raise AssertionError("Undergraduate shift decline table does not begin with the validated California result")
    body_text = page.locator("main").inner_text()
    for expected in ("Public +28,580", "entry/exit nets to -340", "largest positive annual undergraduate movement"):
        if expected not in body_text:
            raise AssertionError(f"Undergraduate shift page is missing validated context {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "does not establish persistence or causation" not in boundary or "R01 remains open" not in boundary:
        raise AssertionError("Undergraduate shift page is missing its persistence boundary")
    if page.locator('a[href="downloads/undergraduate_shift_baseline.csv"]').count() != 2:
        raise AssertionError("Undergraduate shift CSV links are missing")
    if page.locator('a[href="downloads/undergraduate_shift_baseline.md"]').count() != 1:
        raise AssertionError("Undergraduate shift Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Undergraduate shift horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Undergraduate shift browser errors: " + " | ".join(errors))
    context.close()


def inspect_data_governance(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/data-governance.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Data governance page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    if "74" not in summary or "124" not in summary:
        raise AssertionError("Data governance summary does not show the registered/expanded release counts")
    if page.locator(".handoff-gates li").count() != 5:
        raise AssertionError("Data governance page does not show all five release controls")
    if "Any future restricted partner data would remain nonpublic by default" not in page.locator(".handoff-hero .release-note").inner_text():
        raise AssertionError("Data governance page is missing the restricted-data boundary")
    if page.locator('a[href="downloads/public_release_register.csv"]').count() != 1:
        raise AssertionError("Public release register download link is missing")
    if page.locator('a[href="downloads/data_governance.md"]').count() != 1:
        raise AssertionError("Data governance note download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Data governance horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Data governance browser errors: " + " | ".join(errors))
    context.close()


def inspect_release_readiness(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/release-readiness.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Release readiness page failed at {width}px")
    if page.locator('[data-readiness-gate]').count() != 8:
        raise AssertionError("Release readiness does not render all eight gates")
    hero = page.locator(".handoff-hero")
    if hero.get_attribute("data-current-decision") != "READY_WITH_CLAIM_LEVEL_HOLDS":
        raise AssertionError("Release readiness current-publication machine decision is incorrect")
    if hero.get_attribute("data-year-decision") != "HOLD_YEAR_ADVANCE":
        raise AssertionError("Release readiness year-advance machine decision is incorrect")
    summary = page.locator(".handoff-summary").inner_text()
    held_claims = (
        SITE_DATA["qa_resolution_summary"]["hold_for_confirmation"]
        + MEDIUM_QA_SUMMARY["hold_for_confirmation"]
    )
    for expected in (
        "READY WITH CLAIM-LEVEL HOLDS",
        "HOLD YEAR ADVANCE",
        str(held_claims),
        "2/4",
    ):
        if expected not in summary:
            raise AssertionError(f"Release readiness summary is missing {expected}")
    gate_text = page.locator("#readiness-gates").inner_text()
    for expected in ("A01", "A07", "Y01", "27/27", "50/50", "74 artifact families", "17/17", "preflight=PASS", "3,864", "154 institution change-review rows", "226 carry-forward QA rows", "5 medium-priority/directory overlaps"):
        if expected not in gate_text:
            raise AssertionError(f"Release readiness gate matrix is missing {expected}")
    if page.locator('a[href="downloads/release_readiness.csv"]').count() != 2:
        raise AssertionError("Release readiness CSV links are missing")
    if page.locator('a[href="downloads/release_readiness.md"]').count() != 1:
        raise AssertionError("Release readiness Markdown link is missing")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "not the Presidents' Alliance's internal approval process" not in boundary:
        raise AssertionError("Release readiness page is missing its portfolio/non-affiliation boundary")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Release readiness horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Release readiness browser errors: " + " | ".join(errors))
    context.close()


def inspect_planning_scenarios(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/planning-scenarios.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Planning scenarios page failed at {width}px")
    if page.locator('[data-scenario-id]').count() != 3:
        raise AssertionError("Planning scenarios page does not render all three forward cases")
    summary = page.locator(".handoff-summary").inner_text()
    for expected in ("-4.0%", "1,058,964", "1,074,536", "1,086,816"):
        if expected not in summary:
            raise AssertionError(f"Planning scenario summary is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "not a predictive model" not in boundary or "unavailable 2025 IPEDS actual" not in boundary:
        raise AssertionError("Planning scenarios page is missing its non-predictive boundary")
    if page.locator('a[href="downloads/planning_scenarios.csv"]').count() != 2:
        raise AssertionError("Planning scenario CSV links are missing")
    if page.locator('a[href="downloads/planning_scenarios.md"]').count() != 1:
        raise AssertionError("Planning scenario Markdown link is missing")
    if "-44,060" not in page.locator("#backtest").inner_text():
        raise AssertionError("Planning scenario backtest variance is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Planning scenarios horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Planning scenarios browser errors: " + " | ".join(errors))
    context.close()


def inspect_freshness_monitor(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/freshness-monitor.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Freshness monitor page failed at {width}px")
    if page.locator('[data-monitor-id]').count() != 4:
        raise AssertionError("Freshness monitor does not render all four candidate-year assets")
    if page.locator('[data-product-monitor]').count() != 3:
        raise AssertionError("Freshness monitor does not render all three recurring-product triggers")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("2/4", "HOLD YEAR ADVANCE", "PASS", "3"):
        if expected not in summary:
            raise AssertionError(f"Freshness monitor summary is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "not continuously live" not in boundary or "deadlines are not inferred" not in boundary:
        raise AssertionError("Freshness monitor is missing its dated/non-inferred boundary")
    release_text = page.locator("#release-readiness").inner_text()
    if "does not advance the project year" not in release_text or "Fall 2024" not in release_text:
        raise AssertionError("Freshness monitor is missing the current incomplete-package gate")
    preflight_text = page.locator("#directory-preflight").inner_text()
    for expected in ("6/6", "70/70", "3,864", "3,812", "-4", "154", "612", "226", "5 medium-priority", "72 → 70", "DFRCGID", "DFRCUSCG"):
        if expected not in preflight_text:
            raise AssertionError(f"Freshness monitor directory preflight is missing {expected}")
    if page.locator('a[href="candidate-directory-preflight.html"]').count() < 1:
        raise AssertionError("Freshness monitor candidate directory preflight link is missing")
    if page.locator('a[href="candidate-year-watchlist.html"]').count() != 1:
        raise AssertionError("Freshness monitor candidate-year QA watchlist link is missing")
    if page.locator('a[href="downloads/release_monitor_snapshot.json"]').count() != 1:
        raise AssertionError("Release-monitor snapshot download link is missing")
    if page.locator('a[href="downloads/freshness_monitor.csv"]').count() != 2:
        raise AssertionError("Freshness monitor CSV links are missing")
    if page.locator('a[href="downloads/freshness_monitor.md"]').count() != 1:
        raise AssertionError("Freshness monitor Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Freshness monitor horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Freshness monitor browser errors: " + " | ".join(errors))
    context.close()


def inspect_candidate_directory_preflight(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/candidate-directory-preflight.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Candidate directory preflight page failed at {width}px")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("PASS", "6/6", "3,864", "-4"):
        if expected not in summary:
            raise AssertionError(f"Candidate directory preflight summary is missing {expected}")
    continuity = page.locator("#continuity").inner_text()
    for expected in ("3,812", "52", "56", "6"):
        if expected not in continuity:
            raise AssertionError(f"Candidate directory continuity is missing {expected}")
    body = page.locator("main").inner_text()
    for expected in ("70/70", "154", "612", "72 → 70", "DFRCGID", "DFRCUSCG", "EF2025A.zip", "No 2025 enrollment claims yet"):
        if expected not in body:
            raise AssertionError(f"Candidate directory preflight body is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "HOLD_YEAR_ADVANCE" not in boundary or "never substitutes" not in boundary:
        raise AssertionError("Candidate directory preflight is missing its year-advance boundary")
    if page.locator('a[href="downloads/candidate_directory_preflight.json"]').count() != 2:
        raise AssertionError("Candidate directory preflight JSON links are missing")
    if page.locator('a[href="downloads/candidate_directory_preflight.md"]').count() != 1:
        raise AssertionError("Candidate directory preflight Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Candidate directory preflight horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Candidate directory preflight browser errors: " + " | ".join(errors))
    context.close()


def inspect_candidate_directory_changes(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/candidate-directory-changes.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Candidate directory change review page failed at {width}px")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("154", "52 / 56", "612", "1,069"):
        if expected not in summary:
            raise AssertionError(f"Candidate directory change review summary is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    for expected in ("do not infer institutional opening/closure", "2025 enrollment movement", "HOLD_YEAR_ADVANCE"):
        if expected not in boundary:
            raise AssertionError(f"Candidate directory change review boundary is missing {expected}")
    frame_text = page.locator("#frame-turnover").inner_text()
    for expected in ("New directory record", "35", "Title IV / First Look status became ineligible", "38", "Directory record absent", "15"):
        if expected not in frame_text:
            raise AssertionError(f"Candidate directory frame-turnover section is missing {expected}")
    leaver_text = page.locator("#leaver-exposure").inner_text()
    for expected in ("FIDM-Fashion Institute of Design & Merchandising", "128", "17,593", "not projected 2025 losses"):
        if expected not in leaver_text:
            raise AssertionError(f"Candidate directory leaver section is missing {expected}")
    if page.locator("#leaver-exposure tbody tr").count() != 10:
        raise AssertionError("Candidate directory leaver table does not show ten priority rows")
    control_text = page.locator("#control-changes").inner_text()
    for expected in ("Grand Canyon University", "967", "Private for-profit", "Private nonprofit", "The University of Arizona Global Campus", "Public"):
        if expected not in control_text:
            raise AssertionError(f"Candidate directory control section is missing {expected}")
    if page.locator("#control-changes tbody tr").count() != 6:
        raise AssertionError("Candidate directory control table does not contain six shared control changes")
    state_text = page.locator("#state-changes").inner_text()
    for expected in ("The University of Arizona Global Campus", "CA", "AZ", "Simon's Rock at Bard College", "MA", "NY", "West Coast University-Texas"):
        if expected not in state_text:
            raise AssertionError(f"Candidate directory state section is missing {expected}")
    if page.locator("#state-changes tbody tr").count() != 3:
        raise AssertionError("Candidate directory state table does not contain three shared state changes")
    name_text = page.locator("#name-continuity").inner_text()
    for expected in ("Houston Community College", "Houston City College", "4,670", "10,184"):
        if expected not in name_text:
            raise AssertionError(f"Candidate directory name section is missing {expected}")
    if page.locator('a[href="downloads/candidate_directory_change_review.csv"]').count() != 2:
        raise AssertionError("Candidate directory change-review CSV links are missing")
    if page.locator('a[href="downloads/candidate_directory_change_review.md"]').count() != 1:
        raise AssertionError("Candidate directory change-review Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Candidate directory change review horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Candidate directory change review browser errors: " + " | ".join(errors))
    context.close()


def inspect_candidate_year_watchlist(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/candidate-year-watchlist.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Candidate-year QA watchlist page failed at {width}px")

    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("226", "27", "5", "154"):
        if expected not in summary:
            raise AssertionError(f"Candidate-year QA watchlist summary is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    for expected in (
        "do not infer 2025 enrollment movement",
        "institutional opening/closure",
        "continued publication eligibility",
        "full 2025 Fall Enrollment package",
    ):
        if expected not in boundary:
            raise AssertionError(f"Candidate-year QA watchlist boundary is missing {expected}")

    main_text = page.locator("main").inner_text()
    for expected in ("27 current high-priority rows + 50 current medium-priority rows + 154 candidate directory changes - 5 overlaps = 226", "No current high-priority record overlaps", "41 safe with context / 9 held"):
        if expected not in main_text:
            raise AssertionError(f"Candidate-year QA watchlist union is missing {expected}")

    overlap = page.locator("#overlap")
    if overlap.locator("tbody tr").count() != 5:
        raise AssertionError("Candidate-year QA watchlist overlap table does not contain five rows")
    overlap_text = overlap.inner_text()
    for expected in (
        "2,443",
        "Lindsey Wilson College",
        "FIDM-Fashion Institute of Design & Merchandising",
        "Humphreys University-Stockton and Modesto Campuses",
        "City College-Hollywood",
        "City College-Altamonte Springs",
    ):
        if expected not in overlap_text:
            raise AssertionError(f"Candidate-year QA overlap section is missing {expected}")

    high = page.locator("#current-high")
    if high.locator("tbody tr").count() != 10:
        raise AssertionError("Candidate-year QA watchlist current-high table does not contain ten rows")
    high_text = high.inner_text()
    for expected in ("University of the Cumberlands", "+4,616", "Hold for confirmation", "Trine University-Regional/Non-Traditional Campuses", "Safe with context"):
        if expected not in high_text:
            raise AssertionError(f"Candidate-year QA current-high section is missing {expected}")

    candidate_only = page.locator("#candidate-only")
    if candidate_only.locator("tbody tr").count() != 10:
        raise AssertionError("Candidate-year QA watchlist candidate-only table does not contain ten rows")
    candidate_text = candidate_only.inner_text()
    for expected in ("9,326", "Houston Community College", "Houston City College", "4,670", "Grand Canyon University", "967"):
        if expected not in candidate_text:
            raise AssertionError(f"Candidate-year QA candidate-only section is missing {expected}")

    if page.locator('a[href="downloads/candidate_year_qa_watchlist.csv"]').count() != 2:
        raise AssertionError("Candidate-year QA watchlist CSV links are missing")
    if page.locator('a[href="downloads/candidate_year_qa_watchlist.md"]').count() != 1:
        raise AssertionError("Candidate-year QA watchlist Markdown link is missing")
    if "Carry forward the question, not the answer." not in main_text:
        raise AssertionError("Candidate-year QA watchlist revalidation rule is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Candidate-year QA watchlist horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Candidate-year QA watchlist browser errors: " + " | ".join(errors))
    context.close()


def inspect_medium_priority_review(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/medium-priority-review.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Medium-priority QA review page failed at {width}px")

    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("50", "28", "3", "5"):
        if expected not in summary:
            raise AssertionError(f"Medium-priority QA summary is missing {expected}")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    for expected in ("triage signal", "not a source correction", "publication clearance", "evidence review"):
        if expected not in boundary:
            raise AssertionError(f"Medium-priority QA boundary is missing {expected}")

    routes = page.locator("#routes").inner_text()
    for expected in ("Structural / reporting", "3 rows", "Absolute + percentage", "8 rows", "Absolute movement", "11 rows", "Percentage movement", "28 rows", "none is a severity grade"):
        if expected not in routes:
            raise AssertionError(f"Medium-priority QA route section is missing {expected}")

    body = page.locator("main").inner_text()
    for expected in ("25 gain rows", "+7,806", "23 decline rows", "-9,241", "17,047", "-1,435", "flagged subset only"):
        if expected not in body:
            raise AssertionError(f"Medium-priority QA accounting is missing {expected}")

    largest = page.locator("#largest-movements")
    if largest.locator("tbody tr").count() != 10:
        raise AssertionError("Medium-priority QA largest-movement table does not contain ten rows")
    largest_text = largest.inner_text()
    for expected in ("Indiana Wesleyan University-National & Global", "+855", "The University of Texas at Arlington", "-846", "Chaffey College", "-611"):
        if expected not in largest_text:
            raise AssertionError(f"Medium-priority QA largest-movement section is missing {expected}")

    structural = page.locator("#structural-reporting")
    if structural.locator("tbody tr").count() != 3:
        raise AssertionError("Medium-priority QA structural/reporting table does not contain three rows")
    structural_text = structural.inner_text()
    for expected in ("New Orleans Baptist Theological Seminary", "Entered analytic universe", "City College-Hollywood", "R → P", "City College-Altamonte Springs"):
        if expected not in structural_text:
            raise AssertionError(f"Medium-priority QA structural section is missing {expected}")

    overlap = page.locator("#candidate-overlap")
    if overlap.locator("tbody tr").count() != 5:
        raise AssertionError("Medium-priority QA candidate-overlap table does not contain five rows")
    overlap_text = overlap.inner_text()
    for expected in ("2,443", "Lindsey Wilson College", "FIDM-Fashion Institute of Design & Merchandising", "Humphreys University-Stockton and Modesto Campuses", "City College-Hollywood", "City College-Altamonte Springs"):
        if expected not in overlap_text:
            raise AssertionError(f"Medium-priority QA candidate-overlap section is missing {expected}")

    if page.locator('a[href="downloads/medium_priority_review.csv"]').count() != 1:
        raise AssertionError("Medium-priority QA CSV links are missing")
    if page.locator('a[href="downloads/medium_priority_review.md"]').count() != 1:
        raise AssertionError("Medium-priority QA Markdown link is missing")
    if page.locator('a[href="medium-qa-review.html"]').count() < 1:
        raise AssertionError("Medium-priority QA routing page does not link to the evidence review")
    if "No automatic clearance" not in body or "No new risk score" not in body:
        raise AssertionError("Medium-priority QA operating rules are missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Medium-priority QA horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Medium-priority QA browser errors: " + " | ".join(errors))
    context.close()


def inspect_medium_qa_review(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/medium-qa-review.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Medium-priority evidence review page failed at {width}px")

    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("50/50", "41", "9", "100%"):
        if expected not in summary:
            raise AssertionError(f"Medium-priority evidence summary is missing {expected}")
    table = page.locator("#complete-queue tbody")
    if table.locator("tr").count() != 50:
        raise AssertionError("Medium-priority evidence page does not render all 50 reviewed records")
    table_text = table.inner_text()
    for expected in (
        "Texas State University",
        "Georgia Institute of Technology-Main Campus",
        "University of California-Berkeley",
        "Indiana University-Indianapolis",
        "Weber State University",
        "University of New Haven",
        "Safe with context",
        "Hold for confirmation",
    ):
        if expected not in table_text:
            raise AssertionError(f"Medium-priority evidence table is missing {expected}")
    if table.locator('a[target="_blank"]').count() != 50:
        raise AssertionError("Medium-priority evidence table does not expose one source per reviewed record")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "without rewriting IPEDS" not in boundary or "revalidated" not in boundary:
        raise AssertionError("Medium-priority evidence page is missing its publication/revalidation boundary")
    if page.locator('a[href="downloads/medium_qa_resolution_log.csv"]').count() != 2:
        raise AssertionError("Medium-priority evidence CSV links are missing")
    if page.locator('a[href="downloads/medium_qa_resolution_log.md"]').count() != 1:
        raise AssertionError("Medium-priority evidence Markdown link is missing")
    if "not standing approval for a future release" not in page.locator("main").inner_text():
        raise AssertionError("Medium-priority evidence page is missing its no-standing-approval rule")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Medium-priority evidence horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Medium-priority evidence browser errors: " + " | ".join(errors))
    context.close()


def inspect_ad_hoc_analysis(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/ad-hoc-analysis.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Ad hoc analysis page failed at {width}px")
    if page.locator('[data-case-id]').count() != 3:
        raise AssertionError("Ad hoc analysis page does not render all three case cards")
    summary = page.locator(".handoff-summary").inner_text()
    if "3" not in summary or "3/3" not in summary:
        raise AssertionError("Ad hoc analysis summary does not show case/check counts")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "not real client requests" not in boundary or "employment-history claims" not in boundary:
        raise AssertionError("Ad hoc analysis page is missing its simulation boundary")
    if page.locator('a[href="downloads/ad_hoc_analysis_results.csv"]').count() != 2:
        raise AssertionError("Ad hoc result CSV links are missing")
    if page.locator('a[href="downloads/ad_hoc_analysis.md"]').count() != 1:
        raise AssertionError("Ad hoc casebook Markdown link is missing")
    if "86.5%" not in page.locator('[data-case-id="A01"]').inner_text():
        raise AssertionError("A01 concentration result is missing")
    if "+29,539" not in page.locator('[data-case-id="A02"]').inner_text():
        raise AssertionError("A02 national reconciliation is missing")
    if "+63,400" not in page.locator('[data-case-id="A03"]').inner_text():
        raise AssertionError("A03 control reconciliation is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Ad hoc analysis horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Ad hoc analysis browser errors: " + " | ".join(errors))
    context.close()


def inspect_production_cycle(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/production-cycle.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Production cycle page failed at {width}px")
    summary = page.locator(".handoff-summary").inner_text()
    if "7" not in summary or "3" not in summary or "0" not in summary:
        raise AssertionError("Production cycle summary does not show stages/products/deadline boundary")
    if page.locator("#cycle-register .handoff-card").count() != 7:
        raise AssertionError("Production cycle page does not render all seven stage controls")
    if page.locator(".operations-grid .operations-card").count() != 3:
        raise AssertionError("Production cycle page does not render all three recurring products")
    if "does not represent the Presidents' Alliance's internal project-management system" not in page.locator(".handoff-hero .release-note").inner_text():
        raise AssertionError("Production cycle page is missing the portfolio/non-affiliation boundary")
    if page.locator('a[href="downloads/production_cycle_register.csv"]').count() != 1:
        raise AssertionError("Production cycle register download link is missing")
    if page.locator('a[href="downloads/production_cycle.md"]').count() != 1:
        raise AssertionError("Production cycle notes download link is missing")
    if page.locator('a[href="downloads/production_cycle_log_template.csv"]').count() != 1:
        raise AssertionError("Production cycle log template download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Production cycle horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Production cycle browser errors: " + " | ".join(errors))
    context.close()


def inspect_sql_analysis(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )
    response = page.goto(f"{base_url}/sql-analysis.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"SQL analysis page failed at {width}px")
    if page.locator('[data-query-id]').count() != 6:
        raise AssertionError("SQL analysis page does not render all six query cards")
    summary = page.locator(".handoff-summary").inner_text()
    if "6" not in summary or "6/6" not in summary or "5" not in summary:
        raise AssertionError("SQL analysis summary does not show query/check/source-table counts")
    if page.locator('a[href="downloads/portfolio_queries.sql"]').count() != 1:
        raise AssertionError("SQL query-pack download link is missing")
    if page.locator('a[href="downloads/sql_analysis_audit.csv"]').count() != 1:
        raise AssertionError("SQL audit download link is missing")
    if page.locator("tbody tr").count() != 6:
        raise AssertionError("SQL analysis audit table does not contain six rows")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"SQL analysis horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("SQL analysis browser errors: " + " | ".join(errors))
    context.close()


def inspect_research_memo(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/research-memo.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Research memo load failed at {width}px")
    if page.locator("#memo-total").inner_text().strip() != expected_int(SITE_DATA["headline"]["latest_nonresident"]):
        raise AssertionError("Research memo headline total does not match site data")
    change_values = page.locator(".memo-change-row strong").all_inner_texts()
    latest = SITE_DATA["latest_update_review"]["national"]
    expected_changes = [
        f"+{expected_int(latest['undergraduate_change'])}",
        f"-{expected_int(abs(latest['graduate_change']))}",
        f"+{expected_int(latest['absolute_change'])}",
    ]
    if change_values != expected_changes:
        raise AssertionError("Research memo latest-year visual does not match site data")
    if page.locator("#memo-case-studies .qa-case-card").count() != 3:
        raise AssertionError("Research memo does not show three analyst case studies")
    expected_cases = [case["institution"] for case in SITE_DATA["qa_resolution_summary"]["case_studies"]]
    rendered_cases = page.locator("#memo-case-studies .qa-case-card h3").all_inner_texts()
    if rendered_cases != expected_cases:
        raise AssertionError("Research memo case studies do not match site data")
    if page.locator('a[href="downloads/research_memo.md"]').count() != 1:
        raise AssertionError("Research memo download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Research memo horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Research memo browser errors: " + " | ".join(errors))
    context.close()


def inspect_population_crosswalk(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/methodology-crosswalk.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Population crosswalk load failed at {width}px")
    if page.locator(".crosswalk-card").count() != 6:
        raise AssertionError("Population crosswalk does not show six source definitions")
    labels = page.locator(".crosswalk-card h2").all_inner_texts()
    required = {
        "IPEDS U.S. nonresident",
        "Immigrant-origin students",
        "International students",
        "Undocumented students in higher education",
        "Undocumented high school graduates",
        "Refugee/asylee students",
    }
    if set(labels) != required:
        raise AssertionError("Population crosswalk labels do not match the structured source")
    if page.locator('a[href="downloads/population_crosswalk.csv"]').count() != 1:
        raise AssertionError("Population crosswalk CSV download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Population crosswalk horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Population crosswalk browser errors: " + " | ".join(errors))
    context.close()


def inspect_population_trends(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/population-trends.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Population trend comparison failed at {width}px")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("+7.3%", "+107%", "+2.9%", "3"):
        if expected not in summary:
            raise AssertionError(f"Population trend summary is missing {expected}")
    same_year = page.locator("#same-year").inner_text()
    for expected in ("1,014,598", "5,991,000", "510,000", "NOT ADDABLE"):
        if expected not in same_year:
            raise AssertionError(f"Population trend same-year section is missing {expected}")
    if "no 2021–2023 undocumented trend is calculated" not in page.locator("main").inner_text():
        raise AssertionError("Population trend page is missing its undocumented-vintage break")
    if page.locator("table tbody tr").count() != 6:
        raise AssertionError("Population trend page does not show the six-year IPEDS context")
    if page.locator('a[href="downloads/population_trend_comparison.csv"]').count() != 2:
        raise AssertionError("Population trend CSV links are missing")
    if page.locator('a[href="downloads/population_trend_comparison.md"]').count() != 1:
        raise AssertionError("Population trend Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Population trend horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Population trend browser errors: " + " | ".join(errors))
    context.close()


def inspect_source_update_triage(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/source-update-triage.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Source update triage failed at {width}px")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("17", "8", "3", "6", "0 inferred deadlines"):
        if expected not in summary:
            raise AssertionError(f"Source update triage summary is missing {expected}")
    if page.locator('[data-source-route]').count() != 17:
        raise AssertionError("Source update triage does not cover all 17 Research Library sources")
    if page.locator("#routing-rules .handoff-gates li").count() != 5:
        raise AssertionError("Source update triage does not show the five decision gates")
    boundary = page.locator(".handoff-hero .release-note").inner_text()
    if "not the Presidents' Alliance's internal refresh schedule" not in boundary:
        raise AssertionError("Source update triage is missing its portfolio/non-affiliation boundary")
    if page.locator('a[href="downloads/source_update_triage.csv"]').count() != 2:
        raise AssertionError("Source update triage CSV links are missing")
    if page.locator('a[href="downloads/source_update_triage.md"]').count() != 1:
        raise AssertionError("Source update triage Markdown link is missing")
    if "Routine refresh" not in page.locator("main").inner_text():
        raise AssertionError("Source update triage is missing the routine-refresh route")
    if "Methodology review" not in page.locator("main").inner_text():
        raise AssertionError("Source update triage is missing the methodology-review route")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Source update triage horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Source update triage browser errors: " + " | ".join(errors))
    context.close()


def inspect_undocumented_pipeline(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/undocumented-pipeline.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Undocumented pipeline context failed at {width}px")
    summary = page.locator(".handoff-hero .handoff-summary").inner_text()
    for expected in ("70.7%", "70.4%", "10", "NOT A RATE"):
        if expected not in summary:
            raise AssertionError(f"Undocumented pipeline summary is missing {expected}")
    if page.locator("#state-comparison tbody tr").count() != 10:
        raise AssertionError("Undocumented pipeline table does not contain ten state rows")
    if page.locator(".handoff-gates li").count() != 5:
        raise AssertionError("Undocumented pipeline page does not show all five interpretation gates")
    main_text = page.locator("main").inner_text()
    for expected in ("53,000", "358,836", "35,000", "257,125", "11,675", "27,672"):
        if expected not in main_text:
            raise AssertionError(f"Undocumented pipeline page is missing {expected}")
    if "college-going" not in main_text or "transition" not in main_text or "No causal policy test" not in main_text:
        raise AssertionError("Undocumented pipeline page is missing its non-rate/non-causal boundary")
    if page.locator('a[href="downloads/undocumented_pipeline_comparison.csv"]').count() != 2:
        raise AssertionError("Undocumented pipeline CSV links are missing")
    if page.locator('a[href="downloads/undocumented_pipeline_context.md"]').count() != 1:
        raise AssertionError("Undocumented pipeline Markdown link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Undocumented pipeline horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Undocumented pipeline browser errors: " + " | ".join(errors))
    context.close()


def inspect_research_operations(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/research-operations.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Research operations page failed at {width}px")
    if page.locator(".operations-card").count() != 3:
        raise AssertionError("Research operations page does not show all three recurring products")
    if page.locator(".lifecycle-grid li").count() != 7:
        raise AssertionError("Research operations lifecycle does not contain seven controls")
    if "Portfolio demonstration" not in page.locator(".operations-hero .release-note").inner_text():
        raise AssertionError("Research operations page is missing its portfolio/non-affiliation boundary")
    if page.locator('a[href="downloads/recurring_report_register.csv"]').count() != 1:
        raise AssertionError("Recurring-report CSV download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Research operations horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Research operations browser errors: " + " | ".join(errors))
    context.close()


def inspect_research_library(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/research-library.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Research Library page failed at {width}px")
    total = page.locator(".library-card").count()
    if total < 10:
        raise AssertionError(f"Research Library unexpectedly small: {total} resource cards")
    if page.locator("#library-result-count").inner_text().strip() != f"{total} of {total} resources":
        raise AssertionError("Research Library initial result count is incorrect")
    page.locator("#library-search").fill("Digest")
    visible_after_search = page.locator(".library-card:not([hidden])").count()
    if visible_after_search < 1:
        raise AssertionError("Research Library search returned no Digest-related resources")
    digest_titles = page.locator(".library-card:not([hidden]) h2").all_inner_texts()
    if not any("Digest of Education Statistics" in title for title in digest_titles):
        raise AssertionError("Research Library search did not include the Digest benchmark")
    page.locator("#library-reset").click()
    if page.locator(".library-card:not([hidden])").count() != total:
        raise AssertionError("Research Library reset did not restore all resources")
    page.locator("#library-type-filter").select_option(label="Methodology")
    methodology_count = page.locator(".library-card:not([hidden])").count()
    if methodology_count <= 0 or methodology_count >= total:
        raise AssertionError("Research Library type filter did not narrow results")
    page.locator("#library-reset").click()
    page.locator("#library-population-filter").select_option(label="Undocumented")
    population_count = page.locator(".library-card:not([hidden])").count()
    if population_count < 3 or population_count >= total:
        raise AssertionError("Research Library population filter did not return a plausible subset")
    visible_population_tags = page.locator(".library-card:not([hidden]) .library-population-tags").all_inner_texts()
    if not all("Undocumented" in text or "All populations" in text for text in visible_population_tags):
        raise AssertionError("Research Library population filter returned a mismatched card")
    if page.locator('a[href="downloads/research_library.csv"]').count() != 1:
        raise AssertionError("Research Library CSV download link is missing")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Research Library horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Research Library browser errors: " + " | ".join(errors))
    context.close()


def inspect_publication_handoff(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/publication-handoff.html", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"Publication handoff page failed at {width}px")
    if page.locator(".handoff-card").count() != 17:
        raise AssertionError("Publication handoff does not render the expected 17 claim/control cards")
    if page.locator(".handoff-gates li").count() != 5:
        raise AssertionError("Publication handoff does not show all five publication gates")
    if "Portfolio demonstration" not in page.locator(".handoff-hero .release-note").inner_text():
        raise AssertionError("Publication handoff is missing the portfolio/non-affiliation boundary")
    if page.locator('a[href="downloads/publication_handoff.csv"]').count() != 1:
        raise AssertionError("Publication handoff CSV download is missing")
    if "1,044,137" not in page.locator(".handoff-card").first.inner_text():
        raise AssertionError("Publication handoff headline card does not contain the validated national total")
    handoff_text = page.locator("#handoff-register").inner_text()
    for expected in ("N06", "Q02", "Q03", "M02", "P01", "G01", "+31,592", "45 of 51 states/DC", "226 unique UNITIDs", "five medium/directory overlaps", "no high/directory overlap", "All 50 current medium-priority institution flags", "28 percentage-movement", "41 are safe with context", "9 remain held for confirmation", "standing approval", "70.7%", "70.4%", "not addable", "zero inferred internal deadlines"):
        if expected not in handoff_text:
            raise AssertionError(f"Publication handoff is missing expanded control {expected}")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Publication handoff horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Publication handoff browser errors: " + " | ".join(errors))
    context.close()


def inspect_state_profile(browser, base_url: str, *, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
    page.on("console", lambda message: errors.append(f"console: {message.text}") if message.type == "error" else None)
    response = page.goto(f"{base_url}/state.html?state=CA", wait_until="networkidle")
    if response is None or not response.ok:
        raise AssertionError(f"State profile load failed at {width}px")
    page.wait_for_function("document.querySelector('#profile-total').textContent.trim() !== '—'")
    if "California" not in page.locator("#state-profile-title").inner_text():
        raise AssertionError("State profile did not honor query parameter")
    if page.locator("#profile-institution-table tr").count() != 5:
        raise AssertionError("State profile does not show five institution rows")
    if page.locator("#profile-series-table tr").count() != 10:
        raise AssertionError("State profile does not show ten annual rows")
    if page.locator("#profile-trend-chart svg").count() != 1:
        raise AssertionError("State profile trend chart did not render")
    if not page.locator("#state-markdown-link").get_attribute("href").endswith("/CA.md"):
        raise AssertionError("State profile Markdown link is incorrect")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if overflow > 1:
        raise AssertionError(f"State profile horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("State profile browser errors: " + " | ".join(errors))
    context.close()


def main() -> int:
    handler = partial(QuietHandler, directory=str(SITE))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        check_downloads(base_url)
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True)
            except PlaywrightError as exc:
                raise SystemExit(
                    "Chromium is not installed for Playwright. Run: "
                    "python -m playwright install chromium"
                ) from exc
            try:
                inspect_viewport(browser, base_url, width=1280, height=900)
                inspect_viewport(browser, base_url, width=390, height=844)
                inspect_state_profile(browser, base_url, width=1280, height=900)
                inspect_state_profile(browser, base_url, width=390, height=844)
                inspect_research_memo(browser, base_url, width=1280, height=900)
                inspect_research_memo(browser, base_url, width=390, height=844)
                inspect_population_crosswalk(browser, base_url, width=1280, height=900)
                inspect_population_crosswalk(browser, base_url, width=390, height=844)
                inspect_population_trends(browser, base_url, width=1280, height=900)
                inspect_population_trends(browser, base_url, width=390, height=844)
                inspect_undocumented_pipeline(browser, base_url, width=1280, height=900)
                inspect_undocumented_pipeline(browser, base_url, width=390, height=844)
                inspect_source_update_triage(browser, base_url, width=1280, height=900)
                inspect_source_update_triage(browser, base_url, width=390, height=844)
                inspect_research_operations(browser, base_url, width=1280, height=900)
                inspect_research_operations(browser, base_url, width=390, height=844)
                inspect_research_library(browser, base_url, width=1280, height=900)
                inspect_research_library(browser, base_url, width=390, height=844)
                inspect_publication_handoff(browser, base_url, width=1280, height=900)
                inspect_publication_handoff(browser, base_url, width=390, height=844)
                inspect_release_readiness(browser, base_url, width=1280, height=900)
                inspect_release_readiness(browser, base_url, width=390, height=844)
                inspect_data_governance(browser, base_url, width=1280, height=900)
                inspect_data_governance(browser, base_url, width=390, height=844)
                inspect_production_cycle(browser, base_url, width=1280, height=900)
                inspect_production_cycle(browser, base_url, width=390, height=844)
                inspect_sql_analysis(browser, base_url, width=1280, height=900)
                inspect_sql_analysis(browser, base_url, width=390, height=844)
                inspect_ad_hoc_analysis(browser, base_url, width=1280, height=900)
                inspect_ad_hoc_analysis(browser, base_url, width=390, height=844)
                inspect_state_recovery(browser, base_url, width=1280, height=900)
                inspect_state_recovery(browser, base_url, width=390, height=844)
                inspect_undergraduate_shift(browser, base_url, width=1280, height=900)
                inspect_undergraduate_shift(browser, base_url, width=390, height=844)
                inspect_private_nonprofit_growth(browser, base_url, width=1280, height=900)
                inspect_private_nonprofit_growth(browser, base_url, width=390, height=844)
                inspect_qa_review(browser, base_url, width=1280, height=900)
                inspect_qa_review(browser, base_url, width=390, height=844)
                inspect_high_priority_category_diagnostic(browser, base_url, width=1280, height=900)
                inspect_high_priority_category_diagnostic(browser, base_url, width=390, height=844)
                inspect_planning_scenarios(browser, base_url, width=1280, height=900)
                inspect_planning_scenarios(browser, base_url, width=390, height=844)
                inspect_freshness_monitor(browser, base_url, width=1280, height=900)
                inspect_freshness_monitor(browser, base_url, width=390, height=844)
                inspect_candidate_directory_preflight(browser, base_url, width=1280, height=900)
                inspect_candidate_directory_preflight(browser, base_url, width=390, height=844)
                inspect_candidate_directory_changes(browser, base_url, width=1280, height=900)
                inspect_candidate_directory_changes(browser, base_url, width=390, height=844)
                inspect_candidate_year_watchlist(browser, base_url, width=1280, height=900)
                inspect_candidate_year_watchlist(browser, base_url, width=390, height=844)
                inspect_medium_priority_review(browser, base_url, width=1280, height=900)
                inspect_medium_priority_review(browser, base_url, width=390, height=844)
                inspect_medium_qa_review(browser, base_url, width=1280, height=900)
                inspect_medium_qa_review(browser, base_url, width=390, height=844)
                inspect_medium_priority_category_diagnostic(browser, base_url, width=1280, height=900)
                inspect_medium_priority_category_diagnostic(browser, base_url, width=390, height=844)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print("Browser smoke PASS: desktop + mobile rendering, interaction, downloads, and console.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
