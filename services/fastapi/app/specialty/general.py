from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class GeneralSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "General Medicine"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please bring your previous prescriptions and any recent test reports."

    def get_tone(self) -> str:
        return "neutral"

    def get_default_followup_days(self) -> int:
        return 30
