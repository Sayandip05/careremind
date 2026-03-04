from app.specialty.base_specialty import BaseSpecialty


class DentalSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [2, 0.083]

    def get_message_template(self):
        return "Your dental appointment is on {date}. Don't eat 2 hours before, bring X-rays if available."

    def get_tone(self):
        return "caring"
