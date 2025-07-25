"""
Implementación avanzada de detección de idiomas usando FastText.

Este módulo proporciona una implementación opcional basada en FastText para
la detección de idiomas en textos. Solo se cargará y utilizará cuando esté
habilitado en la configuración.
"""
from pathlib import Path
import os
from typing import Optional
from loguru import logger
from config import config as app_config


class FastTextLanguageDetector:
    """
    Detector de idiomas basado en el modelo FastText.

    Utiliza el modelo preentrenado de FastText para identificar
    idiomas en texto con alta precisión.
    """

    def __init__(self):
        """Inicializa el detector cargando el modelo FastText si está disponible."""
        self.lang_config = app_config.language
        self.model = None
        self.model_path = self.lang_config["fasttext_model_path"]
        self.supported_languages = self.lang_config["supported_languages"]
        self.default_language = self.lang_config["default_language"]

        if self.lang_config["use_fasttext"]:
            self._load_model()

    def _load_model(self):
        """Carga el modelo FastText si está disponible."""
        try:
            import fasttext

            model_path = Path(self.model_path)
            if not model_path.exists():
                logger.warning(f"Modelo FastText no encontrado en {model_path}. "
                               "La detección avanzada de idiomas no estará disponible.")
                return

            logger.info(f"Cargando modelo FastText desde {model_path}")
            self.model = fasttext.load_model(str(model_path))
            logger.success("Modelo FastText cargado correctamente")

        except ImportError:
            logger.warning("Librería FastText no instalada. "
                           "Para habilitar la detección avanzada de idiomas, instala: pip install fasttext")

    def detect(self, text: str) -> str:
        """
        Detecta el idioma de un texto usando FastText.

        Args:
            text: Texto para analizar

        Returns:
            Código ISO del idioma detectado
        """
        if not self.model or not text or len(text.strip()) < self.lang_config["text_min_length"]:
            return self.default_language

        try:
            # Normalizar texto para análisis
            text = text.replace('\n', ' ').strip()

            # Predecir idioma con FastText
            predictions = self.model.predict(text, k=3)
            languages = [lang.replace('__label__', '')
                         for lang in predictions[0]]
            scores = predictions[1]

            # Filtrar idiomas soportados
            for i, lang in enumerate(languages):
                # FastText usa códigos como 'en' y 'es', tomamos los primeros 2 caracteres
                lang_code = lang[:2].lower()
                if lang_code in self.supported_languages:
                    confidence = float(scores[i])
                    logger.debug(
                        f"Idioma detectado con FastText: {lang_code} (confianza: {confidence:.2f})")

                    if confidence >= self.lang_config["min_confidence"]:
                        return lang_code

            logger.debug(
                "No se encontró un idioma soportado con suficiente confianza")
            return self.default_language

        except Exception as e:
            logger.error(
                f"Error en la detección de idioma con FastText: {str(e)}")
            return self.default_language
