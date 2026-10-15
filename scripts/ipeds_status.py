"""Shared IPEDS status-code handling for source-data diagnostics.

The analytical pipeline retains official IPEDS values regardless of status code.
Category-countermovement diagnostics use a narrower rule because an imputed or
otherwise derived endpoint can make a two-year composition ratio look observed
when it is not.  Only reported values (R) and implied zeros (Z) receive a
countermovement ratio; every other official status stays visible but is marked
non-comparable for this diagnostic purpose.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence


STATUS_LABELS = {
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

DIAGNOSTIC_COMPARABLE_FLAGS = frozenset({"R", "Z"})


def status_pair(prior: Mapping[str, object], current: Mapping[str, object], field: str) -> str:
    """Return the compact endpoint status-code pair for one IPEDS field."""

    return f"{str(prior[f'X{field}']).strip()}→{str(current[f'X{field}']).strip()}"


def diagnostic_status_assessment(
    prior: Mapping[str, object],
    current: Mapping[str, object],
    fields: Sequence[str],
    *,
    prior_year: int,
    current_year: int,
) -> tuple[bool, str]:
    """Return whether endpoint statuses support a countermovement comparison.

    R and Z are retained as comparable source statuses.  Any other status code
    withholds the ratio while preserving the official value and arithmetic
    identity elsewhere in the diagnostic output.
    """

    issue_parts: list[str] = []
    for year, row in ((prior_year, prior), (current_year, current)):
        codes = Counter(
            str(row[f"X{field}"]).strip()
            for field in fields
            if str(row[f"X{field}"]).strip() not in DIAGNOSTIC_COMPARABLE_FLAGS
        )
        if codes:
            details = ", ".join(
                f"{code or '(blank)'} ({STATUS_LABELS.get(code, 'Unknown status')}) on {count} field(s)"
                for code, count in sorted(codes.items())
            )
            issue_parts.append(f"{year}: {details}")

    nr_pair = status_pair(prior, current, "EFNRALT")
    if issue_parts:
        return (
            False,
            "Countermovement comparison withheld because endpoint status codes are outside the diagnostic "
            f"R/Z comparability rule: {'; '.join(issue_parts)}. EFNRALT status {nr_pair}.",
        )

    return (
        True,
        "All endpoint total/category status codes are R (Reported) or Z (Implied zero); "
        f"EFNRALT status {nr_pair}.",
    )
