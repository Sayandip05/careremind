from abc import ABC, abstractmethod
from typing import List, Dict


class BaseSpecialty(ABC):
    @abstractmethod
    def get_reminder_timing(self) -> List[int]:
        pass

    @abstractmethod
    def get_message_template(self) -> str:
        pass

    @abstractmethod
    def get_tone(self) -> str:
        pass
