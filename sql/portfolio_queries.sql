-- QUERY: Q01 | National year-over-year change | CTE, LAG window function, CASE, arithmetic
WITH ordered AS (
    SELECT
        year,
        nonresident_enrollment,
        LAG(nonresident_enrollment) OVER (ORDER BY year) AS prior_nonresident
    FROM national_year
)
SELECT
    year,
    nonresident_enrollment,
    prior_nonresident,
    CASE
        WHEN prior_nonresident IS NULL THEN NULL
        ELSE nonresident_enrollment - prior_nonresident
    END AS annual_change,
    CASE
        WHEN prior_nonresident IS NULL THEN NULL
        ELSE ROUND(
            100.0 * (nonresident_enrollment - prior_nonresident) / prior_nonresident,
            2
        )
    END AS annual_change_pct
FROM ordered
ORDER BY year;

-- QUERY: Q02 | State recovery from 2019 to 2024 | CTE, conditional aggregation, CASE, RANK
WITH endpoints AS (
    SELECT
        state,
        MAX(CASE WHEN year = 2019 THEN nonresident_enrollment END) AS nonresident_2019,
        MAX(CASE WHEN year = 2024 THEN nonresident_enrollment END) AS nonresident_2024
    FROM state_year
    WHERE year IN (2019, 2024)
    GROUP BY state
),
ranked AS (
    SELECT
        state,
        nonresident_2019,
        nonresident_2024,
        nonresident_2024 - nonresident_2019 AS change_since_2019,
        CASE
            WHEN nonresident_2024 >= nonresident_2019 THEN 'AT_OR_ABOVE_2019'
            ELSE 'BELOW_2019'
        END AS recovery_status,
        RANK() OVER (
            ORDER BY (nonresident_2024 - nonresident_2019) DESC
        ) AS recovery_rank
    FROM endpoints
)
SELECT
    state,
    nonresident_2019,
    nonresident_2024,
    change_since_2019,
    recovery_status,
    recovery_rank
FROM ranked
ORDER BY recovery_rank, state;

-- QUERY: Q03 | Institutional-control decade change | CTE, conditional aggregation, ROUND, RANK
WITH endpoints AS (
    SELECT
        control,
        MAX(CASE WHEN year = 2015 THEN nonresident_enrollment END) AS nonresident_2015,
        MAX(CASE WHEN year = 2024 THEN nonresident_enrollment END) AS nonresident_2024
    FROM control_year
    WHERE year IN (2015, 2024)
    GROUP BY control
)
SELECT
    control,
    nonresident_2015,
    nonresident_2024,
    nonresident_2024 - nonresident_2015 AS decade_change,
    ROUND(
        100.0 * (nonresident_2024 - nonresident_2015) / nonresident_2015,
        2
    ) AS decade_change_pct,
    RANK() OVER (
        ORDER BY (nonresident_2024 - nonresident_2015) DESC
    ) AS decade_change_rank
FROM endpoints
ORDER BY decade_change_rank, control;

-- QUERY: Q04 | Largest 2024 institutions and national share | JOIN, ROW_NUMBER, cumulative SUM window
WITH ranked AS (
    SELECT
        i.unitid,
        i.institution,
        i.state,
        i.control,
        i.nonresident_enrollment,
        ROUND(
            100.0 * i.nonresident_enrollment / n.nonresident_enrollment,
            2
        ) AS national_share_pct,
        ROW_NUMBER() OVER (
            ORDER BY i.nonresident_enrollment DESC, i.unitid
        ) AS institution_rank,
        SUM(i.nonresident_enrollment) OVER (
            ORDER BY i.nonresident_enrollment DESC, i.unitid
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_nonresident
    FROM institutions_latest AS i
    JOIN national_year AS n
      ON n.year = i.year
)
SELECT
    unitid,
    institution,
    state,
    control,
    nonresident_enrollment,
    national_share_pct,
    institution_rank,
    cumulative_nonresident
FROM ranked
WHERE institution_rank <= 20
ORDER BY institution_rank;

-- QUERY: Q05 | Institution-universe change accounting | CTE, CASE classification, GROUP BY, SUM window
WITH classified AS (
    SELECT
        CASE
            WHEN status LIKE 'Continuing%' THEN 'Continuing institutions'
            ELSE 'Universe entry/exit'
        END AS movement_group,
        absolute_change
    FROM institution_change
),
grouped AS (
    SELECT
        movement_group,
        COUNT(*) AS institution_records,
        SUM(absolute_change) AS net_change
    FROM classified
    GROUP BY movement_group
)
SELECT
    movement_group,
    institution_records,
    net_change,
    SUM(net_change) OVER () AS national_net_change
FROM grouped
ORDER BY CASE movement_group WHEN 'Continuing institutions' THEN 1 ELSE 2 END;

-- QUERY: Q06 | State totals reconcile to national totals | CTE, GROUP BY, JOIN, reconciliation deltas
WITH state_totals AS (
    SELECT
        year,
        SUM(nonresident_enrollment) AS state_nonresident,
        SUM(total_enrollment) AS state_total
    FROM state_year
    GROUP BY year
)
SELECT
    n.year,
    n.nonresident_enrollment AS national_nonresident,
    s.state_nonresident,
    s.state_nonresident - n.nonresident_enrollment AS nonresident_delta,
    n.total_enrollment AS national_total,
    s.state_total,
    s.state_total - n.total_enrollment AS total_delta
FROM national_year AS n
JOIN state_totals AS s
  ON s.year = n.year
ORDER BY n.year;
