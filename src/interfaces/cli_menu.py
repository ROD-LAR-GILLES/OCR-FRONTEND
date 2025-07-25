"""
OCR-PYMUPDF - Interfaz de línea de comandos.

Esta interfaz proporciona acceso interactivo a todas las funciones
del sistema OCR. La funcionalidad principal se ha movido a módulos
específicos en el paquete cli/ para mejor organización.
"""

from infrastructure.logging_setup import logger
from .cli import main_loop

# Re-exportar la función principal para mantener compatibilidad
__all__ = ['main_loop']

if __name__ == "__main__":
    logger.info("Iniciando interfaz CLI")
    main_loop()
