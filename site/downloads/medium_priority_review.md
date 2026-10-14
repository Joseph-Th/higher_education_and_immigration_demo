# Medium-Priority Institution QA Triage

This review routes all **50 current medium-priority 2023-2024 institution flags** using only the reason codes already produced by the annual QA rules. It does not create a second risk score, resolve the records, or change source values.

## What the queue represents

- **Percentage-movement route:** 28 rows
- **Absolute-movement route:** 11 rows
- **Absolute + percentage route:** 8 rows
- **Structural/reporting route:** 3 rows
- **Candidate-directory overlap:** 5 rows representing 2,443 current-year U.S. nonresident students

The queue is mixed-direction: 25 gain rows contribute **+7,806**, 23 decline rows contribute **-9,241**, and 2 rows have zero enrollment change. Net movement across the medium queue is **-1,435** against **17,047** of gross absolute movement. These totals describe the flagged subset only and are not a national trend estimate.

## Review routes

| Route | Rows | What triggered the route | Review action |
| --- | ---: | --- | --- |
| Structural / reporting context | 3 | Analytic-universe change or non-R/Z imputation/status transition | Review structural/reporting evidence before interpreting movement |
| Absolute + percentage movement | 8 | At least 500 students plus a percentage threshold | Inspect multi-year history and source/institution context |
| Absolute movement | 11 | At least 500 students without a medium-level percentage trigger | Inspect multi-year history and source status |
| Percentage movement | 28 | At least 50% from a 100+ baseline without a 500-student change | Verify denominator scale and multi-year history |

## Largest medium-priority movements

| Institution | State | Change | Percent | Route | Candidate directory overlap |
| --- | --- | ---: | ---: | --- | --- |
| Indiana Wesleyan University-National & Global | IN | +855 | +29.8% | Absolute + percentage movement | No |
| The University of Texas at Arlington | TX | -846 | -14.7% | Absolute movement | No |
| Georgia Institute of Technology-Main Campus | GA | +835 | +6.6% | Absolute movement | No |
| University of Illinois Urbana-Champaign | IL | +775 | +6.2% | Absolute movement | No |
| Syracuse University | NY | -760 | -18.3% | Absolute movement | No |
| University of Colorado Boulder | CO | -755 | -23.2% | Absolute movement | No |
| Valencia College | FL | +692 | +25.9% | Absolute + percentage movement | No |
| Dallas College | TX | +628 | +29.5% | Absolute + percentage movement | No |
| Northeastern University | MA | -616 | -5.1% | Absolute movement | No |
| Chaffey College | CA | -611 | -87.5% | Absolute + percentage movement | No |

## Structural / reporting-context rows

These three records require structural or reporting-context review before any institution-specific interpretation. Their presence does not establish an error.

| Institution | Status | Change | Flags | Reason |
| --- | --- | ---: | --- | --- |
| New Orleans Baptist Theological Seminary | Entered analytic universe | +129 | — → R | analytic-universe membership changed; universe entry/exit involves at least 100 students |
| City College-Hollywood | Continuing | 0 | R → P | imputation/status flag changed to or from a non-R/Z code |
| City College-Altamonte Springs | Continuing | 0 | R → P | imputation/status flag changed to or from a non-R/Z code |

## Medium-priority rows that also changed in the candidate directory

The 5 cross-signal overlaps should be reviewed with both the latest enrollment movement and candidate directory continuity visible. Their current 2024 U.S. nonresident enrollment sums to **2,443**.

| Institution | State | Change | Review route | Candidate directory signal |
| --- | --- | ---: | --- | --- |
| City College-Hollywood | FL | 0 | Structural / reporting context | Left directory eligible: title_iv_first_look_status_lost |
| City College-Altamonte Springs | FL | 0 | Structural / reporting context | Left directory eligible: title_iv_first_look_status_lost |
| Lindsey Wilson College | KY | +590 | Absolute + percentage movement | Shared attribute change: institution_name_changed |
| FIDM-Fashion Institute of Design & Merchandising | CA | -166 | Percentage movement | Left directory eligible: title_iv_first_look_status_lost |
| Humphreys University-Stockton and Modesto Campuses | CA | +116 | Percentage movement | Shared attribute change: institution_name_changed |

## Interpretation boundary

**Medium-priority flag is a triage signal, not a source correction or publication clearance. Do not promote an institution-specific movement into narrative without evidence review.**

The four routes describe why the existing medium-priority threshold fired and what evidence to inspect next. They are not severity grades. A candidate-directory overlap does not upgrade a row to high priority, and no medium row receives a publication disposition from this artifact.
