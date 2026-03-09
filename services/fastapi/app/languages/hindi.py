from app.languages.base_language import BaseLanguage


class Hindi(BaseLanguage):
    def get_language_code(self) -> str:
        return "hi"

    def get_language_name(self) -> str:
        return "Hindi"

    def get_greeting(self) -> str:
        return "नमस्ते"

    def get_reminder_template(self) -> str:
        return (
            "नमस्ते {patient_name},\n\n"
            "{clinic_name} ({doctor_name}) की ओर से याद दिलाना।\n"
            "आपकी अगली अपॉइंटमेंट {date} को है।\n\n"
            "{pre_visit_instructions}\n\n"
            "रिमाइंडर बंद करने के लिए STOP लिखें।"
        )
