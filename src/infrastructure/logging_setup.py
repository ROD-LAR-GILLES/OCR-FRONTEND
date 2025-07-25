"""
Configuración centralizada de logging.

Este módulo configura el sistema de logging para toda la aplicación,
utilizando loguru para una salida formateada y colorida, y proporcionando
decoradores y utilidades para facilitar el registro de eventos y tiempos de ejecución.
"""
import logging
import sys
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

try:
    from loguru import logger
except ImportError:
    # Fallback to standard logging if loguru is not available
    import logging
    logger = logging.getLogger(__name__)

from shared.util.config import config
from shared.constants.directories import LOGS_DIR

# Configuración de formatos y destinos para loguru
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Asegurar que el directorio de logs exista
LOGS_DIR.mkdir(exist_ok=True)

# Archivo de log con fecha
LOG_FILE = LOGS_DIR / f"ocr_{datetime.now().strftime('%Y%m%d')}.log"

# Configurar loguru usando la configuración centralizada


def setup_logging():
    """Configura el sistema de logging usando la configuración centralizada."""
    if 'logger' in globals() and hasattr(logger, 'remove'):
        # Solo configurar si loguru está disponible
        logger.remove()  # Eliminar handler por defecto

        log_config = config.logging

        # Configuración para consola
        logger.add(
            sys.stderr,
            format=LOG_FORMAT,
            level=log_config.level
        )

        # Configuración para archivo
        logger.add(
            LOG_FILE,
            rotation=log_config.max_file_size,
            retention=f"{log_config.backup_count} days",
            level=log_config.level,
            format=LOG_FORMAT
        )


# Configurar al importar
setup_logging()

# Configurar intercepción de logs de librerías que usan el logging estándar


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Convertir el record de logging a mensaje de loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


# Configurar el logging estándar para que use loguru
logging.basicConfig(handlers=[InterceptHandler()], level=0)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorador que registra el tiempo de ejecución de una función.

    Args:
        func: Función a decorar

    Returns:
        Callable: Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(
            f"{func.__name__} ejecutado en {elapsed_time:.2f} segundos")
        return result
    return wrapper


def get_logger_for_module(module_name: str):
    """
    Obtiene un logger específico para un módulo.

    Args:
        module_name: Nombre del módulo

    Returns:
        Logger: Instancia de logger configurada
    """
    return logger.bind(name=module_name)
