from abc import ABC, abstractmethod


class BaseLanguage(ABC):
    @abstractmethod
    def format_date(self, date: str) -> str:
        pass

    @abstractmethod
    def get_greeting(self) -> str:
        pass
