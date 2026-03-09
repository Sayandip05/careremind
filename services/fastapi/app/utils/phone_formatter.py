"""
Phone number formatter — normalizes Indian phone numbers.
Handles: +91XXXXXXXXXX, 91XXXXXXXXXX, 0XXXXXXXXXX, XXXXXXXXXX,
          +91-XXXXX-XXXXX, +91 XXXXX XXXXX, (91) XXXXXXXXXX, etc.
"""

import re
from typing import Optional


def normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize an Indian phone number to +91XXXXXXXXXX format.
    Returns None if the phone is invalid (not 10 digits after stripping).
    """
    if not phone:
        return None

    # Strip everything that isn't a digit
    digits = re.sub(r"\D", "", phone.strip())

    # Remove leading country code
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("091") and len(digits) == 13:
        digits = digits[3:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]

    # Validate: must be exactly 10 digits, starting with 6-9 (Indian mobile)
    if len(digits) != 10:
        return None

    if digits[0] not in "6789":
        return None

    return f"+91{digits}"


def is_valid_phone(phone: str) -> bool:
    """Check if a phone string can be normalized to a valid Indian number."""
    return normalize_phone(phone) is not None
