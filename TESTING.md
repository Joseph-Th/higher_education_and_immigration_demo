# Testing

**Document role:** Verification authority for the reproducible research pipeline and its published artifacts.

Use the narrowest proof that covers the changed analytical or publication contract.

## Focused work

For one builder, validator, or analytical owner, run that script and its directly relevant tests. The repository test suite is:

```text
python -m unittest discover -s tests -v
```

Do not rebuild every downstream artifact after a documentation-only edit or a change isolated to one independent builder when the broader pipeline cannot be affected.

## Complete offline validation

Changes to shared analytical inputs, cross-artifact reconciliation, publication governance, or the common site data use the repository-owned complete lane:

```text
python scripts/validate_project.py
```

That command compiles the Python sources, audits the cross-year schema, rebuilds derived analysis and publication data, reruns benchmark reconciliation, and executes the repository tests. It is the authority for a full internally-consistent rebuild.

## Published artifacts

PDF, spreadsheet, presentation, and site changes are not proven by successful generation alone. Inspect the affected rendered output and verify that it still matches the validated analytical source and its freshness/provenance manifest where one exists.

Browser-facing publication changes require the repository's existing browser QA at the affected desktop/mobile widths. Deployment is a separate boundary owned by `docs/DEPLOYMENT.md`; a local validation pass is not evidence that the live publication was refreshed.

## Source and release boundaries

- Preserve source URL, retrieval time, file size, and SHA-256 provenance for raw public inputs.
- Do not interpret missing or partial next-release assets as zero or as permission to advance the analysis year.
- A generated public file must be registered by the public-release governance before publication.
- Keep scratch and intermediate artifacts inside project-owned output locations; do not place them at the workspace root.
