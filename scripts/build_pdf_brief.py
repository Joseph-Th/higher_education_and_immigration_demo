"""Render the validated research memo as a reviewer-ready PDF publication."""

from __future__ import annotations

import shutil
import hashlib
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - explicit environment failure path
    raise SystemExit(
        "Playwright is required to build the PDF brief. Install requirements-dev.txt first."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DELIVERABLE = ROOT / "deliverables" / "research_brief.pdf"
PUBLIC_COPY = SITE / "downloads" / "research_brief.pdf"
MANIFEST = ROOT / "deliverables" / "research_brief_manifest.json"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    memo = SITE / "research-memo.html"
    if not memo.exists():
        raise SystemExit("site/research-memo.html is missing; run validate_project.py first")

    DELIVERABLE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_COPY.parent.mkdir(parents=True, exist_ok=True)

    handler = partial(QuietHandler, directory=str(SITE))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                response = page.goto(f"{base_url}/research-memo.html", wait_until="networkidle")
                if response is None or not response.ok:
                    raise RuntimeError("Research memo did not load for PDF rendering")
                page.emulate_media(media="print")
                page.pdf(
                    path=str(DELIVERABLE),
                    format="Letter",
                    print_background=True,
                    prefer_css_page_size=False,
                    display_header_footer=True,
                    header_template="<span></span>",
                    footer_template=(
                        "<div style='width:100%;font-size:8px;color:#657789;"
                        "padding:0 0.45in;text-align:right;font-family:Arial,sans-serif'>"
                        "Higher Education Data Brief&nbsp;&nbsp;·&nbsp;&nbsp;"
                        "<span class='pageNumber'></span>/<span class='totalPages'></span>"
                        "</div>"
                    ),
                    margin={"top": "0.42in", "right": "0.48in", "bottom": "0.55in", "left": "0.48in"},
                )
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    payload = DELIVERABLE.read_bytes()
    if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-2048:]:
        raise RuntimeError("Generated research brief is not a valid-looking PDF")
    if len(payload) < 40_000:
        raise RuntimeError(f"Generated research brief is unexpectedly small: {len(payload)} bytes")
    page_count = len(re.findall(rb"/Type\s*/Page\b", payload))
    if page_count != 3:
        raise RuntimeError(f"Research brief must remain a concise three-page product; got {page_count} pages")

    shutil.copy2(DELIVERABLE, PUBLIC_COPY)
    if DELIVERABLE.read_bytes() != PUBLIC_COPY.read_bytes():
        raise RuntimeError("Public PDF copy does not match canonical deliverable")

    manifest = {
        "source": "site/research-memo.html",
        "source_sha256": hashlib.sha256(memo.read_bytes()).hexdigest(),
        "pdf_sha256": hashlib.sha256(payload).hexdigest(),
        "pdf_bytes": len(payload),
        "page_count": page_count,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {DELIVERABLE} ({len(payload):,} bytes)")
    print(f"Wrote {MANIFEST}")
    print(f"Published exact copy to {PUBLIC_COPY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
