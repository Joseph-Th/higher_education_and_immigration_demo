"""Build and enforce the public data-release governance layer.

The register is intentionally limited to public publication artifacts. The current
project contains no person-level records and no observed immigration-status field.
If future partner work introduces restricted or person-level data, those inputs must
not be added to this PUBLIC register; only approved aggregate outputs may enter the
public tree.
"""

from __future__ import annotations

import csv
import html
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "public_release_register.csv"
DOC_OUTPUT = ROOT / "docs" / "DATA_GOVERNANCE.md"
HTML_OUTPUT = ROOT / "site" / "data-governance.html"
DOWNLOAD_ROOT = ROOT / "site" / "downloads"
SITE_DATA_ROOT = ROOT / "site" / "data"

FIELDS = (
    "artifact_id",
    "source_path",
    "public_path",
    "data_class",
    "unit_of_record",
    "person_level_data",
    "immigration_status_data",
    "release_basis",
    "release_rule",
    "release_decision",
)


def validate_register_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        raise RuntimeError("Public release register cannot be empty")
    ids = [row["artifact_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Public release artifact_id values must be unique")
    public_paths = [row["public_path"] for row in rows]
    if len(public_paths) != len(set(public_paths)):
        raise RuntimeError("Public release public_path values must be unique")
    for row in rows:
        if any(not row[field].strip() for field in FIELDS):
            raise RuntimeError(f"Blank public-release field in {row['artifact_id']}")
        if row["release_decision"] != "PUBLIC":
            raise RuntimeError(
                f"Only approved PUBLIC artifacts belong in the release register: {row['artifact_id']}"
            )
        if row["person_level_data"] != "No" or row["immigration_status_data"] != "No":
            raise RuntimeError(
                f"Person-level or immigration-status data cannot be registered for public release: {row['artifact_id']}"
            )
        for key in ("source_path", "public_path"):
            path = Path(row[key])
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError(f"Unsafe {key} in {row['artifact_id']}: {row[key]}")
        if row["source_path"].startswith("data/raw/"):
            raise RuntimeError(f"Raw source data cannot be published: {row['artifact_id']}")
        if not row["public_path"].startswith("site/downloads/"):
            raise RuntimeError(
                f"Registered public artifacts must live under site/downloads: {row['artifact_id']}"
            )
    return rows


def read_register() -> list[dict[str, str]]:
    with REGISTER.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise RuntimeError(
                f"Public release register schema mismatch: {reader.fieldnames} != {FIELDS}"
            )
        rows = list(reader)
    return validate_register_rows(rows)


def expand_pairs(rows: list[dict[str, str]]) -> list[tuple[Path, Path, dict[str, str]]]:
    pairs: list[tuple[Path, Path, dict[str, str]]] = []
    for row in rows:
        source_pattern = row["source_path"]
        public_pattern = row["public_path"]
        if "*" in source_pattern or "*" in public_pattern:
            if source_pattern.count("*") != 1 or public_pattern.count("*") != 1:
                raise RuntimeError(f"Only one wildcard is supported in {row['artifact_id']}")
            sources = sorted(ROOT.glob(source_pattern))
            if not sources:
                raise RuntimeError(f"Wildcard source matched no files: {source_pattern}")
            public_parent = (ROOT / public_pattern).parent
            for source in sources:
                if not source.is_file():
                    raise RuntimeError(f"Wildcard source is not a file: {source}")
                pairs.append((source, public_parent / source.name, row))
        else:
            source = ROOT / source_pattern
            if not source.is_file():
                raise RuntimeError(f"Registered source does not exist: {source_pattern}")
            pairs.append((source, ROOT / public_pattern, row))
    return pairs


def expanded_file_count(rows: list[dict[str, str]]) -> int:
    count = 0
    for row in rows:
        source_pattern = row["source_path"]
        public_pattern = row["public_path"]
        if "*" in source_pattern or "*" in public_pattern:
            if source_pattern.count("*") != 1 or public_pattern.count("*") != 1:
                raise RuntimeError(f"Only one wildcard is supported in {row['artifact_id']}")
            sources = [path for path in ROOT.glob(source_pattern) if path.is_file()]
            if not sources:
                raise RuntimeError(f"Wildcard source matched no files: {source_pattern}")
            count += len(sources)
        else:
            count += 1
    return count


def publish_registered_downloads(rows: list[dict[str, str]]) -> int:
    pairs = expand_pairs(rows)
    wildcard_dirs = {
        (ROOT / row["public_path"]).parent
        for row in rows
        if "*" in row["public_path"]
    }
    for directory in wildcard_dirs:
        if directory.exists():
            shutil.rmtree(directory)
    for source, public, _ in pairs:
        public.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, public)
    return len(pairs)


