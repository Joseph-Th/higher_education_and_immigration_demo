# PowerPoint Management Briefing

`deliverables/management_briefing_deck.pptx` is the presentation-facing version of the portfolio analysis. It is designed to demonstrate practical management reporting in PowerPoint in addition to the reproducible Python, Excel, SQL, PDF, and web layers.

## Authority boundary

The deck is a **downstream presentation artifact**. It does not define the project's source data or analytical results. The validated CSV/JSON outputs remain authoritative. `scripts/build_management_deck.py` reads those outputs, writes the canonical PPTX, publishes an exact copy to `site/downloads/management_briefing_deck.pptx`, and records source/builder/PPTX SHA-256 hashes in `deliverables/management_briefing_manifest.json`.

## Slide structure

1. **Cover / reporting frame** — reporting period, headline population definition, and current total.
2. **Executive summary** — four KPI cards plus the latest undergraduate/graduate and institution-accounting decomposition, including the fixed R01 state-breadth baseline.
3. **National trend** — 2015-2024 trend plus decade student-level composition.
4. **Geography** — states/DC at or above the 2019 baseline, largest gains, and largest shortfalls.
5. **Drivers** — institutional-control change and continuing-institution versus universe-entry/exit accounting.
6. **Interpretation and QA** — management takeaways, the pre-specified R01 next-release persistence rule, population/vintage boundaries, and analytical-authority rules.

## Rebuild

Install the development requirements, then run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_management_deck.py
python scripts/validate_project.py
```

The repository tests verify PPTX package integrity, exact slide count, expected management-briefing text and figures, public-copy equality, and freshness of every source/builder hash recorded by the manifest.

## Maintenance

Refresh the deck only after the analytical outputs and narrative have passed the normal QA/benchmark/publication controls. A new PPTX should never be used to override a result from the analytical pipeline. If a source file or the deck builder changes, validation should fail until the presentation is regenerated and reviewed.
