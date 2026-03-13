from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class DentalSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Dental"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please do not eat anything 2 hours before your appointment. Bring any previous dental X-rays if available."

    def get_tone(self) -> str:
        return "caring"

    def get_default_followup_days(self) -> int:
        return 180
