"""
Módulo de utilidades compartidas.
"""

from .error_handling import (
    ErrorType, ErrorSeverity, ErrorContext, BaseApplicationError,
    DocumentError, StorageError, LLMError, OCRError, ValidationError,
    ConfigurationError, NetworkError, FileError, ErrorHandler
)

__all__ = [
    # Enums
    'ErrorType',
    'ErrorSeverity',

    # Clases de error
    'ErrorContext',
    'BaseApplicationError',
    'DocumentError',
    'StorageError',
    'LLMError',
    'OCRError',
    'ValidationError',
    'ConfigurationError',
    'NetworkError',
    'FileError',

    # Utilidades
    'ErrorHandler'
]
