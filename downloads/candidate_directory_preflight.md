# Candidate 2025 Directory Preflight

This is a **partial-package structural preflight**, not an analysis-year advance. It uses the available candidate-year IPEDS institutional directory and dictionary to reduce directory-side uncertainty while Fall Enrollment remains unavailable.

- **Captured:** 2026-10-17T15:13:02+00:00
- **Preflight status:** PASS
- **Current published analysis year:** 2024
- **Candidate year:** 2025
- **Year advance authorized:** No
- **Release-monitor decision:** `HOLD_YEAR_ADVANCE`

## What passed

The candidate directory contains **5,985 rows**, all **51 states/DC**, zero duplicate UNITIDs, and **6/6 directory variables** required by the current analysis. The candidate CSV and dictionary also match across **70/70 total fields/variables** with no data-only or dictionary-only variables.

| Required field | Candidate dictionary title |
| --- | --- |
| `UNITID` | Unique identification number of the institution |
| `INSTNM` | Institution (entity) name |
| `STABBR` | State abbreviation |
| `CONTROL` | Control of institution |
| `DEGGRANT` | Degree-granting status |
| `PSET4FLG` | Postsecondary and Title IV institution indicator |

## Directory-side continuity

`Directory-eligible` applies only the current directory-side geography and institution filters: 50 states + DC, `DEGGRANT=1`, and `PSET4FLG` in `{1,3}`. It is not the final analytic universe because the candidate Fall Enrollment file is not yet available for the required UNITID match and enrollment-row checks.

| Measure | Current directory | Candidate directory | Change |
| --- | ---: | ---: | ---: |
| Directory rows | 6,072 | 5,985 | -87 |
| Fields | 72 | 70 | -2 |
| Directory-eligible rows | 3,868 | 3,864 | -4 |
| Core states/DC represented | 51 | 51 | 0 |

Among directory-eligible UNITIDs, **3,812** are shared across 2024-2025, **52** enter the directory-side eligible set, and **56** leave it, for a net change of **-4**. Among shared UNITIDs, 6 change control, 3 change state, and 41 have a changed institution name string.

A hashed institution-level change review now covers **154 affected UNITIDs**. It records structural entry/exit reasons, shared attribute changes, and current-year exposure needed for the eventual full-package QA pass. The 56 directory-side leavers include 54 current-analysis institutions with **612 current-year U.S. nonresident students**. Those are review-priority counts, not projected candidate-year losses. See `docs/CANDIDATE_DIRECTORY_CHANGE_REVIEW.md`.

### Control composition

| Control | Current | Candidate | Change |
| --- | ---: | ---: | ---: |
| Public | 1,642 | 1,644 | +2 |
| Private nonprofit | 1,578 | 1,577 | -1 |
| Private for-profit | 648 | 643 | -5 |

## Schema delta

The candidate directory has 70 fields versus 72 in the current directory. Removed fields: `DFRCGID`, `DFRCUSCG`. Added fields: None. The six fields required by the current analytical join/filter are preserved in both the data file and dictionary, but the nonrequired schema change still belongs in the full annual schema review once the complete package is available.

## Source integrity

- `hd2025.csv` from https://nces.ed.gov/ipeds/complete-data-files/HD2025.zip — 1,009,677 archive bytes; SHA-256 `aadad9277a2255c85813b6d206475ddbf8a7330d79cc0236c2ecae685b00f1bf`
- `hd2025.xlsx` from https://nces.ed.gov/ipeds/complete-data-files/HD2025_Dict.zip — 139,157 archive bytes; SHA-256 `dc454aa6fbc246f3d47d773cd02ebe3b5efcedacbd2f71c54ff39f5844215343`

These hashes describe the candidate preflight capture. They do not enter `data/source_manifest.csv` because the candidate directory is not yet part of the canonical analytical source collection.

## Decision boundary

The directory side is structurally ready for later integration, but **no 2025 enrollment finding can be calculated or published from this preflight**. The project remains on Fall 2024 until `EF2025A.zip` and its dictionary are available, the full source package is preserved, and the cross-year schema/QA workflow passes. R01 persistence therefore remains unresolved.
