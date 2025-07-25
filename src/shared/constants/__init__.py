"""
Constantes compartidas.
"""

from .directories import (
    Directories,
    PDF_DIR, UPLOAD_DIR, OUTPUT_DIR, RESULT_DIR,
    DATA_DIR, CACHE_DIR, MODELS_DIR, LOGS_DIR, STATIC_DIR
)

# Importar configuración desde shared.util en lugar de shared.constants
from shared.util.config import (
    AppConfig, OCRConfig, LLMConfig, OpenAIConfig,
    GeminiConfig, APIConfig, LoggingConfig, config
)

__all__ = [
    # Directorios
    'Directories',
    'PDF_DIR', 'UPLOAD_DIR', 'OUTPUT_DIR', 'RESULT_DIR',
    'DATA_DIR', 'CACHE_DIR', 'MODELS_DIR', 'LOGS_DIR', 'STATIC_DIR',

    # Configuración
    'AppConfig', 'OCRConfig', 'LLMConfig', 'OpenAIConfig',
    'GeminiConfig', 'APIConfig', 'LoggingConfig', 'config'
]
