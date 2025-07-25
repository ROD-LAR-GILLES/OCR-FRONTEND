"""
Módulo de infraestructura para el sistema OCR.

Este módulo contiene implementaciones técnicas de servicios como
almacenamiento, logging y caché que dan soporte a la aplicación.
La infraestructura proporciona servicios a la capa de adaptadores
sin exponer detalles de implementación al dominio.
"""

from .file_storage import save_markdown, log_api_interaction
from .logging_setup import logger, log_execution_time, get_logger_for_module
from .ocr_cache import OCRCache, ocr_cache
from .storage_adapter import StorageAdapter

__all__ = [
    # Almacenamiento de archivos
    'save_markdown',
    'log_api_interaction',
    'StorageAdapter',

    # Logging
    'logger',
    'log_execution_time',
    'get_logger_for_module',

    # Caché OCR
    'OCRCache',
    'ocr_cache',
]
