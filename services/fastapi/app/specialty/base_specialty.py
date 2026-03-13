"""
Base Specialty — Abstract class for all medical specialties.
Each specialty defines reminder timing, pre-visit instructions, tone, and follow-up gap.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta, timezone
from typing import Optional


class ReminderTiming:
    """A single reminder timing offset — days after the visit date."""

    def __init__(self, days_after: int, label: str = ""):
        self.days_after = days_after
        self.label = label or f"{days_after}-day"

    def get_scheduled_at(self, visit_date: date) -> datetime:
        """Calculate the actual datetime to send this reminder (9:00 AM IST)."""
        reminder_date = visit_date + timedelta(days=self.days_after)
        return datetime.combine(reminder_date, datetime.min.time().replace(hour=9))


class BaseSpecialty(ABC):
    """Abstract base for all medical specialties."""

    @abstractmethod
    def get_specialty_name(self) -> str:
        """Human-readable specialty name."""
        ...

    @abstractmethod
    def get_reminder_timing(self) -> list[ReminderTiming]:
        """List of reminder timings relative to the appointment date."""
        ...

    @abstractmethod
    def get_pre_visit_instructions(self) -> str:
        """Instructions for the patient before the visit."""
        ...

    @abstractmethod
    def get_tone(self) -> str:
        """Message tone: neutral, caring, calm, supportive, friendly, gentle, precise."""
        ...

    @abstractmethod
    def get_default_followup_days(self) -> int:
        """Default gap between visits in days (used when next_visit_date is missing)."""
        ...
