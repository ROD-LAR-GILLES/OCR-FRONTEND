"""
Detector de idiomas simplificado - por defecto español.
"""
from loguru import logger

class LanguageDetector:
    def __init__(self):
        """Inicializa el detector con configuración para español por defecto."""
        self.default_language = "es"
        
    def detect_language(self, text: str) -> str:
        """
        Detecta el idioma del texto. Por defecto retorna español.
        """
        if not text or not text.strip():
            return self.default_language
        
        # Para simplificar, siempre retornamos español
        # Esto facilita el procesamiento y configuración de OCR
        logger.debug(f"Detectando idioma para texto de {len(text)} caracteres -> {self.default_language}")
        return self.default_language
