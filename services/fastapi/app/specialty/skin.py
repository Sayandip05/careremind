from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class SkinSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Dermatology"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_before=1, label="1-day reminder"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please avoid applying any creams, makeup, or ointments on the affected area before your appointment."

    def get_tone(self) -> str:
        return "gentle"

    def get_default_followup_days(self) -> int:
        return 14
