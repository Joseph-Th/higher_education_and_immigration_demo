# Population and Source Crosswalk

This crosswalk prevents a common analytical error in higher-education immigration research: treating datasets with similar labels as if they measure the same population. The structured authority is `data/population_crosswalk.csv`; this document is generated from it.

## Decision rule

A source can be compared directly with the project series only when population definition, reference period, unit of analysis, geography, and denominator are compatible. Otherwise it is contextual evidence, a separate companion series, or a documented data need.

| Population | Measurement | Current vintage | Best use | Project status |
| --- | --- | --- | --- | --- |
| [IPEDS U.S. nonresident](https://nces.ed.gov/ipeds/report-your-data/race-ethnicity-definitions/) | Institution-reported administrative count | Fall 2024 provisional | Annual institution/state/national enrollment monitoring | Primary analytic measure |
| [Immigrant-origin students](https://www.higheredimmigrationportal.org/research/securing-americas-talent-pipeline/) | Survey estimate | 2023 CPS used by 2026 report | Measure domestic immigrant-origin participation in higher education | Contextual comparison only |
| [International students](https://www.higheredimmigrationportal.org/methodology/) | Administrative SEVIS record count | October 2025 Portal figures | Current international-student monitoring | Companion source for future comparison |
| [Undocumented students in higher education](https://www.higheredimmigrationportal.org/research/undocumented-students-in-u-s-higher-education-2/) | Modeled survey estimate | 2026 fact sheet; report-specific methodology controls exact vintage | Estimate the scale and composition of undocumented college enrollment | Companion source for future comparison |
| [Undocumented high school graduates](https://www.higheredimmigrationportal.org/research/a-generation-threatened-undocumented-high-school-students-graduate-amidst-uncertain-national-climate/) | Modeled pipeline estimate | 2019-early 2023 pooled ACS used by 2026 report | Assess the potential higher-education access pipeline | Research-agenda companion source |
| [Refugee/asylee students](https://www.higheredimmigrationportal.org/research/securing-americas-talent-pipeline/) | Population embedded within broader immigrant-origin measures | 2023 CPS used by 2026 report | Identify a documented measurement gap before making refugee-specific claims | Explicit measurement gap |

## Population notes

### IPEDS U.S. nonresident

- **Primary source:** NCES IPEDS Fall Enrollment
- **Unit of analysis:** Student enrollment at reporting institutions
- **Included:** Students who are not U.S. citizens or nationals and are in the United States on a visa or temporary basis without the right to remain indefinitely
- **Excluded / not identified:** DACA recipients, undocumented students, and other eligible noncitizens are not reported in this category
- **Geography:** Institution location in 50 states + DC
- **Comparison warning:** Do not treat this as a count of all international, immigrant-origin, undocumented, refugee, or foreign-born students
- **Source checked:** 2026-10-13

### Immigrant-origin students

- **Primary source:** Presidents' Alliance / Migration Policy Institute using U.S. Census Bureau CPS October Supplement
- **Unit of analysis:** Enrolled adults age 18-54 with at least a high school diploma or equivalent
- **Included:** First-generation immigrants plus second-generation immigrants; first generation includes naturalized citizens, permanent residents, refugees, asylees/asylum seekers, TPS recipients, undocumented people, and other domestic immigrant residents
- **Excluded / not identified:** International students in the U.S. on nonimmigrant student visas for temporary study are excluded from the first-generation immigrant estimate
- **Geography:** National and state residence where supported
- **Comparison warning:** This is a household-survey population estimate with a broader concept than IPEDS U.S. nonresident; the two series should not be added or substituted
- **Source checked:** 2026-10-13

### International students

- **Primary source:** U.S. Department of Homeland Security SEVIS Data Mapping Tool via Higher Ed Immigration Portal
- **Unit of analysis:** SEVIS records at certified postsecondary institutions
- **Included:** Associates, bachelors, masters, and doctorate level international-student records at SEVIS-certified institutions
- **Excluded / not identified:** Portal totals exclude vocational programs, primary/secondary school, flight school, and language training
- **Geography:** Institution/state/national views where SEVIS supports them
- **Comparison warning:** SEVIS, Open Doors, and IPEDS use different timing, coverage, and reporting concepts; counts are not directly interchangeable
- **Source checked:** 2026-10-13

### Undocumented students in higher education

- **Primary source:** Presidents' Alliance / American Immigration Council using ACS microdata
- **Unit of analysis:** Estimated enrolled undocumented students
- **Included:** ACS microdata are modeled to identify people likely to be undocumented and enrolled in postsecondary education; DACA-eligible students are estimated as a subset
- **Excluded / not identified:** Potential international students are excluded using demographic, school-attendance, duration-of-stay, and work criteria
- **Geography:** National and state estimates where published
- **Comparison warning:** This is an estimated legal-status population, not an observed administrative category; do not compare one-for-one with IPEDS U.S. nonresident counts
- **Source checked:** 2026-10-13

### Undocumented high school graduates

- **Primary source:** Presidents' Alliance / Migration Policy Institute using ACS plus NCES graduation rates
- **Unit of analysis:** Estimated undocumented youth reaching and completing high school
- **Included:** Undocumented high-school students under age 22 are estimated from ACS; differential graduation rates are then applied to estimate annual graduates
- **Excluded / not identified:** This is not a cohort linkage to students later observed in higher education
- **Geography:** National estimate with supporting state/race/ethnicity inputs
- **Comparison warning:** Do not interpret the annual graduate estimate as a transition rate into college or as the same population observed in higher-education enrollment data
- **Source checked:** 2026-10-13

### Refugee/asylee students

- **Primary source:** Presidents' Alliance / Migration Policy Institute immigrant-origin framework
- **Unit of analysis:** First-generation immigrant students
- **Included:** The first-generation immigrant category explicitly includes resettled refugees, asylees, and asylum seekers among other domestic immigrant groups
- **Excluded / not identified:** The current project does not separately identify refugee/asylee students, and IPEDS U.S. nonresident is not a refugee-status measure
- **Geography:** National/state only when a population-specific source permits
- **Comparison warning:** A refugee/asylee estimate requires a source designed to identify that status; neither the current IPEDS series nor the aggregate immigrant-origin total isolates it
- **Source checked:** 2026-10-13

## Implication for this project

The current longitudinal analysis intentionally stays with IPEDS U.S. nonresident enrollment because that measure is institution-reported, annual, and available consistently across the full period. The crosswalk identifies where a separate companion analysis would require CPS, ACS-derived estimates, SEVIS, or another population-specific source rather than relabeling the IPEDS series.
