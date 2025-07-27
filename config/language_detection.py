"""
Configuración de detección de idioma para compatibilidad.

Este módulo proporciona una capa de compatibilidad mientras se refactoriza el código.

DEPRECATED: 
    Este módulo está marcado para eliminación en futuras versiones.
    Por favor, use src.shared.constants.config.AppConfig en su lugar.
    Ver docs/MIGRATION.md para más información sobre la migración.
"""
import warnings
from src.shared.constants.config import AppConfig
from typing import Dict, Any, Optional

# Emitir advertencia de deprecación
warnings.warn(
    "El módulo config.language_detection está obsoleto y será eliminado en futuras versiones. "
    "Use src.shared.constants.config.AppConfig en su lugar.",
    DeprecationWarning, stacklevel=2
)

# Acceder a la configuración centralizada
config = AppConfig()


def get_config():
    """
    Retorna la configuración de detección de idioma.

    DEPRECATED: Esta función será eliminada en futuras versiones.
    Use src.shared.constants.config.AppConfig en su lugar.
    """
    return {
        "model_path": "data/models/fasttext/lid.176.ftz",
        "min_confidence": 0.7,
        "default_language": config.ocr.language,
        "use_fasttext": True,
        "supported_languages": ["es", "en", "zh", "fr", "de"],
        "fasttext_model_path": "data/models/fasttext/lid.176.ftz"
    }


class SimpleLanguageDetector:
    """Detector simple de idiomas basado en reglas básicas."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el detector simple de idiomas.

        Args:
            config: Configuración opcional
        """
        self.config = config or get_config()
        self.default_language = self.config.get("default_language", "es")

    def detect(self, text: str) -> str:
        """
        Detecta el idioma de un texto usando reglas simples.

        Args:
            text: Texto a analizar

        Returns:
            str: Código ISO del idioma detectado (es, en, etc.)
        """
        # En esta implementación simple, siempre retornamos el idioma por defecto
        return self.default_language
