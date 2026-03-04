from app.specialty.base_specialty import BaseSpecialty


class GeneralSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [1, 0]

    def get_message_template(self):
        return "Your appointment is on {date}. Please arrive 10 minutes early."

    def get_tone(self):
        return "neutral"
