"""
Date parser — handles common Indian date formats from Excel and OCR text.
Returns datetime.date (not datetime) since appointments are date-level.
"""

import re
from datetime import date, datetime
from typing import Optional

# Month name mappings (English + common abbreviations)
MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# Ordered by most common in Indian clinics
DATE_FORMATS = [
    "%d/%m/%Y",     # 15/03/2025
    "%d-%m-%Y",     # 15-03-2025
    "%d.%m.%Y",     # 15.03.2025
    "%d/%m/%y",     # 15/03/25
    "%d-%m-%y",     # 15-03-25
    "%Y-%m-%d",     # 2025-03-15 (ISO)
    "%d %b %Y",     # 15 Mar 2025
    "%d %B %Y",     # 15 March 2025
    "%b %d, %Y",    # Mar 15, 2025
    "%B %d, %Y",    # March 15, 2025
]


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse a date string into datetime.date.
    Handles common Indian formats, Excel serial numbers, and datetime objects.
    Returns None if parsing fails (instead of raising).
    """
    if not date_str:
        return None

    # Already a date or datetime object (from openpyxl)
    if isinstance(date_str, datetime):
        return date_str.date()
    if isinstance(date_str, date):
        return date_str

    text = str(date_str).strip()
    if not text:
        return None

    # Try standard formats first
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    # Try "1 Mar 2025" style with flexible spacing
    match = re.match(
        r"(\d{1,2})\s+([a-zA-Z]+)\s+(\d{2,4})", text
    )
    if match:
        day, month_str, year_str = match.groups()
        month = MONTH_MAP.get(month_str.lower())
        if month:
            year = int(year_str)
            if year < 100:
                year += 2000
            try:
                return date(year, month, int(day))
            except ValueError:
                pass

    # Excel serial number (e.g., 45701 = a date)
    try:
        serial = int(float(text))
        if 40000 < serial < 55000:  # Reasonable range: ~2009 to ~2050
            from datetime import timedelta
            excel_epoch = date(1899, 12, 30)
            return excel_epoch + timedelta(days=serial)
    except (ValueError, OverflowError):
        pass

    return None
