from app.specialty.base_specialty import BaseSpecialty


class DiagnosisSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [2, 0]

    def get_message_template(self):
        return "Your appointment is on {date}. Please bring previous reports and prescriptions."

    def get_tone(self):
        return "professional"