def validate_public_tree(rows: list[dict[str, str]]) -> int:
    pairs = expand_pairs(rows)
    expected = {public.resolve() for _, public, _ in pairs}
    actual = {
        path.resolve()
        for path in DOWNLOAD_ROOT.rglob("*")
        if path.is_file()
    }
    missing = sorted(str(path.relative_to(ROOT)) for path in expected - actual)
    extras = sorted(str(path.relative_to(ROOT)) for path in actual - expected)
    if missing:
        raise RuntimeError(f"Registered public artifacts are missing: {missing}")
    if extras:
        raise RuntimeError(f"Unregistered files exist in the public download tree: {extras}")
    for source, public, row in pairs:
        if source.read_bytes() != public.read_bytes():
            raise RuntimeError(
                f"Public artifact is not an exact source copy: {row['artifact_id']} -> {row['public_path']}"
            )

    expected_site_data = {
        (SITE_DATA_ROOT / "site_data.json").resolve(),
        (SITE_DATA_ROOT / "state_profiles.json").resolve(),
    }
    actual_site_data = {
        path.resolve()
        for path in SITE_DATA_ROOT.rglob("*")
        if path.is_file()
    }
    if actual_site_data != expected_site_data:
        missing_data = sorted(
            str(path.relative_to(ROOT)) for path in expected_site_data - actual_site_data
        )
        extra_data = sorted(
            str(path.relative_to(ROOT)) for path in actual_site_data - expected_site_data
        )
        raise RuntimeError(
            f"Public site/data tree mismatch; missing={missing_data} extras={extra_data}"
        )
    return len(pairs)


