"""
Language registry — maps language names/codes to their class instances.
"""

from app.languages.base_language import BaseLanguage
from app.languages.english import English
from app.languages.hindi import Hindi
from app.languages.bengali import Bengali
from app.languages.marathi import Marathi
from app.languages.tamil import Tamil

# Registry: lowercase name or code → language instance
_REGISTRY: dict[str, BaseLanguage] = {
    "en": English(),
    "english": English(),
    "hi": Hindi(),
    "hindi": Hindi(),
    "bn": Bengali(),
    "bengali": Bengali(),
    "bangla": Bengali(),
    "mr": Marathi(),
    "marathi": Marathi(),
    "ta": Tamil(),
    "tamil": Tamil(),
}

_DEFAULT = English()


def get_language(name: str | None) -> BaseLanguage:
    """
    Get a language by name or code. Falls back to English if unknown.
    Case-insensitive matching.
    """
    if not name:
        return _DEFAULT
    return _REGISTRY.get(name.strip().lower(), _DEFAULT)


def get_supported_languages() -> list[str]:
    """Return list of supported language names."""
    return ["english", "hindi", "bengali", "marathi", "tamil"]
