# Release Readiness Control Matrix

This portfolio control consolidates the project gates required to distinguish a publishable current release from permission to advance the analysis year. It does **not** represent the Presidents' Alliance's internal approval process or organizational sign-off.

- **Current 2024 publication decision:** `READY_WITH_CLAIM_LEVEL_HOLDS`
- **Candidate 2025 year-advance decision:** `HOLD_YEAR_ADVANCE`
- **Candidate package observation:** 2/4 required assets available at `2026-10-14T15:06:36+00:00`
- **Institution-specific claims still held:** 21

The current aggregate publication can remain release-ready while named institution explanations are held. Separately, a partial candidate-year package blocks changing `END_YEAR`; it does not invalidate the already-validated current-year publication.

## Gate matrix

| ID | Scope | Gate | Status | Current release blocker | Year-advance blocker | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Current release | Analytical QA | PASS | Yes | No | 8/8 structural/arithmetic pipeline checks PASS. |
| A02 | Current release | External benchmark | PASS | Yes | No | 24/24 NCES Digest consistency checks PASS. |
| A03 | Current release | High-priority institution review | PASS_WITH_CLAIM_HOLDS | Yes | No | 27/27 high-priority records reviewed; 6 safe with context and 21 institution-specific claims held. |
| A04 | Current release | Publication handoff | PASS_WITH_CLAIM_HOLDS | Yes | No | 14 publication claims/controls have valid authorities, QA gates, disclosures, and release statuses; Q01 preserves claim-level holds. |
| A05 | Current release | Public release register | PASS | Yes | No | 58 artifact families are explicitly PUBLIC; none contain person-level or observed immigration-status data. |
| A06 | Current release | Presentation artifact freshness | PASS | Yes | No | PDF manifest matches its source and 3-page file; PowerPoint manifest matches its builder, 6 sources, and 6-slide file. |
| A07 | Current release | Maintained-source routing coverage | PASS | Yes | No | 17/17 Research Library sources have an explicit refresh/escalation route. |
| Y01 | Year advance | Candidate 2025 IPEDS package | HOLD | No | Yes | 2/4 required candidate-year assets available at 2026-10-14T15:06:36+00:00; snapshot decision=HOLD_YEAR_ADVANCE. |

## Decision boundary

`READY_WITH_CLAIM_LEVEL_HOLDS` means the aggregate/publication controls pass but institution-specific explanatory claims identified by the QA layer remain gated. `HOLD_YEAR_ADVANCE` means the next IPEDS package is incomplete and the project must keep the current analysis year until the complete candidate package is available and schema review begins.

The public-release register is structurally checked here; `scripts/build_data_governance.py`, `scripts/build_site_data.py`, repository tests, and browser QA separately enforce exact-copy publication of the allowlisted tree.