def render_outputs(rows: list[dict[str, str]]) -> None:
    expanded_count = expanded_file_count(rows)
    class_counts = Counter(row["data_class"] for row in rows)
    lines = [
        "# Data Governance and Public Release Controls",
        "",
        "This portfolio project uses public administrative data and publishes only artifacts explicitly listed in `data/public_release_register.csv`. The current release contains no person-level records and no observed student immigration-status field.",
        "",
        f"**Registered artifact families:** {len(rows)}",
        f"**Expanded public download files:** {expanded_count}",
        "**Current person-level public artifacts:** 0",
        "**Current person-level immigration-status artifacts:** 0",
        "",
        "## Release rules",
        "",
        "1. Raw source archives are never placed in the public download tree.",
        "2. Every public download must appear in the structured release register and be copied byte-for-byte from its canonical project source.",
        "3. `site/downloads/` and `site/data/` are exact allowlisted trees; an unregistered file fails the build.",
        "4. Institution-level IPEDS records are public entity data, not student records; QA flags are triage and are never represented as corrections or person-level findings.",
        "5. If future partner work introduces person-level records, direct identifiers, or observed immigration-status data, those inputs are restricted by default and must not be added to this PUBLIC register. Only reviewed aggregate outputs may be considered for publication.",
        "",
        "## Registered public artifacts",
        "",
        "| ID | Public path | Class | Unit | Release basis |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['artifact_id']} | `{row['public_path']}` | {row['data_class']} | "
            f"{row['unit_of_record']} | {row['release_basis']} |"
        )
    lines.extend(
        [
            "",
            "## Handling boundary",
            "",
            "This register governs the portfolio's public release tree. It is not a claim about the Presidents' Alliance's internal systems, partner agreements, or data-retention policies. Any real partner dataset would require its own authorization, access, retention, disclosure, and destruction rules before analysis begins.",
        ]
    )
    DOC_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    class_cards = "".join(
        f"<article><h3>{html.escape(label)}</h3><p><strong>{count}</strong> registered artifact famil{'y' if count == 1 else 'ies'}.</p></article>"
        for label, count in sorted(class_counts.items())
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Data minimization and public-release controls for the higher-education immigration portfolio research product.">
  <meta name="theme-color" content="#10263c">
  <title>Data Governance | Higher Education Data Brief</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to data governance</a>
  <header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="Back to project home"><span class="brand-mark">IE</span><span>Higher Education Data Brief</span></a><nav aria-label="Data governance navigation"><a href="index.html">Brief</a><a href="research-library.html">Library</a><a href="publication-handoff.html">Handoff</a><a href="research-operations.html">Operations</a></nav></div></header>
  <main id="main">
    <section class="handoff-hero"><div class="shell"><p class="eyebrow">Data governance</p><h1>Public by design does not mean publish everything.</h1><p class="lede">The public site is an allowlisted release surface. Every downloadable artifact is registered, classified, copied from a canonical source, and checked for unexpected files before publication.</p><div class="hero-actions"><a class="button button-primary" href="#release-rules">Review release rules</a><a class="button button-secondary" href="downloads/public_release_register.csv">Download release register</a></div><p class="release-note"><strong>Portfolio boundary:</strong> the current project uses public administrative data and contains no person-level records or observed immigration-status field. Any future restricted partner data would remain nonpublic by default.</p><div class="handoff-summary"><article><strong>{len(rows)}</strong><span>registered artifact families</span></article><article><strong>{expanded_count}</strong><span>expanded public download files</span></article><article><strong>0</strong><span>person-level public records</span></article><article><strong>0</strong><span>observed immigration-status records</span></article></div></div></section>
    <section class="section shell" id="release-rules"><div class="section-heading"><p class="eyebrow">Release gate</p><h2>Five controls before data enter the public tree</h2><p>The build treats public release as an explicit data-handling decision, not as a side effect of copying files into a web directory.</p></div><ol class="handoff-gates"><li><strong>Minimize</strong><span>Use the least sensitive data needed for the research question.</span></li><li><strong>Classify</strong><span>Name the unit, source, and whether person-level or immigration-status data are present.</span></li><li><strong>Allowlist</strong><span>Register the exact canonical source and intended public destination.</span></li><li><strong>Reconcile</strong><span>Require analytical and publication QA before release.</span></li><li><strong>Reject extras</strong><span>Fail the build when an unregistered file appears under public data or downloads.</span></li></ol></section>
    <section class="section section-tinted"><div class="shell"><div class="section-heading compact"><p class="eyebrow">Current release classes</p><h2>Public artifacts are classified before publication</h2></div><div class="method-grid">{class_cards}</div></div></section>
    <section class="section shell"><div class="section-heading compact"><p class="eyebrow">Sensitive-data boundary</p><h2>Future partner microdata start restricted, not public</h2></div><div class="method-grid"><article><h3>Do not collect by default</h3><p>Do not create person-level immigration-status fields merely because a question concerns immigrant or undocumented students. Prefer public or aggregate sources when they can answer the question.</p></article><article><h3>Separate analysis from release</h3><p>A dataset may be authorized for analysis without being authorized for publication. Public release requires a separate, explicit decision.</p></article><article><h3>Publish approved aggregates</h3><p>If restricted inputs are ever needed, only reviewed aggregate outputs should be considered for public release, subject to the actual partner agreement and disclosure rules.</p></article><article><h3>Fail closed</h3><p>The current build rejects unregistered files in the public data tree rather than silently serving them.</p></article></div><div class="memo-actions"><a class="button button-primary" href="downloads/data_governance.md">Download governance note</a><a class="button button-secondary" href="publication-handoff.html">Publication handoff</a></div><p class="release-note">Portfolio demonstration only. This page does not represent the Presidents' Alliance's internal data-retention, privacy, or partner-access policies.</p></section>
  </main>
  <footer><div class="shell footer-inner"><span>Data Governance · Portfolio Demonstration</span><a href="index.html">National brief</a></div></footer>
</body>
</html>
"""
    HTML_OUTPUT.write_text(html_text, encoding="utf-8")


def main() -> int:
    rows = read_register()
    # The governance note is itself a registered publication artifact, so render
    # generated outputs before requiring every source path to exist.
    DOC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    render_outputs(rows)
    pairs = expand_pairs(rows)
    print(
        f"Public release register: {len(rows)} artifact families; {len(pairs)} expanded downloads"
    )
    print(f"Wrote {DOC_OUTPUT}")
    print(f"Wrote {HTML_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
