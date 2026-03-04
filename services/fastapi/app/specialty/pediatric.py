from app.specialty.base_specialty import BaseSpecialty


class PediatricSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [2, 1]

    def get_message_template(self):
        return "Your child's appointment is on {date}. We look forward to seeing you!"

    def get_tone(self):
        return "gentle"
