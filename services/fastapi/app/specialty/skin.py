from app.specialty.base_specialty import BaseSpecialty


class SkinSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [3, 1]

    def get_message_template(self):
        return "Your skin checkup is on {date}. Remember to avoid sun exposure 24 hours before visit."

    def get_tone(self):
        return "friendly"
