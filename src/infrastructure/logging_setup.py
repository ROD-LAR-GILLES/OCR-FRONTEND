"""
Configuración centralizada de logging.

Este módulo configura el sistema de logging para toda la aplicación,
utilizando loguru para una salida formateada y colorida, y proporcionando
decoradores y utilidades para facilitar el registro de eventos y tiempos de ejecución.
"""
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from loguru import logger

from config import config
import logging
import sys
import time
from functools import wraps
from pathlib import Path
from datetime import datetime
from typing import Callable, Any

from loguru import logger
from config import config

# Configuración de formatos y destinos para loguru
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Directorio para logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Archivo de log con fecha
LOG_FILE = LOG_DIR / f"ocr_{datetime.now().strftime('%Y%m%d')}.log"

# Configurar loguru
logger.remove()  # Eliminar handler por defecto
logger.add(sys.stderr, format=LOG_FORMAT, level=config.logging["level"])
logger.add(LOG_FILE, rotation="00:00",
           level=config.logging["level"], format=LOG_FORMAT)

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
