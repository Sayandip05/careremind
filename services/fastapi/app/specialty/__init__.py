"""
Specialty registry — maps specialty names to their class instances.
"""

from app.specialty.base_specialty import BaseSpecialty
from app.specialty.general import GeneralSpecialty
from app.specialty.dental import DentalSpecialty
from app.specialty.eye import EyeSpecialty
from app.specialty.orthopedic import OrthopedicSpecialty
from app.specialty.pediatric import PediatricSpecialty
from app.specialty.skin import SkinSpecialty
from app.specialty.diagnosis import DiagnosisSpecialty

# Registry: lowercase name → specialty instance
_REGISTRY: dict[str, BaseSpecialty] = {
    "general": GeneralSpecialty(),
    "dental": DentalSpecialty(),
    "eye": EyeSpecialty(),
    "ophthalmology": EyeSpecialty(),
    "orthopedic": OrthopedicSpecialty(),
    "ortho": OrthopedicSpecialty(),
    "pediatric": PediatricSpecialty(),
    "child": PediatricSpecialty(),
    "skin": SkinSpecialty(),
    "dermatology": SkinSpecialty(),
    "diagnosis": DiagnosisSpecialty(),
    "diagnostic": DiagnosisSpecialty(),
    "lab": DiagnosisSpecialty(),
}

_DEFAULT = GeneralSpecialty()


def get_specialty(name: str | None) -> BaseSpecialty:
    """
    Get a specialty by name. Falls back to GeneralSpecialty if unknown.
    Case-insensitive matching with common aliases.
    """
    if not name:
        return _DEFAULT
    return _REGISTRY.get(name.strip().lower(), _DEFAULT)
