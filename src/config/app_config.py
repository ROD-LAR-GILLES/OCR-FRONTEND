"""
Configuración unificada del sistema OCR.

Este módulo proporciona una clase de configuración centralizada que integra
todas las configuraciones del sistema en un solo lugar, facilitando
su acceso y modificación desde cualquier parte de la aplicación.
"""
from pathlib import Path
from typing import Any, Dict, Optional

from .api_settings import load_api_settings
from .language_detection import get_config as get_language_config
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .api_settings import load_api_settings
from .language_detection import get_config as get_language_config
from .llm_config import LLMConfig
from .state import LLM_MODE, LLM_PROVIDER
from .ocr_settings import OCRSettings
from .settings import Settings


class AppConfig:
    """
    Configuración unificada del sistema OCR.

    Esta clase proporciona acceso centralizado a toda la configuración
    del sistema, organizada por categorías.
    """

    def __init__(self):
        """Inicializa la configuración unificada del sistema."""
        # Cargar configuraciones de APIs
        self.api = load_api_settings()

        # Configuración de detección de idiomas
        self.language = get_language_config()

        # Configuración de LLM
        self.llm_mode = LLM_MODE
        self.llm_provider = LLM_PROVIDER
        self.llm_config = LLMConfig.load_config()

        # Configuración de OCR
        self.ocr = {
            "dpi": OCRSettings.DPI,
            "lang": OCRSettings.OCR_LANG,
            "corrections_path": OCRSettings.CORRECTIONS_PATH,
            "words_path": OCRSettings.WORDS_PATH,
            "patterns_path": OCRSettings.PATTERNS_PATH,
        }

        # Configuración de rutas
        self.paths = {
            "data_dir": Path(os.getenv("DATA_DIR", "data")),
            "result_dir": Path(os.getenv("RESULT_DIR", "result")),
        }

        # Configuración de logging
        self.logging = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": OCRSettings.LOG_FORMAT,
        }

    def get_tesseract_config(self, psm: int) -> str:
        """
        Obtiene la configuración de Tesseract para un modo PSM específico.

        Args:
            psm: Page Segmentation Mode para Tesseract

        Returns:
            str: Configuración formateada para Tesseract
        """
        return OCRSettings.get_tesseract_config(psm)

    def update_llm_config(self, config: Dict[str, Any]) -> None:
        """
        Actualiza y guarda la configuración de LLM.

        Args:
            config: Nueva configuración a guardar
        """
        LLMConfig.save_config(config)
        self.llm_config = config

    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración para un proveedor LLM específico.

        Args:
            provider: Nombre del proveedor (openai, gemini)
                     Si es None, usa el proveedor configurado

        Returns:
            Dict: Configuración del proveedor solicitado
        """
        provider = provider or self.llm_provider or "openai"
        return self.api.get(provider, {})


# Instancia global de configuración unificada
config = AppConfig()
