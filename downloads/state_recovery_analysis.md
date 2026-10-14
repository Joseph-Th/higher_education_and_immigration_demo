# State Recovery Decomposition, 2019-2024

This analysis explains the project's existing state-recovery finding rather than introducing a new population definition. It decomposes each state's 2019-2024 U.S. nonresident enrollment change by student level, institutional control, and institution continuity, then measures how concentrated the directional institution movement is among the three largest contributors.

## National pattern

- **33 states/DC** were at or above their 2019 level in 2024; **18** remained below.
- Across the recovered group, **6** states/DC were undergraduate-led and **27** were graduate-led.
- By institutional control, recovered states/DC were led by private nonprofits in **16** cases, public institutions in **17**, and private for-profits in **0**.
- Summing all state changes reconciles to a national 2019-2024 change of **+71,079** students.

`level_driver` identifies the student-level component aligned with the state's net direction. Institution concentration is measured against gross movement in the state's net direction, so offsets from institutions moving the other way remain visible rather than being hidden inside the net value.

## Largest gains

| State | Net change | Undergraduate | Graduate | Control driver | Institution accounting | Top-three directional share | Leading institution |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Illinois (IL) | +14,464 | +3,359 | +11,105 | Private nonprofit-led | +14,464 | 33.7% | Illinois Institute of Technology (+2,161) |
| Texas (TX) | +14,279 | +3,862 | +10,417 | Public-led | +14,279 | 50.6% | University of North Texas (+4,906) |
| Indiana (IN) | +12,853 | -1,916 | +14,769 | Private nonprofit-led | +12,853 | 86.7% | Trine University-Regional/Non-Traditional Campuses (+8,893) |
| Florida (FL) | +11,980 | +8,369 | +3,611 | Public-led | +11,980 | 39.5% | Broward College (+3,363) |
| Missouri (MO) | +11,148 | -160 | +11,308 | Private nonprofit-led | +11,148 | 68.5% | Webster University (+3,351) |
| Georgia (GA) | +7,725 | +649 | +7,076 | Public-led | +7,725 | 71.3% | Georgia Institute of Technology-Main Campus (+4,550) |
| New York (NY) | +7,034 | -5,711 | +12,745 | Private nonprofit-led | +7,034 | 46.3% | New York University (+3,759) |
| Massachusetts (MA) | +6,809 | -806 | +7,615 | Private nonprofit-led | +6,809 | 55.9% | Northeastern University (+4,331) |

## Largest remaining shortfalls

| State | Net change | Undergraduate | Graduate | Control driver | Institution accounting | Top-three directional share | Leading institution |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| California (CA) | -33,282 | -37,674 | +4,392 | Public-led | -33,282 | 13.8% | Academy of Art University (-2,320) |
| Oregon (OR) | -4,265 | -4,164 | -101 | Public-led | -4,265 | 65.3% | Oregon State University (-1,295) |
| Kansas (KS) | -3,842 | -4,391 | +549 | Public-led | -3,842 | 93.2% | Fort Hays State University (-4,697) |
| Washington (WA) | -3,834 | -4,699 | +865 | Public-led | -3,834 | 35.8% | Washington State University (-977) |
| Idaho (ID) | -3,648 | -3,709 | +61 | Private nonprofit-led | -3,648 | 99.3% | Brigham Young University-Idaho (-3,764) |
| District of Columbia (DC) | -1,794 | -1,611 | -183 | Private nonprofit-led | -1,794 | 89.9% | American University (-982) |
| Iowa (IA) | -1,421 | -1,727 | +306 | Public-led | -1,421 | 64.3% | University of Iowa (-841) |
| Pennsylvania (PA) | -1,077 | -3,413 | +2,336 | Public-led | -1,077 | 60.9% | Pennsylvania State University-Main Campus (-2,872) |

## Interpretation

A state's net change can be concentrated even when its overall recovery status looks broad at first glance. The institution accounting therefore keeps continuing-institution change, newly present institutions, and institutions no longer in the state analytic universe separate. A UNITID entering or leaving a state's analytic universe can reflect reporting, eligibility, merger/reorganization, or location/classification change and should not automatically be interpreted as a campus opening or closure.

The student-level and institutional-control decompositions are arithmetic, not causal. They identify which components contribute most to the observed direction; they do not establish why those components changed. Control is measured at each endpoint, so changes can also reflect an institution changing control category between 2019 and 2024.

## Reproduction

```bash
python scripts/build_state_recovery_analysis.py
```

Canonical authorities are `data/processed/state_year.csv`, `data/processed/state_change_summary.csv`, and `data/processed/institution_year.csv`. The generated CSV is a downstream comparative analysis.
