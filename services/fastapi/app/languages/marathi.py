from app.languages.base_language import BaseLanguage


class Marathi(BaseLanguage):
    def format_date(self, date: str) -> str:
        return date

    def get_greeting(self) -> str:
        return "नमस्कार"
