from app.languages.base_language import BaseLanguage


class Tamil(BaseLanguage):
    def format_date(self, date: str) -> str:
        return date

    def get_greeting(self) -> str:
        return "வணக்கம்"
