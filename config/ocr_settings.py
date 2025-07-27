"""
Módulo de configuración OCR para compatibilidad.

Este módulo proporciona una capa de compatibilidad mientras se refactoriza el código.

DEPRECATED: 
    Este módulo está marcado para eliminación en futuras versiones.
    Por favor, use src.shared.constants.config.AppConfig en su lugar.
    Ver docs/MIGRATION.md para más información sobre la migración.
"""
import warnings
from src.shared.constants.config import AppConfig

# Emitir advertencia de deprecación
warnings.warn(
    "El módulo config.ocr_settings está obsoleto y será eliminado en futuras versiones. "
    "Use src.shared.constants.config.AppConfig en su lugar.",
    DeprecationWarning, stacklevel=2
)

# Acceder a la configuración centralizada
config = AppConfig()

# Clase de compatibilidad para mantener compatibilidad con el código existente


class OCRSettings:
    """
    Configuraciones para OCR (compatibilidad).

    DEPRECATED: Esta clase será eliminada en futuras versiones.
    Use src.shared.constants.config.AppConfig.ocr en su lugar.
    """
    DPI = config.ocr.dpi
    OCR_LANG = config.ocr.language

    # Rutas de archivos de datos para OCR
    CORRECTIONS_PATH = "data/corrections.csv"
    WORDS_PATH = "data/legal_words.txt"
    PATTERNS_PATH = "data/legal_patterns.txt"

    # Formato de logging (compatibilidad)
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

    @staticmethod
    def get_tesseract_config(psm: int = 3) -> str:
        """Construye la configuración para Tesseract."""
        return f"--psm {psm} --oem 3"
