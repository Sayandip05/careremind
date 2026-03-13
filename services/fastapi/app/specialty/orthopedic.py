from app.specialty.base_specialty import BaseSpecialty, ReminderTiming


class OrthopedicSpecialty(BaseSpecialty):
    def get_specialty_name(self) -> str:
        return "Orthopedic"

    def get_reminder_timing(self) -> list[ReminderTiming]:
        return [
            ReminderTiming(days_after=7, label="7-day follow-up"),
            ReminderTiming(days_after=30, label="30-day follow-up"),
        ]

    def get_pre_visit_instructions(self) -> str:
        return "Please wear comfortable, loose-fitting clothes. Bring any recent X-rays or MRI reports."

    def get_tone(self) -> str:
        return "supportive"

    def get_default_followup_days(self) -> int:
        return 45
