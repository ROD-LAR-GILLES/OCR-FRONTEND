# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/__init__.py
#  Python 3.11 • Módulo OCR modular
# ──────────────────────────────────────────────────────────────

"""
Módulo OCR modular organizado por responsabilidades.

Exporta las funciones principales para mantener compatibilidad.
"""

from .engine import perform_ocr_on_page
from .utils import needs_ocr, extract_blocks, visualize_ocr_regions
from .tables import detect_table_regions, ocr_table_to_markdown, extract_tables_from_page, has_visual_table
from .text_processing import detect_lists, detect_structured_headings, segment_text_blocks, apply_manual_corrections, cleanup_text
from .image_processing import correct_rotation, estimate_psm_for_page
from .config import build_tesseract_config, DPI, TESSERACT_CONFIG, OCR_LANG, CORRECTIONS_PATH

__all__ = [
    # Engine principal
    'perform_ocr_on_page',

    # Utilidades
    'needs_ocr',
    'extract_blocks',
    'visualize_ocr_regions',

    # Detección de tablas
    'detect_table_regions',
    'ocr_table_to_markdown',
    'extract_tables_from_page',
    'has_visual_table',

    # Procesamiento de texto
    'detect_lists',
    'detect_structured_headings',
    'segment_text_blocks',
    'apply_manual_corrections',
    'cleanup_text',

    # Procesamiento de imágenes
    'correct_rotation',
    'estimate_psm_for_page',

    # Configuración
    'build_tesseract_config',
    'DPI',
    'TESSERACT_CONFIG',
    'OCR_LANG',
    'CORRECTIONS_PATH'
]
