import re


def format_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91"):
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}"
