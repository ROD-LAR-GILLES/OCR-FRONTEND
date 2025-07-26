# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/engine.py
#  Python 3.11 • Motor principal OCR
# ──────────────────────────────────────────────────────────────

"""
Motor principal de OCR que coordina todos los módulos.
"""

import logging
from io import BytesIO

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

import config.state as state
from adapters.llm_refiner import LLMRefiner

from .config import DPI, build_tesseract_config
from .image_processing import correct_rotation, estimate_psm_for_page
from .tables import detect_table_regions, ocr_table_to_markdown
from .text_processing import (apply_manual_corrections, cleanup_text, detect_lists,
                              detect_structured_headings, segment_text_blocks)

# Inicializar el refinador LLM
llm_refiner = LLMRefiner()


def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página PDF.

    Args:
        page: Página PDF de PyMuPDF

    Returns:
        str: Texto extraído y procesado

    Proceso:
    1. Renderiza página
    2. Corrige rotación 
    3. Aplica preprocesamiento
    4. Ejecuta OCR con configuración dinámica
    5. Post-procesa resultado
    """
    # 1) Render
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))

    # 2) Deskew / rotate
    img_pil = correct_rotation(img_pil)

    # 3) Contraste local + binarizado
    gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    binar = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 15
    )
    # 4) Denoise ligero
    binar = cv2.morphologyEx(
        binar, cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)),
        iterations=1
    )
    img_pil = Image.fromarray(binar)

    # 5) PSM dinámico
    psm = estimate_psm_for_page(img_pil)
    config = build_tesseract_config(psm)

    # 6) Idioma fijado a español
    lang_param = "spa"

    # 7) OCR principal
    raw = pytesseract.image_to_string(img_pil, lang=lang_param, config=config)

    # 8) Limpieza y post-procesado existentes
    raw = re.sub(r"-\n(\w+)", r"\1", raw)
    cleaned = detect_lists(cleanup_text(raw))
    cleaned = apply_manual_corrections(cleaned)
    segmented = segment_text_blocks(cleaned)

    # 9) Detección de tablas OCR (tu lógica actual)
    table_regions = detect_table_regions(img_pil)
    if table_regions:
        tables_md = []
        for region in table_regions:
            table_img = img_pil.crop(region)
            md_tbl = ocr_table_to_markdown(table_img)
            if md_tbl.strip():
                tables_md.append(md_tbl)
        if tables_md:
            segmented += "\n\n## Tablas detectadas\n" + "\n\n".join(tables_md)

    # 10) Refinamiento LLM opcional
    try:
        if state.LLM_MODE not in {"off", None}:
            logging.info(
                f"[LLM] Page-level refinement · mode={state.LLM_MODE}")
            segmented = llm_refiner.prompt_refine(segmented)
        else:
            logging.debug(
                f"[LLM] Skipped page-level refinement · mode={state.LLM_MODE}")
    except Exception as exc:
        logging.warning(f"[LLM] Page-level refinement error → {exc}")
    return detect_structured_headings(segmented)
