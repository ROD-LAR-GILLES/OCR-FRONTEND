"""
CLI Module - Interfaz de línea de comandos modular.

Este módulo organiza la interfaz CLI en componentes separados:
- menu: Menú principal y navegación
- pdf_handler: Gestión y selección de PDFs
- processing: Funciones de procesamiento
- cache_manager: Gestión de caché OCR
- helpers: Utilidades compartidas
"""

from .constants import PDF_DIR
from .helpers import show_llm_status
from .cache_manager import show_cache_stats
from .processing import convert_pdf
from .pdf_handler import list_pdfs, select_pdf
from .menu import main_loop

# Importar componentes principales para fácil acceso

__all__ = [
    'main_loop',
    'list_pdfs',
    'select_pdf',
    'convert_pdf',
    'show_cache_stats',
    'show_llm_status',
    'PDF_DIR'
]
