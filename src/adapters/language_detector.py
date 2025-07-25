"""
Detector de idiomas para texto extraído de documentos.

Este módulo proporciona detección de idiomas para optimizar el proceso OCR
y el refinamiento posterior. Implementa una estrategia de detección
configurable con fallback a español cuando no se puede determinar el idioma.
"""
import re
from typing import Dict, Optional, List, Tuple
from loguru import logger
from config.language_detection import get_config
from config import config as app_config


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
        """Inicializa el detector con configuración para los idiomas soportados."""
        # Usar la configuración centralizada
        lang_config = app_config.language
        self.default_language = lang_config["default_language"]
        self.min_confidence = lang_config["min_confidence"]
        self.text_min_length = lang_config["text_min_length"]
        self.supported_languages = lang_config["supported_languages"]

        # Marcadores de idioma (caracteres y secuencias únicas)
        self.markers = {
            "es": ["ñ", "á", "é", "í", "ó", "ú", "¿", "¡"],
            "en": ["th", "wh", "ing"],
            "fr": ["ç", "œ", "à", "ê", "ô", "ù"],
            "de": ["ä", "ö", "ü", "ß"],
            "it": ["zz", "gli", "gn", "sci"]
        }

        # Palabras comunes por idioma
        self.common_words = {
            "es": ["de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para"],
            "en": ["the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "as", "with", "was"],
            "fr": ["le", "la", "les", "des", "un", "une", "et", "est", "en", "que", "qui", "dans", "pour"],
            "de": ["der", "die", "das", "und", "ist", "von", "dem", "zu", "mit", "den", "auf", "ein", "eine"],
            "it": ["il", "la", "e", "di", "che", "in", "un", "una", "per", "con", "sono", "ho", "hai"]
        }

    def detect_language(self, text: str) -> str:
        """
        Detecta el idioma del texto mediante análisis heurístico.

        Args:
            text: Texto para analizar

        Returns:
            Código ISO del idioma detectado (es, en, fr, de, it)
        """
        if not text or len(text.strip()) < self.text_min_length:
            logger.debug(
                f"Texto demasiado corto para detección fiable: {len(text) if text else 0} caracteres")
            return self.default_language

        # Normalizar texto para análisis
        text = text.lower()

        # Calcular confianza para cada idioma
        scores: Dict[str, float] = {}

        # 1. Análisis de marcadores específicos
        for lang, markers in self.markers.items():
            marker_count = sum(text.count(m) for m in markers)
            scores[lang] = scores.get(lang, 0) + marker_count / len(text) * 100

        # 2. Análisis de palabras comunes
        words = re.findall(r'\b\w+\b', text)
        for lang, common in self.common_words.items():
            common_count = sum(1 for w in words if w in common)
            scores[lang] = scores.get(lang, 0) + common_count / len(words) * 50

        # Normalizar puntuaciones
        total_score = sum(scores.values()) or 1
        for lang in scores:
            scores[lang] /= total_score

        # Encontrar el idioma con mayor puntuación
        best_lang, best_score = max(
            scores.items(), key=lambda x: x[1], default=(self.default_language, 0))

        logger.debug(
            f"Detección de idioma: {best_lang} (confianza: {best_score:.2f})")
        logger.debug(
            f"Puntuaciones por idioma: {', '.join(f'{l}:{s:.2f}' for l, s in scores.items())}")

        # Verificar confianza mínima
        if best_score < self.min_confidence:
            logger.debug(
                f"Confianza insuficiente ({best_score:.2f}), utilizando idioma por defecto: {self.default_language}")
            return self.default_language

        return best_lang

    def detect(self, text: str) -> str:
        """
        API pública para detectar el idioma de un texto.

        Args:
            text: Texto para analizar

        Returns:
            Código ISO del idioma detectado
        """
        return self.detect_language(text)
