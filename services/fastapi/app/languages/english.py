from app.languages.base_language import BaseLanguage


class English(BaseLanguage):
    def get_language_code(self) -> str:
        return "en"

    def get_language_name(self) -> str:
        return "English"

    def get_greeting(self) -> str:
        return "Hello"

    def get_reminder_template(self) -> str:
        return (
            "Hello {patient_name},\n\n"
            "This is a reminder from {clinic_name} ({doctor_name}).\n"
            "Your appointment is on {date}.\n\n"
            "{pre_visit_instructions}\n\n"
            "Please reply STOP to opt out of reminders."
        )
