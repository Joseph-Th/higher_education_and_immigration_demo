# Data Governance and Public Release Controls

This portfolio project uses public administrative data and publishes only artifacts explicitly listed in `data/public_release_register.csv`. The current release contains no person-level records and no observed student immigration-status field.

**Registered artifact families:** 35
**Expanded public download files:** 85
**Current person-level public artifacts:** 0
**Current person-level immigration-status artifacts:** 0

## Release rules

1. Raw source archives are never placed in the public download tree.
2. Every public download must appear in the structured release register and be copied byte-for-byte from its canonical project source.
3. `site/downloads/` and `site/data/` are exact allowlisted trees; an unregistered file fails the build.
4. Institution-level IPEDS records are public entity data, not student records; QA flags are triage and are never represented as corrections or person-level findings.
5. If future partner work introduces person-level records, direct identifiers, or observed immigration-status data, those inputs are restricted by default and must not be added to this PUBLIC register. Only reviewed aggregate outputs may be considered for publication.

## Registered public artifacts

| ID | Public path | Class | Unit | Release basis |
| --- | --- | --- | --- | --- |
| PR01 | `site/downloads/national_year.csv` | Aggregate analytic data | National-year | Derived entirely from public IPEDS administrative data |
| PR02 | `site/downloads/state_year.csv` | Aggregate analytic data | State-year | Derived entirely from public IPEDS administrative data |
| PR03 | `site/downloads/state_change_summary.csv` | Aggregate analytic data | State | Derived entirely from public IPEDS administrative data |
| PR04 | `site/downloads/control_year.csv` | Aggregate analytic data | Institutional-control-year | Derived entirely from public IPEDS administrative data |
| PR05 | `site/downloads/institution_change_summary.csv` | Institution-level public data | Institution endpoint | Derived from public IPEDS institution records |
| PR06 | `site/downloads/latest_release_institution_review.csv` | QA / audit | Institution-year comparison | Derived from public IPEDS institution records |
| PR07 | `site/downloads/institutions_2024.csv` | Institution-level public data | Institution | Derived from public IPEDS institution records |
| PR08 | `site/downloads/schema_audit.csv` | QA / audit | Source year | Project-generated metadata over public source dictionaries |
| PR09 | `site/downloads/source_manifest.csv` | Source provenance | Source archive | Project-generated provenance for public NCES downloads |
| PR10 | `site/downloads/benchmark_audit.csv` | QA / audit | Metric-year | Project-generated comparison to a public NCES benchmark |
| PR11 | `site/downloads/nces_digest_2025_306_10.csv` | External benchmark | Metric-year | Compact transcription of a public NCES table used only for validation |
| PR12 | `site/downloads/latest_update_review.md` | Publication | Research update memo | Generated from validated public administrative data |
| PR13 | `site/downloads/qa_resolution_log.csv` | QA / audit | Institution review | Analyst review of public institution-level records and public evidence links |
| PR14 | `site/downloads/qa_resolution_log.md` | Publication | Institution review memo | Generated from the QA resolution register |
| PR15 | `site/downloads/research_library.csv` | Research governance | Source resource | Metadata describing public sources and research products |
| PR16 | `site/downloads/research_library.md` | Publication | Source guide | Generated from the structured Research Library |
| PR17 | `site/downloads/research_agenda.csv` | Research governance | Research question | Project planning metadata with no participant or respondent records |
| PR18 | `site/downloads/research_agenda.md` | Publication | Research agenda | Generated from the structured research agenda |
| PR19 | `site/downloads/publication_handoff.csv` | Research governance | Public claim/control | Generated from validated project outputs |
| PR20 | `site/downloads/publication_handoff.md` | Publication | Publication handoff memo | Generated from the structured publication handoff |
| PR21 | `site/downloads/population_crosswalk.csv` | Research governance | Population/source definition | Methodology metadata over public population definitions and sources |
| PR22 | `site/downloads/population_crosswalk.md` | Publication | Methodology crosswalk | Generated from the population/source crosswalk |
| PR23 | `site/downloads/recurring_report_register.csv` | Research governance | Recurring research product | Portfolio operations metadata grounded in public product information |
| PR24 | `site/downloads/recurring_report_register.md` | Publication | Recurring report operations memo | Generated from the recurring-report register |
| PR25 | `site/downloads/briefing_note.md` | Publication | Stakeholder briefing | Generated from validated aggregate findings and QA status |
| PR26 | `site/downloads/research_memo.md` | Publication | Research memo | Generated from validated aggregate findings and public institution evidence |
| PR27 | `site/downloads/ipeds_portfolio_analysis.xlsx` | Publication | Analysis workbook | Workbook built from public administrative data and validated project outputs |
| PR28 | `site/downloads/research_brief.pdf` | Publication | Research brief | PDF generated from the validated public research memo |
| PR29 | `site/downloads/state_profile_index.csv` | Aggregate analytic data | State | Derived entirely from public IPEDS administrative data |
| PR30 | `site/downloads/state_profiles/*.md` | State publication | State profile | Generated from public state and institution-level IPEDS outputs |
| PR31 | `site/downloads/public_release_register.csv` | Research governance | Public artifact control | Project release-control metadata |
| PR32 | `site/downloads/data_governance.md` | Publication | Data governance note | Generated from the public release register and project handling rules |
| PR33 | `site/downloads/production_cycle_register.csv` | Research governance | Production stage control | Portfolio coordination metadata with no partner-confidential or person-level records |
| PR34 | `site/downloads/production_cycle.md` | Publication | Production-cycle coordination note | Generated from the stage register and public recurring-product operations metadata |
| PR35 | `site/downloads/production_cycle_log_template.csv` | Research governance | Blank live-cycle coordination log template | Empty portfolio template containing field names only |

## Handling boundary

This register governs the portfolio's public release tree. It is not a claim about the Presidents' Alliance's internal systems, partner agreements, or data-retention policies. Any real partner dataset would require its own authorization, access, retention, disclosure, and destruction rules before analysis begins.