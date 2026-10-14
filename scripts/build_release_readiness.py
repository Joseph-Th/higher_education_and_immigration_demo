"""Build a consolidated offline release-readiness control matrix.

The project has several independent controls: analytical QA, an external
benchmark, institution-level review, publication handoff, public-release
governance, presentation freshness, source-update routing, and a next-year
package gate. This product combines those controls without collapsing two
different decisions:

1. whether the current validated publication can be released; and
2. whether the analysis year may advance to the candidate IPEDS year.

The current-release decision may remain ready while specific institution claims
stay held. A partial next-year package may also block year advancement without
invalidating the already-validated current publication.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

from build_data_governance import read_register as read_public_release_register
from project_config import END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC_OUTPUT = ROOT / "docs" / "RELEASE_READINESS.md"
CSV_OUTPUT = DATA / "release_readiness.csv"
HTML_OUTPUT = ROOT / "site" / "release-readiness.html"

FIELDS = (
    "gate_id",
    "gate_scope",
    "gate_name",
    "status",
    "blocks_current_release",
    "blocks_year_advance",
    "evidence",
    "authority",
    "next_action",
)
ALLOWED_STATUSES = {"PASS", "PASS_WITH_CLAIM_HOLDS", "HOLD"}
EXPECTED_HANDOFF_IDS = {
    "N01",
    "N02",
    "N03",
    "N04",
    "N05",
    "N06",
    "S01",
    "C01",
    "I01",
    "Q01",
    "M01",
    "M02",
    "P01",
    "G01",
    "B01",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_presentation_freshness() -> str:
    pdf_manifest = json.loads(
        (ROOT / "deliverables" / "research_brief_manifest.json").read_text(encoding="utf-8")
    )
    pdf_source = ROOT / pdf_manifest["source"]
    pdf = ROOT / "deliverables" / "research_brief.pdf"
    public_pdf = ROOT / "site" / "downloads" / "research_brief.pdf"
    if sha256(pdf_source) != pdf_manifest["source_sha256"]:
        raise RuntimeError("Research brief source is newer than its PDF manifest")
    if sha256(pdf) != pdf_manifest["pdf_sha256"]:
        raise RuntimeError("Research brief PDF does not match its manifest")
    if pdf.read_bytes() != public_pdf.read_bytes():
        raise RuntimeError("Public research brief PDF is not the canonical deliverable")

    deck_manifest = json.loads(
        (ROOT / "deliverables" / "management_briefing_manifest.json").read_text(encoding="utf-8")
    )
    builder = ROOT / deck_manifest["builder"]
    deck = ROOT / "deliverables" / "management_briefing_deck.pptx"
    public_deck = ROOT / "site" / "downloads" / "management_briefing_deck.pptx"
    if sha256(builder) != deck_manifest["builder_sha256"]:
        raise RuntimeError("Management deck builder is newer than its manifest")
    for source_name, expected_hash in deck_manifest["source_sha256"].items():
        if sha256(ROOT / source_name) != expected_hash:
            raise RuntimeError(f"Management deck source is newer than its manifest: {source_name}")
    if sha256(deck) != deck_manifest["pptx_sha256"]:
        raise RuntimeError("Management deck does not match its manifest")
    if deck.read_bytes() != public_deck.read_bytes():
        raise RuntimeError("Public management deck is not the canonical deliverable")
    return (
        f"PDF manifest matches its source and {pdf_manifest['page_count']}-page file; "
        f"PowerPoint manifest matches its builder, {len(deck_manifest['source_sha256'])} sources, "
        f"and {deck_manifest['slide_count']}-slide file."
    )


def build_rows() -> tuple[list[dict[str, str]], dict[str, object]]:
    qa = json.loads((DATA / "qa_report.json").read_text(encoding="utf-8"))
    benchmark = read_csv(DATA / "benchmark_audit.csv")
    resolution = json.loads((DATA / "qa_resolution_summary.json").read_text(encoding="utf-8"))
    handoff = read_csv(DATA / "publication_handoff.csv")
    release_register = read_public_release_register()
    library = read_csv(DATA / "research_library.csv")
    triage = read_csv(DATA / "source_update_triage.csv")
    snapshot = json.loads((DATA / "release_monitor_snapshot.json").read_text(encoding="utf-8"))

    if not qa.get("checks") or any(value != "PASS" for value in qa["checks"].values()):
        raise RuntimeError("Release readiness requires all analytical QA checks to pass")
    benchmark_passed = sum(row["status"] == "PASS" for row in benchmark)
    if not benchmark or benchmark_passed != len(benchmark):
        raise RuntimeError("Release readiness requires all external benchmark checks to pass")
    if not resolution.get("required_high_priority_covered"):
        raise RuntimeError("Release readiness requires complete high-priority QA review coverage")
    if resolution["reviewed_count"] != resolution["high_priority_total"]:
        raise RuntimeError("Release readiness high-priority review counts do not reconcile")

    handoff_ids = {row["claim_id"] for row in handoff}
    if handoff_ids != EXPECTED_HANDOFF_IDS or len(handoff) != len(EXPECTED_HANDOFF_IDS):
        raise RuntimeError("Release readiness requires the complete publication handoff control set")
    allowed_handoff_statuses = {"READY", "READY WITH CONTEXT", "READY WITH CLAIM-LEVEL HOLDS"}
    if any(row["publication_status"] not in allowed_handoff_statuses for row in handoff):
        raise RuntimeError("Publication handoff contains a non-releaseable status")
    claim_hold_rows = [row for row in handoff if row["publication_status"] == "READY WITH CLAIM-LEVEL HOLDS"]
    if {row["claim_id"] for row in claim_hold_rows} != {"Q01"}:
        raise RuntimeError("Claim-level publication holds must remain isolated to the institution QA control")

    release_ids = {row["artifact_id"] for row in release_register}
    if not {"PR57", "PR58"}.issubset(release_ids):
        raise RuntimeError("Release readiness artifacts must be registered before publication")
    if any(row["release_decision"] != "PUBLIC" for row in release_register):
        raise RuntimeError("Public release register contains a non-PUBLIC row")
    if any(
        row["person_level_data"] != "No" or row["immigration_status_data"] != "No"
        for row in release_register
    ):
        raise RuntimeError("Public release register contains a sensitive-data release")

    library_ids = {row["resource_id"] for row in library}
    triage_ids = {row["resource_id"] for row in triage}
    if not library or triage_ids != library_ids or len(triage) != len(library):
        raise RuntimeError("Release readiness requires one-for-one source-update routing coverage")

    presentation_evidence = validate_presentation_freshness()

    if snapshot["current_analysis_end_year"] != END_YEAR:
        raise RuntimeError("Release snapshot current year does not match project END_YEAR")
    file_rows = snapshot.get("files", [])
    if len(file_rows) != 4:
        raise RuntimeError("Release readiness requires exactly four candidate-year package observations")
    available_count = sum(bool(row["available"]) for row in file_rows)
    package_ready = available_count == len(file_rows)
    derived_year_decision = "READY_FOR_SCHEMA_REVIEW" if package_ready else "HOLD_YEAR_ADVANCE"
    if snapshot["package_ready"] != package_ready or snapshot["release_decision"] != derived_year_decision:
        raise RuntimeError("Release snapshot decision does not reconcile to candidate-file availability")

    rows = [
        {
            "gate_id": "A01",
            "gate_scope": "Current release",
            "gate_name": "Analytical QA",
            "status": "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": f"{len(qa['checks'])}/{len(qa['checks'])} structural/arithmetic pipeline checks PASS.",
            "authority": "data/qa_report.json",
            "next_action": "Keep the current analytical outputs only while every QA check remains PASS.",
        },
        {
            "gate_id": "A02",
            "gate_scope": "Current release",
            "gate_name": "External benchmark",
            "status": "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": f"{benchmark_passed}/{len(benchmark)} NCES Digest consistency checks PASS.",
            "authority": "data/benchmark_audit.csv",
            "next_action": "Investigate any future failed benchmark before changing public interpretation.",
        },
        {
            "gate_id": "A03",
            "gate_scope": "Current release",
            "gate_name": "High-priority institution review",
            "status": "PASS_WITH_CLAIM_HOLDS" if resolution["hold_for_confirmation"] else "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": (
                f"{resolution['reviewed_count']}/{resolution['high_priority_total']} high-priority records reviewed; "
                f"{resolution['safe_with_context']} safe with context and "
                f"{resolution['hold_for_confirmation']} institution-specific claims held."
            ),
            "authority": "data/qa_resolution_summary.json",
            "next_action": "Keep held institution movements out of institution-specific explanatory narrative until directly confirmed.",
        },
        {
            "gate_id": "A04",
            "gate_scope": "Current release",
            "gate_name": "Publication handoff",
            "status": "PASS_WITH_CLAIM_HOLDS" if claim_hold_rows else "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": f"{len(handoff)} publication claims/controls have valid authorities, QA gates, disclosures, and release statuses; Q01 preserves claim-level holds.",
            "authority": "data/publication_handoff.csv",
            "next_action": "Rebuild and re-read the handoff whenever data, definitions, sources, or public copy change.",
        },
        {
            "gate_id": "A05",
            "gate_scope": "Current release",
            "gate_name": "Public release register",
            "status": "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": f"{len(release_register)} artifact families are explicitly PUBLIC; none contain person-level or observed immigration-status data.",
            "authority": "data/public_release_register.csv",
            "next_action": "Run data-governance publication after this build so the public download tree is copied and checked byte-for-byte.",
        },
        {
            "gate_id": "A06",
            "gate_scope": "Current release",
            "gate_name": "Presentation artifact freshness",
            "status": "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": presentation_evidence,
            "authority": "deliverables/research_brief_manifest.json; deliverables/management_briefing_manifest.json",
            "next_action": "Rebuild and visually review the PDF or deck when any bound source or builder changes.",
        },
        {
            "gate_id": "A07",
            "gate_scope": "Current release",
            "gate_name": "Maintained-source routing coverage",
            "status": "PASS",
            "blocks_current_release": "Yes",
            "blocks_year_advance": "No",
            "evidence": f"{len(triage)}/{len(library)} Research Library sources have an explicit refresh/escalation route.",
            "authority": "data/source_update_triage.csv",
            "next_action": "Route a changed source by method/governance impact before treating a new date or file as a new finding.",
        },
        {
            "gate_id": "Y01",
            "gate_scope": "Year advance",
            "gate_name": f"Candidate {snapshot['candidate_next_year']} IPEDS package",
            "status": "PASS" if package_ready else "HOLD",
            "blocks_current_release": "No",
            "blocks_year_advance": "Yes",
            "evidence": (
                f"{available_count}/{len(file_rows)} required candidate-year assets available at "
                f"{snapshot['checked_at_utc']}; snapshot decision={snapshot['release_decision']}."
            ),
            "authority": "data/release_monitor_snapshot.json",
            "next_action": (
                "Begin schema review before changing END_YEAR."
                if package_ready
                else f"Keep END_YEAR={END_YEAR}; recheck when the missing Fall Enrollment package assets are published."
            ),
        },
    ]

    if any(row["status"] not in ALLOWED_STATUSES for row in rows):
        raise RuntimeError("Release readiness produced an unsupported gate status")
    current_blockers = [
        row for row in rows
        if row["blocks_current_release"] == "Yes" and row["status"] == "HOLD"
    ]
    year_blockers = [
        row for row in rows
        if row["blocks_year_advance"] == "Yes" and row["status"] == "HOLD"
    ]
    current_decision = (
        "HOLD_CURRENT_RELEASE"
        if current_blockers
        else (
            "READY_WITH_CLAIM_LEVEL_HOLDS"
            if any(row["status"] == "PASS_WITH_CLAIM_HOLDS" for row in rows)
            else "READY_TO_PUBLISH"
        )
    )
    year_decision = "HOLD_YEAR_ADVANCE" if year_blockers else "READY_FOR_SCHEMA_REVIEW"
    if year_decision != snapshot["release_decision"]:
        raise RuntimeError("Consolidated year-advance decision does not match the release snapshot")

    summary: dict[str, object] = {
        "current_release_decision": current_decision,
        "year_advance_decision": year_decision,
        "current_year": END_YEAR,
        "candidate_year": snapshot["candidate_next_year"],
        "snapshot_checked_at_utc": snapshot["checked_at_utc"],
        "gate_count": len(rows),
        "current_release_gate_count": sum(row["blocks_current_release"] == "Yes" for row in rows),
        "year_advance_gate_count": sum(row["blocks_year_advance"] == "Yes" for row in rows),
        "claim_holds": resolution["hold_for_confirmation"],
        "candidate_assets_available": available_count,
        "candidate_assets_required": len(file_rows),
    }
    return rows, summary


def write_csv(rows: list[dict[str, str]]) -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    lines = [
        "# Release Readiness Control Matrix",
        "",
        "This portfolio control consolidates the project gates required to distinguish a publishable current release from permission to advance the analysis year. It does **not** represent the Presidents' Alliance's internal approval process or organizational sign-off.",
        "",
        f"- **Current {summary['current_year']} publication decision:** `{summary['current_release_decision']}`",
        f"- **Candidate {summary['candidate_year']} year-advance decision:** `{summary['year_advance_decision']}`",
        f"- **Candidate package observation:** {summary['candidate_assets_available']}/{summary['candidate_assets_required']} required assets available at `{summary['snapshot_checked_at_utc']}`",
        f"- **Institution-specific claims still held:** {summary['claim_holds']}",
        "",
        "The current aggregate publication can remain release-ready while named institution explanations are held. Separately, a partial candidate-year package blocks changing `END_YEAR`; it does not invalidate the already-validated current-year publication.",
        "",
        "## Gate matrix",
        "",
        "| ID | Scope | Gate | Status | Current release blocker | Year-advance blocker | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['gate_id']} | {row['gate_scope']} | {row['gate_name']} | {row['status']} | "
            f"{row['blocks_current_release']} | {row['blocks_year_advance']} | {row['evidence']} |"
        )
    lines.extend(
        [
            "",
            "## Decision boundary",
            "",
            "`READY_WITH_CLAIM_LEVEL_HOLDS` means the aggregate/publication controls pass but institution-specific explanatory claims identified by the QA layer remain gated. `HOLD_YEAR_ADVANCE` means the next IPEDS package is incomplete and the project must keep the current analysis year until the complete candidate package is available and schema review begins.",
            "",
            "The public-release register is structurally checked here; `scripts/build_data_governance.py`, `scripts/build_site_data.py`, repository tests, and browser QA separately enforce exact-copy publication of the allowlisted tree.",
            "",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def write_html(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    cards = []
    for row in rows:
        status_class = "handoff-status-hold" if row["status"] in {"HOLD", "PASS_WITH_CLAIM_HOLDS"} else "handoff-status-ready"
        cards.append(
            f"""
          <article class="handoff-card" data-readiness-gate="{html.escape(row['gate_id'])}">
            <div class="handoff-card-head"><span>{html.escape(row['gate_id'])}</span><span class="handoff-status {status_class}">{html.escape(row['status'].replace('_', ' '))}</span></div>
            <p class="case-kicker">{html.escape(row['gate_scope'])}</p>
            <h2>{html.escape(row['gate_name'])}</h2>
            <dl class="handoff-meta">
              <div><dt>Evidence</dt><dd>{html.escape(row['evidence'])}</dd></div>
              <div><dt>Authority</dt><dd><code>{html.escape(row['authority'])}</code></dd></div>
              <div><dt>Next action</dt><dd>{html.escape(row['next_action'])}</dd></div>
            </dl>
          </article>"""
        )

    current_label = str(summary["current_release_decision"]).replace("_", " ").replace("CLAIM LEVEL", "CLAIM-LEVEL")
    year_label = str(summary["year_advance_decision"]).replace("_", " ")
    HTML_OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Consolidated release-readiness controls separating the current publication decision from permission to advance the IPEDS analysis year.">
  <meta name="theme-color" content="#10263c">
  <title>Release Readiness | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to release readiness</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Release readiness navigation"><a href="index.html">Brief</a><a href="freshness-monitor.html">Freshness</a><a href="publication-handoff.html">Handoff</a><a href="data-governance.html">Governance</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero" data-current-decision="{html.escape(str(summary['current_release_decision']))}" data-year-decision="{html.escape(str(summary['year_advance_decision']))}"><div class="shell"><p class="eyebrow">Release control</p><h1>Current publication readiness and next-year readiness are different decisions.</h1><p class="lede">This control matrix consolidates analytical QA, benchmarks, institution review, publication handoff, public-release governance, artifact freshness, source routing, and the candidate-year package gate without allowing one decision to stand in for the other.</p><div class="hero-actions"><a class="button button-primary" href="#readiness-gates">Review gates</a><a class="button button-secondary" href="downloads/release_readiness.csv">Download control matrix</a></div><p class="release-note"><strong>Portfolio boundary:</strong> this is a reproducible project control, not the Presidents' Alliance's internal approval process or organizational sign-off.</p><div class="handoff-summary"><article><strong>{html.escape(current_label)}</strong><span>current {summary['current_year']} publication</span></article><article><strong>{html.escape(year_label)}</strong><span>candidate {summary['candidate_year']} year advance</span></article><article><strong>{summary['claim_holds']}</strong><span>institution-specific claims still held</span></article><article><strong>{summary['candidate_assets_available']}/{summary['candidate_assets_required']}</strong><span>candidate-year package assets available</span></article></div></div></section>
    <section class="section shell"><div class="section-heading"><p class="eyebrow">Decision separation</p><h2>A hold can be narrow without becoming a blanket publication failure.</h2><p>The current aggregate release is ready because its analytical, benchmark, handoff, governance, artifact, and routing controls pass. Institution-specific explanations remain held where evidence is insufficient. Separately, the candidate-year package is incomplete, so the project must not change the analysis year.</p></div><div class="method-grid"><article><h3>Current release</h3><p><strong>{html.escape(current_label)}</strong><br>Aggregate publication can proceed with the existing institution-level claim holds intact.</p></article><article><h3>Year advance</h3><p><strong>{html.escape(year_label)}</strong><br>Only {summary['candidate_assets_available']} of {summary['candidate_assets_required']} required candidate-year assets are available.</p></article><article><h3>Claim holds</h3><p><strong>{summary['claim_holds']}</strong><br>Held institution-specific explanations do not rewrite or remove the official aggregate IPEDS values.</p></article><article><h3>Snapshot time</h3><p><strong>{html.escape(str(summary['snapshot_checked_at_utc']))}</strong><br>The next-year package result is a dated observation, not a continuously live status.</p></article></div></section>
    <section class="section section-tinted" id="readiness-gates"><div class="shell"><div class="section-heading"><p class="eyebrow">Control matrix</p><h2>Eight gates with explicit blocking scope.</h2><p>Seven controls govern the current release. The candidate-package gate governs whether the project may begin a year advance. A future failure stops only the decision whose blocker column applies.</p></div><div class="handoff-grid">{''.join(cards)}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Operating rule</p><h2>Ready now does not mean advance the year.</h2></div><div class="method-grid"><article><h3>Publish current data</h3><p>Keep the current aggregate publication available while its seven current-release gates remain satisfied.</p></article><article><h3>Respect claim-level holds</h3><p>Do not promote a held institution movement into explanatory narrative merely because aggregate publication is ready.</p></article><article><h3>Wait for the complete package</h3><p>Keep <code>END_YEAR={END_YEAR}</code> until all four candidate assets are available; availability then starts schema review rather than automatic publication.</p></article><article><h3>Exact public tree</h3><p>The downstream data-governance build and repository/browser checks enforce the allowlisted public copies byte-for-byte.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/release_readiness.csv">Download readiness CSV</a><a class="button button-secondary" href="downloads/release_readiness.md">Download readiness note</a><a class="button button-secondary" href="freshness-monitor.html">Next-year freshness</a><a class="button button-secondary" href="publication-handoff.html">Publication handoff</a></div></section>
  </main>
  <footer><div class="shell footer-inner"><span>Release Readiness · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    rows, summary = build_rows()
    write_csv(rows)
    write_markdown(rows, summary)
    write_html(rows, summary)
    print(
        "Release readiness: "
        f"current={summary['current_release_decision']}; "
        f"year_advance={summary['year_advance_decision']}; "
        f"gates={summary['gate_count']}"
    )
    print(f"Wrote {CSV_OUTPUT}")
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
