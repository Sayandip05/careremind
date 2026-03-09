from app.languages.base_language import BaseLanguage


class Marathi(BaseLanguage):
    def get_language_code(self) -> str:
        return "mr"

    def get_language_name(self) -> str:
        return "Marathi"

    def get_greeting(self) -> str:
        return "नमस्कार"

    def get_reminder_template(self) -> str:
        return (
            "नमस्कार {patient_name},\n\n"
            "{clinic_name} ({doctor_name}) कडून स्मरणपत्र।\n"
            "तुमची पुढील भेट {date} रोजी आहे।\n\n"
            "{pre_visit_instructions}\n\n"
            "रिमाइंडर बंद करण्यासाठी STOP पाठवा।"
        )
