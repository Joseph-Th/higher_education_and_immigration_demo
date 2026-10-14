"""Capture a structural preflight for the available candidate-year IPEDS directory.

This is an online monitoring lane, not part of the reproducible offline build.
It is intentionally narrower than the annual schema audit: when the next-year
HD data and dictionary are available before Fall Enrollment, it checks the
directory-side fields and institution-universe continuity that can be reviewed
without pretending the analysis year is ready to advance.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

from openpyxl import load_workbook

from project_config import CORE_STATES, END_YEAR


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_ROOT = DATA / "raw" / "ipeds"
RELEASE_SNAPSHOT = DATA / "release_monitor_snapshot.json"
DEFAULT_OUTPUT = DATA / "candidate_directory_preflight.json"
USER_AGENT = "Mozilla/5.0 (compatible; ipeds-portfolio-directory-preflight/1.0)"

REQUIRED_FIELDS = ("UNITID", "INSTNM", "STABBR", "CONTROL", "DEGGRANT", "PSET4FLG")
CONTROL_LABELS = {"1": "Public", "2": "Private nonprofit", "3": "Private for-profit"}


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=90) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} for {url}")
            return response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc


def archive_member(payload: bytes, suffix: str) -> tuple[str, bytes]:
    try:
        archive = ZipFile(io.BytesIO(payload))
    except BadZipFile as exc:
        raise RuntimeError("Candidate directory response is not a valid ZIP archive") from exc
    members = [name for name in archive.namelist() if name.lower().endswith(suffix)]
    if len(members) != 1:
        raise RuntimeError(f"Expected exactly one {suffix} member; found {members}")
    name = members[0]
    return name, archive.read(name)


def decode_csv(payload: bytes) -> tuple[list[dict[str, str]], list[str], str]:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = payload.decode(encoding)
            reader = csv.DictReader(io.StringIO(text, newline=""))
            rows = list(reader)
            return rows, list(reader.fieldnames or []), encoding
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Candidate directory CSV is not decodable as UTF-8 or cp1252")


def current_directory() -> tuple[list[dict[str, str]], list[str], str, str]:
    folder = RAW_ROOT / str(END_YEAR) / f"HD{END_YEAR}"
    revised = sorted(folder.glob("*_rv.csv"))
    paths = revised or sorted(folder.glob("*.csv"))
    if not paths:
        raise RuntimeError(f"Current-year directory CSV is missing from {folder}")
    path = paths[0]
    payload = path.read_bytes()
    rows, fields, encoding = decode_csv(payload)
    return rows, fields, encoding, path.name


def dictionary_vars(payload: bytes) -> tuple[dict[str, str], int]:
    workbook = load_workbook(io.BytesIO(payload), read_only=True, data_only=True)
    names = {name.casefold(): name for name in workbook.sheetnames}
    if "varlist" not in names:
        raise RuntimeError(f"Candidate directory dictionary has no Varlist sheet: {workbook.sheetnames}")
    sheet = workbook[names["varlist"]]
    rows = sheet.iter_rows(values_only=True)
    header = next(rows)
    columns = {str(value).casefold(): index for index, value in enumerate(header)}
    for required in ("varname", "vartitle"):
        if required not in columns:
            raise RuntimeError(f"Candidate dictionary Varlist missing {required}")
    result: dict[str, str] = {}
    for row in rows:
        name = row[columns["varname"]]
        if name is None:
            continue
        title = row[columns["vartitle"]]
        result[str(name)] = "" if title is None else str(title)
    return result, len(result)


def eligible(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["STABBR"].strip() not in CORE_STATES:
            continue
        if row["DEGGRANT"].strip() != "1" or row["PSET4FLG"].strip() not in {"1", "3"}:
            continue
        unitid = row["UNITID"].strip()
        if unitid in result:
            raise RuntimeError(f"Duplicate eligible UNITID {unitid}")
        result[unitid] = row
    return result


def control_counts(rows: dict[str, dict[str, str]]) -> dict[str, int]:
    counts = Counter(row["CONTROL"].strip() for row in rows.values())
    unexpected = sorted(set(counts) - set(CONTROL_LABELS))
    if unexpected:
        raise RuntimeError(f"Unexpected CONTROL values in candidate directory: {unexpected}")
    return {CONTROL_LABELS[code]: counts.get(code, 0) for code in CONTROL_LABELS}


def load_release_snapshot() -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    snapshot = json.loads(RELEASE_SNAPSHOT.read_text(encoding="utf-8"))
    if int(snapshot.get("current_analysis_end_year", -1)) != END_YEAR:
        raise RuntimeError("Release-monitor current year does not match project END_YEAR")
    candidate = END_YEAR + 1
    if int(snapshot.get("candidate_next_year", -1)) != candidate:
        raise RuntimeError("Release-monitor candidate year does not match END_YEAR + 1")
    files = snapshot.get("files")
    if not isinstance(files, list):
        raise RuntimeError("Release-monitor files payload is invalid")
    by_name = {str(row.get("file", "")): row for row in files}
    required_names = {f"HD{candidate}.zip", f"HD{candidate}_Dict.zip"}
    if not required_names.issubset(by_name):
        raise RuntimeError("Release-monitor snapshot is missing candidate directory assets")
    if not all(bool(by_name[name].get("available")) for name in required_names):
        raise RuntimeError("Candidate directory preflight requires both HD data and dictionary to be available")
    return snapshot, by_name


def build_payload() -> dict[str, object]:
    release_snapshot, release_files = load_release_snapshot()
    candidate = END_YEAR + 1
    data_name = f"HD{candidate}.zip"
    dictionary_name = f"HD{candidate}_Dict.zip"
    data_url = str(release_files[data_name]["url"])
    dictionary_url = str(release_files[dictionary_name]["url"])

    data_archive = download(data_url)
    dictionary_archive = download(dictionary_url)
    data_member, data_csv = archive_member(data_archive, ".csv")
    dictionary_member, dictionary_xlsx = archive_member(dictionary_archive, ".xlsx")

    candidate_rows, candidate_fields, candidate_encoding = decode_csv(data_csv)
    current_rows, current_fields, current_encoding, current_csv = current_directory()
    dictionary, dictionary_field_count = dictionary_vars(dictionary_xlsx)

    missing_data_fields = [field for field in REQUIRED_FIELDS if field not in candidate_fields]
    missing_dictionary_fields = [field for field in REQUIRED_FIELDS if field not in dictionary]
    if missing_data_fields or missing_dictionary_fields:
        raise RuntimeError(
            "Candidate directory required fields are incomplete: "
            f"data={missing_data_fields}; dictionary={missing_dictionary_fields}"
        )

    ids = [row["UNITID"].strip() for row in candidate_rows]
    duplicate_unitids = len(ids) - len(set(ids))
    if duplicate_unitids:
        raise RuntimeError(f"Candidate directory contains {duplicate_unitids} duplicate UNITIDs")

    candidate_states = {row["STABBR"].strip() for row in candidate_rows if row["STABBR"].strip() in CORE_STATES}
    current_states = {row["STABBR"].strip() for row in current_rows if row["STABBR"].strip() in CORE_STATES}
    if candidate_states != CORE_STATES:
        raise RuntimeError(f"Candidate directory core-state coverage mismatch: {sorted(CORE_STATES - candidate_states)}")
    if current_states != CORE_STATES:
        raise RuntimeError("Current directory no longer covers all 50 states plus DC")

    candidate_eligible = eligible(candidate_rows)
    current_eligible = eligible(current_rows)
    shared = set(candidate_eligible) & set(current_eligible)
    entering = set(candidate_eligible) - set(current_eligible)
    leaving = set(current_eligible) - set(candidate_eligible)

    candidate_controls = control_counts(candidate_eligible)
    current_controls = control_counts(current_eligible)
    control_changes = sum(
        current_eligible[unitid]["CONTROL"].strip() != candidate_eligible[unitid]["CONTROL"].strip()
        for unitid in shared
    )
    state_changes = sum(
        current_eligible[unitid]["STABBR"].strip() != candidate_eligible[unitid]["STABBR"].strip()
        for unitid in shared
    )
    name_changes = sum(
        current_eligible[unitid]["INSTNM"].strip() != candidate_eligible[unitid]["INSTNM"].strip()
        for unitid in shared
    )

    removed_fields = sorted(set(current_fields) - set(candidate_fields))
    added_fields = sorted(set(candidate_fields) - set(current_fields))
    required_titles = {field: dictionary[field] for field in REQUIRED_FIELDS}

    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "current_analysis_end_year": END_YEAR,
        "candidate_next_year": candidate,
        "preflight_scope": "candidate institutional directory only; not Fall Enrollment",
        "status": "PASS",
        "year_advance_authorized": False,
        "authorization_boundary": (
            "Directory-side structural checks pass, but year advancement remains governed by the complete "
            "Fall Enrollment plus directory package and full schema review."
        ),
        "candidate_source": {
            "data_url": data_url,
            "data_archive_bytes": len(data_archive),
            "data_sha256": hashlib.sha256(data_archive).hexdigest(),
            "data_member": data_member,
            "data_encoding": candidate_encoding,
            "dictionary_url": dictionary_url,
            "dictionary_archive_bytes": len(dictionary_archive),
            "dictionary_sha256": hashlib.sha256(dictionary_archive).hexdigest(),
            "dictionary_member": dictionary_member,
        },
        "required_directory_fields": list(REQUIRED_FIELDS),
        "required_field_titles": required_titles,
        "missing_required_data_fields": missing_data_fields,
        "missing_required_dictionary_fields": missing_dictionary_fields,
        "candidate_directory_rows": len(candidate_rows),
        "candidate_field_count": len(candidate_fields),
        "candidate_core_states_dc_count": len(candidate_states),
        "candidate_duplicate_unitid_count": duplicate_unitids,
        "candidate_directory_eligible_rows": len(candidate_eligible),
        "candidate_control_counts": candidate_controls,
        "current_reference": {
            "year": END_YEAR,
            "directory_csv": current_csv,
            "encoding": current_encoding,
            "directory_rows": len(current_rows),
            "field_count": len(current_fields),
            "core_states_dc_count": len(current_states),
            "directory_eligible_rows": len(current_eligible),
            "control_counts": current_controls,
        },
        "schema_delta": {
            "field_count_change": len(candidate_fields) - len(current_fields),
            "removed_fields": removed_fields,
            "added_fields": added_fields,
            "required_fields_preserved": not missing_data_fields and not missing_dictionary_fields,
        },
        "eligible_universe_continuity": {
            "shared_unitids": len(shared),
            "entering_unitids": len(entering),
            "leaving_unitids": len(leaving),
            "net_change": len(candidate_eligible) - len(current_eligible),
            "shared_control_changes": control_changes,
            "shared_state_changes": state_changes,
            "shared_name_changes": name_changes,
        },
        "release_monitor_checked_at_utc": release_snapshot["checked_at_utc"],
        "release_monitor_decision": release_snapshot["release_decision"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-snapshot",
        type=Path,
        default=None,
        help=f"Optional output path. Recommended: {DEFAULT_OUTPUT.relative_to(ROOT)}",
    )
    args = parser.parse_args()

    try:
        payload = build_payload()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2))
    if args.write_snapshot:
        args.write_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.write_snapshot.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote candidate directory preflight to {args.write_snapshot}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
