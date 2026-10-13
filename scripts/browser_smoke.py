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
    )
    for chart_id in chart_ids:
        if page.locator(f"#{chart_id} svg").count() != 1:
            raise AssertionError(f"Chart did not render: {chart_id}")

    dynamics = SITE_DATA["institution_dynamics"]["decade"]
    continuing_text = page.locator("#dynamics-continuing-count").inner_text().strip()
    if continuing_text != expected_int(dynamics["continuing_institutions"]):
        raise AssertionError("Institution dynamics count does not match site data")

    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    if overflow > 1:
        raise AssertionError(f"Page-level horizontal overflow at {width}px: {overflow}px")
    if errors:
        raise AssertionError("Browser errors: " + " | ".join(errors))
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
