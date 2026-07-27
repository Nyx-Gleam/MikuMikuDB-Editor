"""
localization.localization
=========================
Global localization manager (same public API as the original:
LocalizationManager, get_localized_text, set_current_language,
get_current_language, _call_txt).

Difference from the original: the location of data/lang.json no longer
depends solely on the current working directory (cwd). The original used
`os.path.join("data", "lang.json")`, which meant that if the frozen
application (.exe) was launched with a different working directory
(for example, from a misconfigured shortcut or by opening a .pdpack file
using "Open with..."), `data/lang.json` could not be found and the entire
UI would fall back to "TEXT_NOT_FOUND (404)".

This implementation searches for the localization file in the following
order: the current working directory (for backward compatibility), then
the application/executable directory.
"""

import json
import os

from core.paths import get_application_path


def _find_lang_json() -> str:
    """Search for data/lang.json in several candidate locations, in priority order."""
    candidates = [
        os.path.join(os.getcwd(), "data", "lang.json"),             # Original behavior
        os.path.join(get_application_path(), "data", "lang.json"),  # Application/executable directory
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    # None of the candidate paths exist yet. Return the most reasonable
    # location (next to the executable) so the warning points to a useful path.
    return candidates[1]


class LocalizationManager:
    """Global localization manager for handling multiple languages."""

    _instance = None
    _localization_data = None
    _current_language = "en"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
            cls._instance._load_localization_data()
        return cls._instance

    def _load_localization_data(self):
        """Load localization data from the JSON file."""
        try:
            json_path = _find_lang_json()
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    self._localization_data = json.load(f)
            else:
                print(f"Warning: Localization file not found at {json_path}")
                self._localization_data = {}
        except Exception as e:
            print(f"Error loading localization data: {e}")
            self._localization_data = {}

    def set_language(self, language_code):
        """Set the current application language."""
        self._current_language = language_code

    def get_language(self):
        """Return the current application language."""
        return self._current_language

    def get_text(self, text_id, language_code=None):
        """
        Retrieve a localized string using its text identifier.

        Args:
            text_id (str):
                Localization key.
            language_code (str, optional):
                Language code (e.g. "en", "es", "ja").
                If None, the current language is used.

        Returns:
            str:
                The localized string, or "TEXT_NOT_FOUND (404)"
                if the key does not exist.
        """
        if language_code is None:
            language_code = self._current_language

        if self._localization_data is None:
            print(f"[Localization] Missing data: attempted to get '{text_id}' for '{language_code}' but localization data is not loaded.")
            print("[Localization] Please check data/lang.json and ensure it exists and contains valid JSON.")
            return "TEXT_NOT_FOUND (404)"

        full_key = f"{text_id}_{language_code}"

        if full_key in self._localization_data:
            return self._localization_data[full_key]

        if language_code != "en":
            fallback_key = f"{text_id}_en"
            if fallback_key in self._localization_data:
                return self._localization_data[fallback_key]

        print(f"[Localization] TEXT NOT FOUND -> id: '{text_id}' (requested language: '{language_code}').")
        print(f"[Localization] Add the keys '{text_id}_{language_code}' or '{text_id}_en' to data/lang.json to resolve this.")
        return "TEXT_NOT_FOUND (404)"


def get_localized_text(text_id, language_code=None):
    """Retrieve a localized string."""
    manager = LocalizationManager()
    return manager.get_text(text_id, language_code)


def set_current_language(language_code):
    """Set the global application language."""
    manager = LocalizationManager()
    manager.set_language(language_code)


def get_current_language():
    """Return the currently selected application language."""
    manager = LocalizationManager()
    return manager.get_language()


def _call_txt(text_id, language_code=None):
    """
    Short alias for get_localized_text().

    Example:
        _("button_accept")
        _("button_accept", "es")
    """
    return get_localized_text(text_id, language_code)
