"""
Custom Specialty — Handles any free-text specialty name that doesn't match
the built-in registry. Falls back to general reminder timings / tone but
uses the doctor's actual specialty name in message context.
"""

from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class CustomSpecialty(BaseSpecialty):
    """
    Flexible specialty for any type of doctor not in the registry.
    Accepts any free-text string (e.g. "Psychiatrist", "Pulmonologist")
    and uses it to provide context to the AI message generator.
    """

    def __init__(self, name: str):
        self._name = name.strip().title()

    def get_specialty_name(self) -> str:
        return self._name

    def get_reminder_timing(self) -> list[ReminderTiming]:
        # Default general follow-up schedule
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return (
            f"Please bring any relevant reports and prescriptions to your "
            f"{self._name} appointment."
        )

    def get_tone(self) -> str:
        return "caring"

    def get_default_followup_days(self) -> int:
        return 30
