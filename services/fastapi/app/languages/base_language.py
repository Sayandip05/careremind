"""
Base Language — Abstract class for all supported languages.
Each language provides reminder message templates with placeholders.
"""

from abc import ABC, abstractmethod
from datetime import date


class BaseLanguage(ABC):
    """Abstract base for all supported languages."""

    @abstractmethod
    def get_language_code(self) -> str:
        """ISO language code (e.g., 'en', 'hi')."""
        ...

    @abstractmethod
    def get_language_name(self) -> str:
        """Human-readable name."""
        ...

    @abstractmethod
    def get_greeting(self) -> str:
        """Greeting word used at the start of messages."""
        ...

    @abstractmethod
    def get_reminder_template(self) -> str:
        """
        Reminder message template with placeholders:
        {patient_name}, {doctor_name}, {clinic_name},
        {date}, {pre_visit_instructions}
        """
        ...

    def format_date(self, d: date) -> str:
        """Format a date for display. Override for locale-specific formatting."""
        return d.strftime("%d/%m/%Y")
