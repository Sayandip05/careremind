"""
Specialty registry — maps specialty names to their class instances.
Supports any free-text custom specialty via CustomSpecialty fallback.
"""

from app.specialty.base_specialty import BaseSpecialty
from app.specialty.general import GeneralSpecialty
from app.specialty.dental import DentalSpecialty
from app.specialty.eye import EyeSpecialty
from app.specialty.orthopedic import OrthopedicSpecialty
from app.specialty.pediatric import PediatricSpecialty
from app.specialty.skin import SkinSpecialty
from app.specialty.diagnosis import DiagnosisSpecialty
from app.specialty.custom import CustomSpecialty

# ── Known specialty registry ─────────────────────────────────
# Lowercase name → specialty instance
_REGISTRY: dict[str, BaseSpecialty] = {
    # General
    "general": GeneralSpecialty(),
    "general medicine": GeneralSpecialty(),
    "gp": GeneralSpecialty(),
    # Dental
    "dental": DentalSpecialty(),
    "dentist": DentalSpecialty(),
    # Eye
    "eye": EyeSpecialty(),
    "ophthalmology": EyeSpecialty(),
    "optometry": EyeSpecialty(),
    # Orthopedic
    "orthopedic": OrthopedicSpecialty(),
    "ortho": OrthopedicSpecialty(),
    "orthopedics": OrthopedicSpecialty(),
    "bone": OrthopedicSpecialty(),
    # Pediatric
    "pediatric": PediatricSpecialty(),
    "paediatric": PediatricSpecialty(),
    "child": PediatricSpecialty(),
    "children": PediatricSpecialty(),
    # Skin
    "skin": SkinSpecialty(),
    "dermatology": SkinSpecialty(),
    "dermatologist": SkinSpecialty(),
    # Diagnosis / Lab
    "diagnosis": DiagnosisSpecialty(),
    "diagnostic": DiagnosisSpecialty(),
    "lab": DiagnosisSpecialty(),
    "pathology": DiagnosisSpecialty(),
}

_DEFAULT = GeneralSpecialty()


def get_specialty(name: str | None) -> BaseSpecialty:
    """
    Get a specialty by name (case-insensitive).

    - If name matches a known entry → return that specialty class.
    - If name is a non-empty unknown string (e.g. "Psychiatrist") →
      return a CustomSpecialty that uses that name in message context.
    - If name is empty or None → return GeneralSpecialty (default).
    """
    if not name:
        return _DEFAULT

    key = name.strip().lower()
    if key in _REGISTRY:
        return _REGISTRY[key]

    # Unknown specialty: preserve the doctor's actual specialty name
    # instead of silently falling back to "General Medicine"
    return CustomSpecialty(name)


def list_known_specialties() -> list[str]:
    """Returns all known specialty display names (for API docs / frontend dropdowns)."""
    seen = set()
    names = []
    for sp in _REGISTRY.values():
        label = sp.get_specialty_name()
        if label not in seen:
            seen.add(label)
            names.append(label)
    names.append("Other")  # Always include Other at the end
    return names
