"""Download the IPEDS source files used by this portfolio project.

The script intentionally uses only the Python standard library. It downloads
official NCES ZIP archives, validates and extracts them, and writes a small
provenance manifest containing hashes and retrieval metadata.
"""

from __future__ import annotations

import csv
import hashlib
import io
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile


START_YEAR = 2015
END_YEAR = 2024
ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw" / "ipeds"
MANIFEST_PATH = ROOT / "data" / "source_manifest.csv"

HISTORICAL_BASE = "https://nces.ed.gov/ipeds/datacenter/data"
CURRENT_BASE = "https://nces.ed.gov/ipeds/complete-data-files"

USER_AGENT = (
    "Mozilla/5.0 (compatible; immigration-education-demonstration/1.0; "
    "+https://nces.ed.gov/ipeds/)"
)


def table_names(year: int) -> tuple[str, str]:
    return f"EF{year}A", f"HD{year}"


def source_url(table: str, year: int, *, dictionary: bool) -> str:
    # NCES moved the current complete-data files to a new endpoint. Historical
    # files remain on the Data Center endpoint.
    base = CURRENT_BASE if year >= 2024 else HISTORICAL_BASE
    suffix = "_Dict.zip" if dictionary else ".zip"
    return f"{base}/{table}{suffix}"


def download(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=90) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} for {url}")
            return response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc


def safe_extract(zip_bytes: bytes, destination: Path) -> list[str]:
    try:
        archive = ZipFile(io.BytesIO(zip_bytes))
    except BadZipFile as exc:
        raise RuntimeError("Downloaded response is not a valid ZIP archive") from exc

    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    root = destination.resolve()

    for member in archive.infolist():
        member_path = (destination / member.filename).resolve()
        if os.path.commonpath([root, member_path]) != str(root):
            raise RuntimeError(f"Unsafe ZIP member path: {member.filename}")
        archive.extract(member, destination)
        if not member.is_dir():
            extracted.append(member.filename)

    return sorted(extracted)


def main() -> int:
    rows: list[dict[str, str | int]] = []
    RAW_ROOT.mkdir(parents=True, exist_ok=True)

    for year in range(START_YEAR, END_YEAR + 1):
        for table in table_names(year):
            for kind, is_dictionary in (("data", False), ("dictionary", True)):
                url = source_url(table, year, dictionary=is_dictionary)
                label = f"{table}{'_Dict' if is_dictionary else ''}"
                destination = RAW_ROOT / str(year) / label
                print(f"Downloading {label}: {url}")
                payload = download(url)
                digest = hashlib.sha256(payload).hexdigest()

                # Extract into a temporary sibling directory first, then replace
                # the destination only after successful ZIP validation/extraction.
                destination.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(
                    dir=destination.parent, prefix=f".{label}."
                ) as temp_dir:
                    temp_path = Path(temp_dir)
                    extracted = safe_extract(payload, temp_path)
                    if destination.exists():
                        for child in destination.rglob("*"):
                            if child.is_file():
                                child.unlink()
                        for child in sorted(destination.rglob("*"), reverse=True):
                            if child.is_dir():
                                child.rmdir()
                        destination.rmdir()
                    temp_path.rename(destination)

                rows.append(
                    {
                        "year": year,
                        "table": table,
                        "source_type": kind,
                        "url": url,
                        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                        "archive_bytes": len(payload),
                        "sha256": digest,
                        "extracted_files": "|".join(extracted),
                    }
                )

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "year",
                "table",
                "source_type",
                "url",
                "retrieved_utc",
                "archive_bytes",
                "sha256",
                "extracted_files",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} source records to {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

