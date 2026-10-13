"""Build analysis-ready IPEDS aggregates and a reproducible QA record.

The public research brief focuses on institutions located in the 50 states and
District of Columbia. Raw IPEDS files also contain other U.S. jurisdictions;
those records are retained in the source files but are excluded from headline
national/state totals by an explicit geography rule below.
"""

from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from project_config import CORE_STATES, END_YEAR, START_YEAR

ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw" / "ipeds"
PROCESSED = ROOT / "data" / "processed"
QA_PATH = ROOT / "data" / "qa_report.json"

LEVELS = {
    "1": "all",
    "2": "undergraduate",
    "12": "graduate",
}

CONTROL_LABELS = {
    "1": "Public",
    "2": "Private nonprofit",
    "3": "Private for-profit",
}

IMPUTATION_LABELS = {
    "A": "Not applicable",
    "B": "Institution left item blank",
    "C": "Analyst corrected reported value",
    "D": "Do not know",
    "G": "Data generated from other data values",
    "H": "Value not derived - data not usable",
    "J": "Logical imputation",
    "K": "Ratio adjustment",
    "L": "Imputed using Group Median",
    "N": "Imputed using Nearest Neighbor",
    "P": "Imputed using Carry Forward",
    "R": "Reported",
    "Z": "Implied zero",
    "": "Blank/unknown",
}


def preferred_csv(year: int, table: str) -> Path:
    folder = RAW_ROOT / str(year) / table
    revised = sorted(folder.glob("*_rv.csv"))
    if revised:
        return revised[0]
    regular = sorted(folder.glob("*.csv"))
    if not regular:
        raise RuntimeError(f"No CSV source found in {folder}")
    return regular[0]


def read_csv(path: Path):
    payload = path.read_bytes()
    try:
        text = payload.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = payload.decode("cp1252")
        encoding = "cp1252"
    handle = io.StringIO(text, newline="")
    reader = csv.DictReader(handle)
    reader.source_encoding = encoding  # type: ignore[attr-defined]
    return handle, reader


