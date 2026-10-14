# National Population Trend Comparison

## Decision boundary

These are **separate population measures, not one combined enrollment series**. IPEDS U.S. nonresident, immigrant-origin, and undocumented-student estimates use different definitions and data systems. Same-year values are shown only for scale context and **must not be added, subtracted, or interpreted as mutually exclusive categories**.

## What the compatible segments show

- **IPEDS U.S. nonresident:** 973,058 in 2019 to 1,044,137 in 2024, +71,079 (7.3%). This is the project's institution-reported annual series.
- **Immigrant-origin students:** approximately 2.9 million in 2000 to 5,991,000 in 2023. The source reports a **107%** increase and a rise from about 20% to 32% of higher-education enrollment. Nonimmigrant international students are excluded from this immigrant-origin estimate.
- **Undocumented students, historical segment:** 427,000 in 2019 to more than 408,000 in 2021. The source reports a **4.2% decline**; rounded headline counts do not exactly reproduce that percentage.
- **Undocumented students, current segment:** 510,000 in 2023 to 525,000 in 2024, +15,000 (2.9%). The 2024 estimate represents 2.4% of postsecondary students in the current source.

The project does **not** calculate a 2021-2023 undocumented trend. The historical and current estimates are retained as separate source segments until the underlying modeling vintages are shown to be equivalent enough for a continuous series.

## 2023 scale context: not addable

| Population measure | 2023 national estimate | Interpretation |
| --- | ---: | --- |
| IPEDS U.S. nonresident | 1,014,598 | Temporary-status institution-reported category |
| Immigrant-origin | 5,991,000 | Domestic first- and second-generation survey estimate; excludes nonimmigrant international students |
| Undocumented higher education | 510,000 | Modeled legal-status estimate; conceptually part of the broader first-generation immigrant-origin population |

These values answer different questions. Their relative size can be described, but they are not components of a single total.

## Comparison rules

1. **IPEDS vs immigrant-origin:** not directly comparable. The immigrant-origin measure focuses on domestic first- and second-generation students and excludes nonimmigrant international students, while IPEDS U.S. nonresident captures temporary-status noncitizens under the federal reporting definition.
2. **IPEDS vs undocumented:** not directly comparable. IPEDS U.S. nonresident explicitly does not identify undocumented or DACA students as that category.
3. **Immigrant-origin vs undocumented:** the undocumented population is conceptually included within the broader first-generation immigrant-origin framework, but the estimates come from different surveys/models. Do not subtract one from the other or infer a share without aligned universes and denominators.
4. **State comparison remains held:** IPEDS geography is institution location, while CPS/ACS estimates generally follow student residence. A state-level comparison needs an explicit geography crosswalk rather than assuming equivalence.

## Source authority

- IPEDS values: `data/processed/national_year.csv` generated from official NCES complete-data files.
- Immigrant-origin observations: Presidents' Alliance / Migration Policy Institute 2026 report using the 2000 and 2023 CPS October Supplements.
- Historical undocumented observations: American Immigration Council 2023 fact sheet using 2019 and 2021 ACS estimates.
- Current undocumented observations: American Immigration Council 2026 fact sheet using 2023 and 2024 ACS estimates.
- Structured external observations and provenance: `data/population_trend_reference.csv`.
