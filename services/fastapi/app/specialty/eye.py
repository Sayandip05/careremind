from app.specialty.base_specialty import BaseSpecialty


class EyeSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [1, 0.125]

    def get_message_template(self):
        return "Your eye appointment is on {date}. Arrange transport as vision may be blurred after."

    def get_tone(self):
        return "caring"
