from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class PediatricSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Pediatric"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_before=1, label="1-day reminder"),
            ReminderTiming(hours_before=2, label="2-hour reminder"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please bring your child's vaccination card and any previous medical records."

    def get_tone(self) -> str:
        return "friendly"

    def get_default_followup_days(self) -> int:
        return 30
