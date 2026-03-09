from app.languages.base_language import BaseLanguage


class Bengali(BaseLanguage):
    def get_language_code(self) -> str:
        return "bn"

    def get_language_name(self) -> str:
        return "Bengali"

    def get_greeting(self) -> str:
        return "নমস্কার"

    def get_reminder_template(self) -> str:
        return (
            "নমস্কার {patient_name},\n\n"
            "{clinic_name} ({doctor_name}) থেকে মনে করানো হচ্ছে।\n"
            "আপনার পরবর্তী অ্যাপয়েন্টমেন্ট {date} তারিখে।\n\n"
            "{pre_visit_instructions}\n\n"
            "রিমাইন্ডার বন্ধ করতে STOP লিখুন।"
        )
