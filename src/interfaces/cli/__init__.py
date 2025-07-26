"""
CLI Module - Interfaz de línea de comandos consolidada.

Este módulo organiza la interfaz CLI con componentes consolidados:
- menu: Menú principal y navegación
- pdf_management: Gestión consolidada de PDFs
- processing: Funciones de procesamiento
- utils: Utilidades consolidadas (helpers + constantes)
"""

from .utils import show_llm_status, CLI_PDF_DIR
from .pdf_management import pdf_manager, list_pdfs, select_pdf
from .processing import convert_pdf
from .menu import main_loop

# Importar componentes principales para fácil acceso

__all__ = [
    'main_loop',
    'list_pdfs',
    'select_pdf',
    'convert_pdf',
    'show_llm_status',
    'pdf_manager',
    'CLI_PDF_DIR'
]
