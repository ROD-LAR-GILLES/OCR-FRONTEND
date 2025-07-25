"""
Configuración centralizada de logging.
"""
import logging
import time
from functools import wraps
from config.ocr_settings import OCRSettings

# Configuración global del logger
logging.basicConfig(
    format=OCRSettings.LOG_FORMAT,
    level=getattr(logging, OCRSettings.LOG_LEVEL)
)

# Logger principal de la aplicación
logger = logging.getLogger("OCR-PYMUPDF")

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logging.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
        return result
    return wrapper
