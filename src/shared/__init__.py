"""
Módulo compartido.

Contiene constantes, utilidades y componentes reutilizables
a través de toda la aplicación.
"""

from .constants import (
    Directories, config,
    PDF_DIR, UPLOAD_DIR, OUTPUT_DIR, RESULT_DIR,
    DATA_DIR, CACHE_DIR, MODELS_DIR, LOGS_DIR, STATIC_DIR
)

from .utils import (
    ErrorType, ErrorSeverity, ErrorContext, BaseApplicationError,
    DocumentError, StorageError, LLMError, OCRError, ValidationError,
    ConfigurationError, NetworkError, FileError, ErrorHandler
)

__all__ = [
    # Directorios y configuración
    'Directories', 'config',
    'PDF_DIR', 'UPLOAD_DIR', 'OUTPUT_DIR', 'RESULT_DIR',
    'DATA_DIR', 'CACHE_DIR', 'MODELS_DIR', 'LOGS_DIR', 'STATIC_DIR',

    # Manejo de errores
    'ErrorType', 'ErrorSeverity', 'ErrorContext', 'BaseApplicationError',
    'DocumentError', 'StorageError', 'LLMError', 'OCRError', 'ValidationError',
    'ConfigurationError', 'NetworkError', 'FileError', 'ErrorHandler'
]
