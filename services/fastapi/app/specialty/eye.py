from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class EyeSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Ophthalmology"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Your eyes may be dilated during the checkup. Please bring someone who can drive you home. Bring your current glasses or lenses."

    def get_tone(self) -> str:
        return "calm"

    def get_default_followup_days(self) -> int:
        return 90
