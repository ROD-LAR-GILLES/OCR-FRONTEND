"""
Módulo OCR centralizado.

Este módulo expone todas las funcionalidades del OCR estructuradas en 3 componentes:
- ocr_engine: Motor principal y configuración
- ocr_image: Procesamiento de imágenes y tablas
- ocr_text: Procesamiento de texto OCR
"""

# Importamos desde los nuevos módulos refactorizados
from .ocr_engine import (
    extract_text_from_pdf,
    extract_text_from_image,
    process_pdf_file,
    OCR_LANG,
    DPI,
    build_tesseract_config
)

from .ocr_image import (
    correct_rotation,
    estimate_psm_for_page,
    has_visual_table,
    detect_table_regions,
    extract_tables_from_page,
    create_mask_without_tables,
    ocr_table_to_markdown
)

from .ocr_text import (
    apply_corrections,
    fix_line_breaks,
    apply_legal_corrections,
    clean_and_format_text,
    detect_language,
    split_into_sections
)

__all__ = [
    # De ocr_engine
    'extract_text_from_pdf',
    'extract_text_from_image',
    'process_pdf_file',
    'OCR_LANG',
    'DPI',
    'build_tesseract_config',

    # De ocr_image
    'correct_rotation',
    'estimate_psm_for_page',
    'has_visual_table',
    'detect_table_regions',
    'extract_tables_from_page',
    'create_mask_without_tables',
    'ocr_table_to_markdown',

    # De ocr_text
    'apply_corrections',
    'fix_line_breaks',
    'apply_legal_corrections',
    'clean_and_format_text',
    'detect_language',
    'split_into_sections'
]
