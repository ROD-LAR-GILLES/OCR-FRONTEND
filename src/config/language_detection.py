"""
Configuración para la detección de idiomas.

Este módulo proporciona configuraciones y utilidades para la detección
de idiomas en documentos procesados por el sistema OCR.
"""
from typing import Dict, Any
import os
from pathlib import Path
from loguru import logger


def get_config() -> Dict[str, Any]:
    """
    Obtiene la configuración para la detección de idiomas.

    Returns:
        Dict[str, Any]: Configuración con parámetros para la detección
    """
    # Intentar cargar desde variables de entorno primero
    default_language = os.getenv("LANGUAGE_DEFAULT", "es")
    min_confidence = float(os.getenv("LANGUAGE_MIN_CONFIDENCE", "0.6"))
    use_fasttext = os.getenv(
        "USE_FASTTEXT", "").lower() in ("true", "1", "yes")

    # Ruta del modelo FastText (relativa al directorio de datos)
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    fasttext_model_path = os.getenv(
        "FASTTEXT_MODEL_PATH",
        str(data_dir / "models/fasttext/lid.176.ftz")
    )

    return {
        "default_language": default_language,
        "min_confidence": min_confidence,
        "supported_languages": ["es", "en", "fr", "de", "it"],
        "use_fasttext": use_fasttext,
        "fasttext_model_path": fasttext_model_path,
        "text_min_length": 50,  # Longitud mínima para detección confiable
    }


class SimpleLanguageDetector:
    """Detector básico de idiomas que siempre retorna español."""

    def __init__(self):
        """Inicializa el detector con configuración para español por defecto."""
        self.default_language = "es"

    def detect(self, text: str) -> str:
        """
        Detecta el idioma del texto. Por defecto retorna español.

        Args:
            text: Texto a analizar

        Returns:
            str: Código ISO del idioma (siempre 'es' para simplificar)
        """
        if not text or not text.strip():
            return self.default_language

        # Para simplificar, siempre retornamos español
        # Esto facilita el procesamiento y configuración de OCR
        logger.debug(
            f"Detectando idioma para texto de {len(text)} caracteres -> {self.default_language}")
        return self.default_language


# Instancia global del detector simple
detector = SimpleLanguageDetector()
