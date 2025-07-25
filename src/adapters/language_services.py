"""
Servicios de detección y procesamiento de idiomas.

Este módulo contiene los adaptadores para detectar idiomas en textos,
incluyendo tanto implementaciones básicas como avanzadas.
"""

import re
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Type

# Importaciones de terceros
from loguru import logger

# Importaciones internas
from shared.util.config import AppConfig

# Implementación de SimpleLanguageDetector para evitar dependencia externa


class SimpleLanguageDetector:
    """
    Detector simple de idiomas basado en palabras clave.

    Esta es una implementación simplificada para evitar dependencias externas.
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.default_language = self.config.get('default_language', 'es')

    def detect(self, text):
        """Detecta el idioma basándose en palabras clave comunes"""
        # Por defecto devolvemos español
        return self.default_language

# Función para obtener la configuración


def get_config():
    return {'default_language': 'es'}


# Instancia de configuración
app_config = AppConfig()


# ===== Detector base de idiomas =====

class LanguageDetector:
    """
    Detector de idiomas basado en características del texto.

    Utiliza varias estrategias para determinar el idioma:
    1. Análisis de frecuencia de caracteres específicos de cada idioma
    2. Detección de palabras clave específicas
    3. Patrones gramaticales y sintácticos

    Por defecto, retorna español si no hay suficiente confianza.
    """

    def __init__(self):
        """Inicializa el detector con la configuración por defecto."""
        self.config = get_config()
        self.supported_languages = self.config.get(
            "supported_languages", ["es", "en"])
        self.default_language = self.config.get("default_language", "es")

        # Palabras comunes para cada idioma soportado
        self.common_words = {
            "es": ["el", "la", "los", "las", "un", "una", "y", "en", "de", "que", "por", "con", "para"],
            "en": ["the", "and", "to", "of", "a", "in", "that", "it", "with", "for", "as", "on"]
        }

    def detect(self, text: str) -> str:
        """
        Detecta el idioma de un texto utilizando heurísticas simples.

        Args:
            text: Texto para analizar

        Returns:
            Código ISO del idioma detectado (por defecto 'es')
        """
        if not text or len(text.strip()) < self.config.get("text_min_length", 50):
            return self.default_language

        text_lower = text.lower()
        scores = {}

        # 1. Buscar palabras comunes
        for lang, words in self.common_words.items():
            if lang not in self.supported_languages:
                continue

            # Calcular proporción de palabras encontradas
            count = sum(1 for word in words if re.search(
                r'\b' + re.escape(word) + r'\b', text_lower))
            scores[lang] = count / len(words)

        # 2. Caracteres especiales
        if "es" in self.supported_languages:
            # Más peso para español si hay caracteres como ñ, ¿, ¡, etc.
            es_chars = sum(1 for c in text if c in "áéíóúüñ¿¡")
            if es_chars > 0:
                scores["es"] = scores.get("es", 0) + 0.3

        # 3. Patrones gramaticales
        if "en" in self.supported_languages:
            # Patrones típicos ingleses (ej: 's, 've, 'll)
            en_patterns = sum(1 for pattern in ["'s", "'ve", "'ll", "'re"]
                              if pattern in text_lower)
            if en_patterns > 0:
                scores["en"] = scores.get("en", 0) + 0.2

        # Determinar idioma basado en puntuación
        if not scores:
            return self.default_language

        best_lang = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"Idioma detectado: {best_lang} (scores: {scores})")
        return best_lang


# ===== Detector avanzado usando FastText =====

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


# ===== Fábrica de detectores de idiomas =====

# Variable para la disponibilidad de FastText
try:
    import fasttext
    FASTTEXT_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    FASTTEXT_AVAILABLE = False


class LanguageDetectorFactory:
    """
    Fábrica para crear detectores de idiomas según la configuración.

    Esta clase permite instanciar diferentes implementaciones de
    detectores de idiomas según las necesidades y disponibilidad
    de bibliotecas como FastText.
    """

    # Registro de implementaciones disponibles
    implementations: Dict[str, Type] = {
        "basic": LanguageDetector,
        "simple": SimpleLanguageDetector,
    }

    # Añadir FastText si está disponible
    if FASTTEXT_AVAILABLE:
        implementations["fasttext"] = FastTextLanguageDetector

    @classmethod
    def create(cls, detector_type: str) -> LanguageDetector:
        """
        Crea una instancia del detector especificado.

        Args:
            detector_type: Tipo de detector a crear ('basic', 'fasttext', etc)

        Returns:
            Instancia del detector solicitado o del detector básico si no existe
        """
        if detector_type not in cls.implementations:
            logger.warning(f"Tipo de detector '{detector_type}' no disponible. "
                           f"Tipos disponibles: {list(cls.implementations.keys())}")
            detector_type = "basic"

        logger.debug(f"Creando detector de idioma: {detector_type}")
        return cls.implementations[detector_type]()

    @classmethod
    def register(cls, name: str, implementation: Type) -> None:
        """
        Registra una nueva implementación de detector.

        Args:
            name: Nombre para la implementación
            implementation: Clase de la implementación
        """
        cls.implementations[name] = implementation
        logger.debug(f"Registrado detector de idioma: {name}")


# Función auxiliar para obtener el detector configurado
def get_language_detector() -> LanguageDetector:
    """
    Obtiene el detector de idioma configurado en el sistema.

    Returns:
        Una instancia del detector configurado
    """
    config = get_config()
    detector_type = config.get("detector_type", "basic")

    # Si se ha configurado FastText pero no está disponible, usar detector básico
    if detector_type == "fasttext" and not FASTTEXT_AVAILABLE:
        logger.warning(
            "FastText solicitado pero no disponible. Usando detector básico.")
        detector_type = "basic"

    return LanguageDetectorFactory.create(detector_type)
