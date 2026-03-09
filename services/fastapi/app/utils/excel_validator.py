"""
Excel column validator — fuzzy-matches messy spreadsheet headers
to the canonical fields CareRemind needs.
"""

import re
from typing import Optional

# Each canonical field → list of patterns that match it (case-insensitive)
COLUMN_PATTERNS: dict[str, list[str]] = {
    "name": [
        r"name", r"patient", r"patient.?name", r"full.?name",
        r"nm", r"pt.?name",
    ],
    "phone": [
        r"phone", r"mobile", r"contact", r"mob", r"cell",
        r"phone.?no", r"mobile.?no", r"contact.?no",
        r"ph.?no", r"mob.?no", r"number", r"whatsapp",
    ],
    "visit_date": [
        r"visit.?date", r"last.?visit", r"date.?of.?visit",
        r"consultation.?date", r"seen.?on", r"visit",
        r"date",  # generic "Date" column — assumed to be visit date
    ],
    "next_visit_date": [
        r"next.?visit", r"follow.?up", r"return.?date",
        r"next.?appointment", r"next.?date", r"revisit",
        r"follow.?up.?date", r"nxt.?visit",
    ],
}


def match_columns(headers: list[str]) -> dict[str, Optional[int]]:
    """
    Takes a list of raw column headers from an Excel sheet.
    Returns a dict mapping canonical field names to column indices.

    Example:
        headers = ["Patient Name", "Contact No", "Next Visit Date"]
        → {"name": 0, "phone": 1, "visit_date": None, "next_visit_date": 2}
    """
    mapping: dict[str, Optional[int]] = {
        field: None for field in COLUMN_PATTERNS
    }

    for idx, raw_header in enumerate(headers):
        if not raw_header:
            continue
        cleaned = str(raw_header).strip().lower()

        for field, patterns in COLUMN_PATTERNS.items():
            if mapping[field] is not None:
                continue  # Already matched — don't override
            for pattern in patterns:
                if re.search(pattern, cleaned):
                    mapping[field] = idx
                    break

    return mapping


def validate_mapping(mapping: dict[str, Optional[int]]) -> tuple[bool, list[str]]:
    """
    Check if the minimum required columns were found.
    Required: name + phone. Optional: visit_date, next_visit_date.
    Returns (is_valid, list_of_missing_required_fields).
    """
    required = ["name", "phone"]
    missing = [f for f in required if mapping.get(f) is None]
    return len(missing) == 0, missing
