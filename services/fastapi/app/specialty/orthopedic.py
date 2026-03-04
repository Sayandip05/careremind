from app.specialty.base_specialty import BaseSpecialty


class OrthopedicSpecialty(BaseSpecialty):
    def get_reminder_timing(self):
        return [3, 1]

    def get_message_template(self):
        return (
            "Your orthopedic appointment is on {date}. Please bring MRI/X-ray reports."
        )

    def get_tone(self):
        return "professional"
