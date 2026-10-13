# Data Calendar

This project treats data currency as an operational responsibility rather than a one-time collection task.

## Current published coverage

| Component | Latest year used | Current project treatment |
| --- | ---: | --- |
| Fall Enrollment (`EFyyyyA`) | 2024 | Provisional |
| Institutional directory (`HDyyyy`) | 2024 | Same-year join for published analysis |
| NCES Digest external benchmark | 2024 | Provisional year in Digest 2025 Table 306.10 |

The current source archives were retrieved on October 13, 2026. Exact timestamps and hashes are in `data/source_manifest.csv`.

## Next-release check

Run:

```bash
python scripts/check_for_new_release.py
```

The script checks the NCES Complete Data Files endpoint for the next year's:

- Fall Enrollment data;
- Fall Enrollment dictionary;
- institutional directory data; and
- institutional directory dictionary.

**Last checked October 13, 2026:** the 2025 institutional directory and dictionary are available, while `EF2025A.zip` and `EF2025A_Dict.zip` are not yet available at the Complete Data Files endpoint. The project therefore remains correctly pinned to Fall 2024.

The check is deliberately **not** part of `scripts/validate_project.py` because reproducibility of the current release should not depend on network availability or the state of a future NCES release.

## Research Library health check

Run:

```bash
python scripts/check_research_library.py
```

This separate online lane checks every URL in `data/research_library.csv`, follows redirects, and reports HTTP/network failures. HTTP 401/403 responses are reported separately as **scripted-access restrictions**, not silently treated as either success or a broken link; those resources require manual browser review. The command fails on network errors and other broken HTTP responses such as 404/5xx. It does not modify the recorded `last_checked` metadata automatically; a human source review is still required before changing that field. Keeping this check outside `scripts/validate_project.py` prevents temporary external-site outages from breaking the offline research build.

Do not advance `END_YEAR` merely because a directory file exists. The recurring analysis is ready to advance only when the Fall Enrollment data and its dictionary are available and pass the schema review.

## Update trigger

When the next Fall Enrollment archive becomes available:

1. confirm the release status on NCES;
2. follow `docs/UPDATE_PLAYBOOK.md`;
3. preserve the prior source lineage through manifest hashes;
4. rerun the schema audit before interpreting new values; and
5. re-review every public finding after the data rebuild.

This separation between **release detection**, **source collection**, **schema validation**, and **publication** is intentional. A newly posted file is a trigger for review, not automatic permission to publish.

