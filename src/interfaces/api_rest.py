"""
Entry point for the OCR-FRONTEND API.

Este módulo sirve como punto de entrada para iniciar el servidor API.
La funcionalidad principal se ha movido a los módulos específicos en el paquete api/.
"""

from infrastructure.logging_setup import logger
from .api.server import start_api

# Re-exportar la función principal para mantener compatibilidad
__all__ = ['start_api']

if __name__ == "__main__":
    start_api()
