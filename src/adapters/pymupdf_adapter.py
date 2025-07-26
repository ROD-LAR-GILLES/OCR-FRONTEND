"""
PDF-to-Markdown adapter.

- Uses PyMuPDF (fitz) to extract embedded text from digital PDFs.
- Falls back to selective OCR (see ``ocr_adapter``) when pages have no selectable text.

This module resides in the *infrastructure* layer of the clean architecture,
serving as a bridge between domain logic and external libraries.
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import List

try:
    import fitz
except ImportError:
    fitz = None

from PIL import Image
from loguru import logger

# Imports actualizados para nueva arquitectura
from shared.constants.config import config
from adapters.llm_refiner import LLMRefiner
from . import ocr_adapter, parallel_ocr

# Inicializar el refinador LLM (será manejado por el contenedor de dependencias)
llm_refiner = LLMRefiner()


###############################################################################
#                      FULL DOCUMENT EXTRACTION FLOW                          #
###############################################################################

def extract_markdown(pdf_path: Path) -> str:
    """
    Convert an entire PDF to Markdown, applying OCR selectively.

    - If ``needs_ocr(page)`` is True → run OCR on that page.
    - Else, extract embedded text with PyMuPDF.

    The final Markdown includes:
    - A top-level title (file stem).
    - One section per page.
    """
    logger.info(f"Iniciando procesamiento del archivo: {pdf_path}")
    page_parts: List[str] = []

    # Extracción de texto principal
    logger.info("Extracción de texto de páginas")
    texts = parallel_ocr.run_parallel(pdf_path)

    for page_num, text in enumerate(texts, start=1):
        page_parts.append(f"## Page {page_num}\n\n{text.strip()}")

    logger.info("Completada extracción de texto")

    md_out = f"# {pdf_path.stem}\n\n" + "\n\n".join(page_parts)

    # ─── Optional document-level LLM refinement ──────────────────────────

    # Fase final - Refinamiento LLM
    logger.info("Iniciando refinamiento con LLM")
    try:
        if config.llm.mode != "off":
            logger.info(
                f"Aplicando refinamiento LLM con modo: {config.llm.mode}")
            md_out = llm_refiner.prompt_refine(md_out)
            logger.info("Refinamiento LLM completado exitosamente")
    except Exception as exc:
        logger.warning(f"El refinamiento LLM fue omitido: {exc}")

    logger.success(f"Procesamiento completado para {pdf_path}")
    return md_out
