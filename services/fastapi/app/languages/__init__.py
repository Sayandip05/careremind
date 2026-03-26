"""
Languages package — re-exports get_language() for convenience.
Consistent with specialty/__init__.py pattern.
"""

from app.languages.detector import get_language, get_supported_languages

__all__ = ["get_language", "get_supported_languages"]
