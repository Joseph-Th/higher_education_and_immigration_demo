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

    chart_ids = (
        "national-chart",
        "level-chart",
        "state-bars",
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

    update = SITE_DATA["latest_update_review"]
    high_text = page.locator("#update-high-priority").inner_text().strip()
    if high_text != expected_int(update["review_queue"]["high"]):
        raise AssertionError("Latest-release high-priority count does not match site data")
    resolution = SITE_DATA["qa_resolution_summary"]
    if page.locator("#resolution-reviewed").inner_text().strip() != expected_int(resolution["reviewed_count"]):
        raise AssertionError("QA resolution reviewed count does not match site data")
    if page.locator("#resolution-safe").inner_text().strip() != expected_int(resolution["safe_with_context"]):
        raise AssertionError("QA resolution safe count does not match site data")
    if page.locator("#resolution-held").inner_text().strip() != expected_int(resolution["hold_for_confirmation"]):
        raise AssertionError("QA resolution held count does not match site data")
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
    if "41" not in summary or "91" not in summary:
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
    if page.locator(".handoff-card").count() != 11:
        raise AssertionError("Publication handoff does not render the expected 11 claim/control cards")
    if page.locator(".handoff-gates li").count() != 5:
        raise AssertionError("Publication handoff does not show all five publication gates")
    if "Portfolio demonstration" not in page.locator(".handoff-hero .release-note").inner_text():
        raise AssertionError("Publication handoff is missing the portfolio/non-affiliation boundary")
    if page.locator('a[href="downloads/publication_handoff.csv"]').count() != 1:
        raise AssertionError("Publication handoff CSV download is missing")
    if "1,044,137" not in page.locator(".handoff-card").first.inner_text():
        raise AssertionError("Publication handoff headline card does not contain the validated national total")
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
                inspect_research_operations(browser, base_url, width=1280, height=900)
                inspect_research_operations(browser, base_url, width=390, height=844)
                inspect_research_library(browser, base_url, width=1280, height=900)
                inspect_research_library(browser, base_url, width=390, height=844)
                inspect_publication_handoff(browser, base_url, width=1280, height=900)
                inspect_publication_handoff(browser, base_url, width=390, height=844)
                inspect_data_governance(browser, base_url, width=1280, height=900)
                inspect_data_governance(browser, base_url, width=390, height=844)
                inspect_production_cycle(browser, base_url, width=1280, height=900)
                inspect_production_cycle(browser, base_url, width=390, height=844)
                inspect_sql_analysis(browser, base_url, width=1280, height=900)
                inspect_sql_analysis(browser, base_url, width=390, height=844)
                inspect_ad_hoc_analysis(browser, base_url, width=1280, height=900)
                inspect_ad_hoc_analysis(browser, base_url, width=390, height=844)
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
