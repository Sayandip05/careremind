from app.languages.base_language import BaseLanguage


class Tamil(BaseLanguage):
    def get_language_code(self) -> str:
        return "ta"

    def get_language_name(self) -> str:
        return "Tamil"

    def get_greeting(self) -> str:
        return "வணக்கம்"

    def get_reminder_template(self) -> str:
        return (
            "வணக்கம் {patient_name},\n\n"
            "{clinic_name} ({doctor_name}) இலிருந்து நினைவூட்டல்.\n"
            "உங்கள் அடுத்த சந்திப்பு {date} அன்று.\n\n"
            "{pre_visit_instructions}\n\n"
            "நினைவூட்டல்களை நிறுத்த STOP என பதிலளிக்கவும்."
        )
