"""
Fábrica de detectores de idiomas para el sistema OCR.

Este módulo proporciona una fábrica para crear detectores de idiomas
según la configuración del sistema. Soporta múltiples estrategias
de detección, desde la más simple a la más avanzada.
"""
from src.adapters.language_detector import LanguageDetector
from config.language_detection import SimpleLanguageDetector
from typing import Dict, Type, Optional
from loguru import logger
from shared.constants.config import AppConfig

# Instancia de configuración
app_config = AppConfig()

# Importación condicional para evitar errores si FastText no está disponible
try:
    from src.adapters.fasttext_detector import FastTextLanguageDetector
    FASTTEXT_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    FASTTEXT_AVAILABLE = False


class LanguageDetectorFactory:
    """
    Fábrica para crear detectores de idiomas según la configuración.

    Esta clase permite instanciar diferentes implementaciones de
    detectores de idiomas según las necesidades y disponibilidad
    de dependencias.
    """

    # Registro de detectores disponibles
    _detectors: Dict[str, Type] = {
        "simple": SimpleLanguageDetector,
        "heuristic": LanguageDetector
    }

    # Instancia singleton para cada tipo
    _instances: Dict[str, object] = {}

    @classmethod
    def register_detector(cls, name: str, detector_class: Type) -> None:
        """
        Registra un nuevo tipo de detector en la fábrica.

        Args:
            name: Nombre identificador del detector
            detector_class: Clase del detector a registrar
        """
        cls._detectors[name] = detector_class

    @classmethod
    def create(cls, detector_type: Optional[str] = None) -> object:
        """
        Crea o retorna una instancia de un detector de idiomas.

        Args:
            detector_type: Tipo de detector a crear (simple, heuristic, fasttext)
                Si es None, se selecciona según la configuración.

        Returns:
            Instancia del detector solicitado
        """
        lang_config = app_config.language

        # Si no se especifica, determinar según configuración
        if detector_type is None:
            if lang_config["use_fasttext"] and FASTTEXT_AVAILABLE:
                detector_type = "fasttext"
            else:
                detector_type = "heuristic"

        # Registrar FastText si está disponible
        if FASTTEXT_AVAILABLE and "fasttext" not in cls._detectors:
            cls.register_detector("fasttext", FastTextLanguageDetector)

        # Verificar que el tipo solicitado existe
        if detector_type not in cls._detectors:
            logger.warning(f"Tipo de detector '{detector_type}' no disponible. "
                           f"Usando detector por defecto 'heuristic'")
            detector_type = "heuristic"

        # Crear o retornar instancia existente (patrón singleton)
        if detector_type not in cls._instances:
            detector_class = cls._detectors[detector_type]
            cls._instances[detector_type] = detector_class()
            logger.debug(f"Creado detector de idiomas tipo '{detector_type}'")

        return cls._instances[detector_type]

# Función auxiliar para obtener un detector según la configuración


def get_language_detector(detector_type: Optional[str] = None):
    """
    Obtiene un detector de idiomas según la configuración.

    Args:
        detector_type: Tipo específico de detector (opcional)

    Returns:
        Instancia del detector de idiomas
    """
    return LanguageDetectorFactory.create(detector_type)
