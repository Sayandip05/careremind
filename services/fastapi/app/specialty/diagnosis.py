from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class DiagnosisSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Diagnostic Lab"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please fast for 12 hours before a blood test (only water is allowed). Bring your doctor's prescription."

    def get_tone(self) -> str:
        return "precise"

    def get_default_followup_days(self) -> int:
        return 90
