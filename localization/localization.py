"""
localization.localization
==========================
Gestor global de localización (mismo API público que el original:
LocalizationManager, get_localized_text, set_current_language,
get_current_language, _call_txt).

Cambio respecto al original: la ubicación de data/lang.json ya no depende
únicamente del directorio de trabajo actual (cwd). El original hacía
`os.path.join("data", "lang.json")`, lo que significa que si la app frozen
(.exe) se lanza con un cwd distinto a su propia carpeta (por ejemplo, un
acceso directo mal configurado, o al abrir un .pdpack con "abrir con..."),
`data/lang.json` deja de encontrarse y todo el texto de la UI cae a
"TEXT_NOT_FOUND (404)". Ahora se prueban, en orden: cwd (comportamiento
original, por compatibilidad), la carpeta del ejecutable/script, y la
carpeta raíz del proyecto (padre de este paquete).
"""
import json
import os

from core.paths import get_application_path


def _find_lang_json() -> str:
    """Busca data/lang.json en varias ubicaciones candidatas, en orden de prioridad."""
    candidates = [
        os.path.join(os.getcwd(), "data", "lang.json"),          # comportamiento original
        os.path.join(get_application_path(), "data", "lang.json"),  # carpeta de la app/exe
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Ninguna existe todavía: devolvemos la más razonable (junto al ejecutable)
    # para que el mensaje de advertencia apunte a un lugar útil.
    return candidates[1]


class LocalizationManager:
    """Gestor global de localización para manejar múltiples idiomas."""

    _instance = None
    _localization_data = None
    _current_language = "en"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
            cls._instance._load_localization_data()
        return cls._instance

    def _load_localization_data(self):
        """Carga los datos de localización desde el archivo JSON."""
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
        """Establece el idioma actual."""
        self._current_language = language_code

    def get_language(self):
        """Obtiene el idioma actual."""
        return self._current_language

    def get_text(self, text_id, language_code=None):
        """
        Obtiene el texto localizado por text_id y language_code.

        Args:
            text_id (str): Identificador del texto
            language_code (str): Código de idioma (en, es, ja). Si es None, usa el idioma actual

        Returns:
            str: El texto localizado o "TEXT_NOT_FOUND (404)" si no se encuentra
        """
        if language_code is None:
            language_code = self._current_language

        if self._localization_data is None:
            print(f"[Localization] Missing data: attempted to get '{text_id}' for '{language_code}' but localization data is not loaded.")
            print("[Localization] Please check data/lang.json and ensure it exists and is valid JSON.")
            return "TEXT_NOT_FOUND (404)"

        full_key = f"{text_id}_{language_code}"

        if full_key in self._localization_data:
            return self._localization_data[full_key]

        if language_code != "en":
            fallback_key = f"{text_id}_en"
            if fallback_key in self._localization_data:
                return self._localization_data[fallback_key]

        print(f"[Localization] TEXT NOT FOUND -> id: '{text_id}' (lang requested: '{language_code}').")
        print(f"[Localization] Add keys '{text_id}_{language_code}' or '{text_id}_en' to data/lang.json to fix this.")
        return "TEXT_NOT_FOUND (404)"


def get_localized_text(text_id, language_code=None):
    """Función global para obtener texto localizado."""
    manager = LocalizationManager()
    return manager.get_text(text_id, language_code)


def set_current_language(language_code):
    """Establece el idioma globalmente."""
    manager = LocalizationManager()
    manager.set_language(language_code)


def get_current_language():
    """Obtiene el idioma actual."""
    manager = LocalizationManager()
    return manager.get_language()


def _call_txt(text_id, language_code=None):
    """
    Alias corto para get_localized_text()
    Uso: _("button_accept") o _("button_accept", "es")
    """
    return get_localized_text(text_id, language_code)