def parse_int(value: str | None, *, field: str, context: str) -> int:
    if value is None:
        raise RuntimeError(f"Missing field {field} in {context}")
    value = value.strip()
    if value == "":
        raise RuntimeError(f"Blank numeric field {field} in {context}")
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Non-integer {field}={value!r} in {context}") from exc


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator * 100.0


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    institution_year: list[dict] = []
    qa_years: list[dict] = []
    excluded_geographies: Counter[str] = Counter()

    for year in range(START_YEAR, END_YEAR + 1):
        ef_table = f"EF{year}A"
        hd_table = f"HD{year}"
        ef_path = preferred_csv(year, ef_table)
        hd_path = preferred_csv(year, hd_table)

        directory: dict[str, dict[str, str]] = {}
        hd_handle, hd_reader = read_csv(hd_path)
        try:
            required_hd = {"UNITID", "INSTNM", "STABBR", "CONTROL", "DEGGRANT", "PSET4FLG"}
            missing_hd = required_hd.difference(hd_reader.fieldnames or [])
            if missing_hd:
                raise RuntimeError(f"Missing columns in {hd_path.name}: {sorted(missing_hd)}")
            for row in hd_reader:
                unitid = row["UNITID"].strip()
                if unitid in directory:
                    raise RuntimeError(f"Duplicate UNITID {unitid} in {hd_path.name}")
                directory[unitid] = {
                    "institution": row["INSTNM"].strip(),
                    "state": row["STABBR"].strip(),
                    "control": row["CONTROL"].strip(),
                    "degree_granting": row["DEGGRANT"].strip(),
                    "pset4flg": row["PSET4FLG"].strip(),
                }
        finally:
            hd_handle.close()

        by_unit: dict[str, dict[str, dict]] = defaultdict(dict)
        duplicate_rows = 0
        selected_rows = 0
        ef_handle, ef_reader = read_csv(ef_path)
        try:
            required = {"UNITID", "EFALEVEL", "EFTOTLT", "EFNRALT", "XEFTOTLT", "XEFNRALT"}
            missing = required.difference(ef_reader.fieldnames or [])
            if missing:
                raise RuntimeError(f"Missing columns in {ef_path.name}: {sorted(missing)}")

            for row in ef_reader:
                level_code = row["EFALEVEL"].strip()
                if level_code not in LEVELS:
                    continue
                selected_rows += 1
                unitid = row["UNITID"].strip()
                level = LEVELS[level_code]
                if level in by_unit[unitid]:
                    duplicate_rows += 1
                    continue

                total = parse_int(row["EFTOTLT"], field="EFTOTLT", context=f"{year}/{unitid}/{level}")
                nonresident = parse_int(row["EFNRALT"], field="EFNRALT", context=f"{year}/{unitid}/{level}")
                if total < 0 or nonresident < 0:
                    raise RuntimeError(f"Negative enrollment in {year}/{unitid}/{level}")
                if nonresident > total:
                    raise RuntimeError(
                        f"U.S. nonresident count exceeds total enrollment in {year}/{unitid}/{level}"
                    )

                by_unit[unitid][level] = {
                    "total": total,
                    "nonresident": nonresident,
                    "total_flag": row["XEFTOTLT"].strip(),
                    "nonresident_flag": row["XEFNRALT"].strip(),
                }
        finally:
            ef_handle.close()

        if duplicate_rows:
            raise RuntimeError(f"Found {duplicate_rows} duplicate selected rows in {ef_path.name}")

        missing_directory: list[str] = []
        level_counts = Counter()
        nonresident_flags = Counter()
        total_flags = Counter()
        core_institutions = 0
        excluded_universe = 0

        for unitid, levels in by_unit.items():
            if "all" not in levels:
                # Some institutions can have component rows without a usable all-student
                # row. They are not safe for the institution-year analytic unit.
                continue
            if unitid not in directory:
                missing_directory.append(unitid)
                continue

            state = directory[unitid]["state"]
            if state not in CORE_STATES:
                excluded_geographies[state or "(blank)"] += 1
                continue
            if directory[unitid]["degree_granting"] != "1" or directory[unitid]["pset4flg"] not in {"1", "3"}:
                excluded_universe += 1
                continue
            control = directory[unitid]["control"]
            if control not in CONTROL_LABELS:
                raise RuntimeError(f"Unexpected CONTROL={control!r} in {year}/{unitid}")

            core_institutions += 1
            all_row = levels["all"]
            undergraduate = levels.get("undergraduate")
            graduate = levels.get("graduate")
            for level in levels:
                level_counts[level] += 1
            nonresident_flags[all_row["nonresident_flag"]] += 1
            total_flags[all_row["total_flag"]] += 1

            institution_year.append(
                {
                    "year": year,
                    "unitid": unitid,
                    "institution": directory[unitid]["institution"],
                    "state": state,
                    "control": CONTROL_LABELS[control],
                    "total_enrollment": all_row["total"],
                    "nonresident_enrollment": all_row["nonresident"],
                    "nonresident_share_pct": round(pct(all_row["nonresident"], all_row["total"]) or 0.0, 4),
                    "undergraduate_total": "" if undergraduate is None else undergraduate["total"],
                    "undergraduate_nonresident": "" if undergraduate is None else undergraduate["nonresident"],
                    "graduate_total": "" if graduate is None else graduate["total"],
                    "graduate_nonresident": "" if graduate is None else graduate["nonresident"],
                    "nonresident_imputation_flag": all_row["nonresident_flag"],
                    "total_imputation_flag": all_row["total_flag"],
                    "source_enrollment_csv": ef_path.name,
                    "source_directory_csv": hd_path.name,
                }
            )

        if missing_directory:
            raise RuntimeError(
                f"{year}: {len(missing_directory)} selected UNITIDs missing from directory; "
                f"first={missing_directory[:5]}"
            )

        qa_years.append(
            {
                "year": year,
                "source_enrollment_csv": ef_path.name,
                "source_directory_csv": hd_path.name,
                "selected_level_rows": selected_rows,
                "institutions_in_analytic_universe": core_institutions,
                "excluded_in_50_states_dc_outside_degree_granting_first_look_universe": excluded_universe,
                "institutions_with_undergraduate_row": level_counts["undergraduate"],
                "institutions_with_graduate_row": level_counts["graduate"],
                "nonresident_flag_counts": dict(sorted(nonresident_flags.items())),
                "total_flag_counts": dict(sorted(total_flags.items())),
            }
        )

    # Aggregate state-year, control-year, and national-year metrics from the
    # normalized institution-year table.
    state_acc: dict[tuple[int, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    control_acc: dict[tuple[int, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    national_acc: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in institution_year:
        key = (row["year"], row["state"])
        control_key = (row["year"], row["control"])
        for field in (
            "total_enrollment",
            "nonresident_enrollment",
            "undergraduate_total",
            "undergraduate_nonresident",
            "graduate_total",
            "graduate_nonresident",
        ):
            value = row[field]
            if value != "":
                state_acc[key][field] += int(value)
                control_acc[control_key][field] += int(value)
                national_acc[row["year"]][field] += int(value)
        state_acc[key]["institution_count"] += 1
        control_acc[control_key]["institution_count"] += 1
        national_acc[row["year"]]["institution_count"] += 1

    state_rows: list[dict] = []
    for (year, state), values in sorted(state_acc.items()):
        state_rows.append(
            {
                "year": year,
                "state": state,
                "institution_count": values["institution_count"],
                "total_enrollment": values["total_enrollment"],
                "nonresident_enrollment": values["nonresident_enrollment"],
                "nonresident_share_pct": round(
                    pct(values["nonresident_enrollment"], values["total_enrollment"]) or 0.0, 4
                ),
                "undergraduate_total": values["undergraduate_total"],
                "undergraduate_nonresident": values["undergraduate_nonresident"],
                "graduate_total": values["graduate_total"],
                "graduate_nonresident": values["graduate_nonresident"],
            }
        )

    control_rows: list[dict] = []
    for (year, control), values in sorted(control_acc.items()):
        control_rows.append(
            {
                "year": year,
                "control": control,
                "institution_count": values["institution_count"],
                "total_enrollment": values["total_enrollment"],
                "nonresident_enrollment": values["nonresident_enrollment"],
                "nonresident_share_pct": round(
                    pct(values["nonresident_enrollment"], values["total_enrollment"]) or 0.0, 4
                ),
                "undergraduate_nonresident": values["undergraduate_nonresident"],
                "graduate_nonresident": values["graduate_nonresident"],
            }
        )

    national_rows: list[dict] = []
    previous_nr: int | None = None
    for year in range(START_YEAR, END_YEAR + 1):
        values = national_acc[year]
        nr = values["nonresident_enrollment"]
        yoy = None if previous_nr is None else pct(nr - previous_nr, previous_nr)
        national_rows.append(
            {
                "year": year,
                "institution_count": values["institution_count"],
                "total_enrollment": values["total_enrollment"],
                "nonresident_enrollment": nr,
                "nonresident_share_pct": round(pct(nr, values["total_enrollment"]) or 0.0, 4),
                "yoy_nonresident_pct": "" if yoy is None else round(yoy, 4),
                "undergraduate_total": values["undergraduate_total"],
                "undergraduate_nonresident": values["undergraduate_nonresident"],
                "graduate_total": values["graduate_total"],
                "graduate_nonresident": values["graduate_nonresident"],
            }
        )
        previous_nr = nr

    # Latest-year institutional detail is small enough to expose for transparent drill-down.
    latest_institutions = sorted(
        (row for row in institution_year if row["year"] == END_YEAR),
        key=lambda row: (-row["nonresident_enrollment"], row["institution"]),
    )

    write_csv(
        PROCESSED / "state_year.csv",
        state_rows,
        list(state_rows[0].keys()),
    )
    write_csv(
        PROCESSED / "national_year.csv",
        national_rows,
        list(national_rows[0].keys()),
    )
    write_csv(
        PROCESSED / "control_year.csv",
        control_rows,
        list(control_rows[0].keys()),
    )
    write_csv(
        PROCESSED / f"institutions_{END_YEAR}.csv",
        latest_institutions,
        list(latest_institutions[0].keys()),
    )

    # Keep the full institution-year table reproducible but out of version control;
    # it is used as an intermediate validation/analysis artifact.
    write_csv(
        PROCESSED / "institution_year.csv",
        institution_year,
        list(institution_year[0].keys()),
    )

    level_reconciliation = all(
        row["total_enrollment"] == row["undergraduate_total"] + row["graduate_total"]
        and row["nonresident_enrollment"]
        == row["undergraduate_nonresident"] + row["graduate_nonresident"]
        for row in national_rows
    )

    qa = {
        "analytic_universe": "Degree-granting institutions in the IPEDS First Look/Digest Title IV universe (PSET4FLG 1 or 3), located in the 50 states and District of Columbia",
        "years": qa_years,
        "institution_year_rows": len(institution_year),
        "state_year_rows": len(state_rows),
        "control_year_rows": len(control_rows),
        "excluded_jurisdiction_institution_year_counts": dict(sorted(excluded_geographies.items())),
        "imputation_flag_labels": IMPUTATION_LABELS,
        "checks": {
            "duplicate_selected_rows": "PASS",
            "directory_join_coverage": "PASS",
            "nonnegative_counts": "PASS",
            "nonresident_not_greater_than_total": "PASS",
            "all_years_present": "PASS" if len(national_rows) == END_YEAR - START_YEAR + 1 else "FAIL",
            "all_51_geographies_present_each_year": "PASS" if len(state_rows) == 51 * (END_YEAR - START_YEAR + 1) else "FAIL",
            "all_three_controls_present_each_year": "PASS" if len(control_rows) == 3 * (END_YEAR - START_YEAR + 1) else "FAIL",
            "undergraduate_plus_graduate_reconciles_to_total": "PASS" if level_reconciliation else "FAIL",
        },
    }
    QA_PATH.write_text(json.dumps(qa, indent=2), encoding="utf-8")

    print(f"Built {len(institution_year):,} institution-year rows")
    print(f"Built {len(state_rows):,} state-year rows")
    print(f"Built {len(control_rows):,} control-year rows")
    print(f"Built {len(national_rows):,} national-year rows")
    print(f"Wrote QA report to {QA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
