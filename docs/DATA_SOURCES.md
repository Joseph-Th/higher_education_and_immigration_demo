# Data Sources

## Primary source

**National Center for Education Statistics (NCES), Integrated Postsecondary Education Data System (IPEDS)**  
U.S. Department of Education, Institute of Education Sciences  
https://nces.ed.gov/ipeds/

IPEDS Complete Data Files documentation:  
https://nces.ed.gov/ipeds/help/complete-data-files

IPEDS release-cycle documentation:  
https://nces.ed.gov/ipeds/use-the-data/timing-of-ipeds-data-collection

## Initial tables

### Fall Enrollment: `EFyyyyA`

Files: `EF2015A` through `EF2024A`

Purpose: institution-level fall enrollment counts by race/ethnicity, gender, attendance status, and student level.

The analysis will use the U.S. nonresident category only after the relevant variables and aggregation levels are verified against each year's data dictionary.

### Institutional directory: `HDyyyy`

Files: `HD2015` through `HD2024`

Purpose: institution metadata used to attach state, institution name, sector/control, and other directory fields to enrollment records.

## Collection status

The initial collection was completed on **October 13, 2026**. It contains 40 NCES archives: enrollment data, enrollment dictionaries, institutional directory data, and institutional directory dictionaries for each year from 2015 through 2024.

The exact retrieval timestamps, archive sizes, SHA-256 hashes, source URLs, and extracted filenames are recorded in `data/source_manifest.csv`.

The required cross-year schema currently passes the automated audit for all ten years. See `data/schema_audit.csv` and `docs/VARIABLE_MAPPING.md`.

## Retrieval endpoints

NCES currently exposes two URL patterns across the requested years:

- 2015-2023 historical files: `https://nces.ed.gov/ipeds/datacenter/data/<TABLE>.zip`
- 2024 files: `https://nces.ed.gov/ipeds/complete-data-files/<TABLE>.zip`

Data dictionaries follow the same pattern with `_Dict.zip` appended to the table name.

The repository's download script encodes this distinction and records the exact URL used for each file in `data/source_manifest.csv`.

## Release treatment

The project distinguishes **data year**, **collection/release vintage**, and **release status**.

- Historical years will use the current NCES complete-data files available at retrieval time.
- Fall 2024 is part of the 2024-25 IPEDS collection cycle. The 2024-25 IPEDS Access database is currently identified by NCES as provisional, so this project will treat the Fall 2024 values as provisional unless NCES documentation for the specific complete-data file establishes otherwise.
- Published output will label provisional data explicitly.
- If NCES later issues a final/revised 2024 file, the source manifest and analysis will be refreshed rather than silently replacing the source.

## Source integrity

For every downloaded archive, the collection script records:

- table name;
- data year;
- source type (`data` or `dictionary`);
- source URL;
- retrieval timestamp in UTC;
- byte size;
- SHA-256 hash;
- extracted file names.

This allows the exact source vintage used in the analysis to be identified later even if NCES updates a file at the same URL.

## Definitions requiring special care

IPEDS defines **U.S. nonresident** as a person who is not a U.S. citizen or national, is in the United States on a visa or temporary basis, and does not have the right to remain indefinitely. Current IPEDS instructions state that DACA recipients, undocumented students, and other eligible noncitizens are not to be reported in the U.S. nonresident category.

This project will therefore avoid using "immigrant," "undocumented," and "international" interchangeably with the IPEDS U.S. nonresident category.

## Additional sources under consideration

The first analysis will remain IPEDS-only. Later contextual work may use other official or well-documented sources, but any additional source will receive its own provenance and comparability review before inclusion.

