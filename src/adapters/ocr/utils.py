# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/utils.py
#  Python 3.11 • Utilidades OCR
# ──────────────────────────────────────────────────────────────

"""
Funciones de utilidad para el sistema OCR.
"""

import logging
from io import BytesIO
import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

from .config import DPI, TESSERACT_CONFIG, OCR_LANG


def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR revisando si contiene texto seleccionable.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        bool: True si no hay texto y se debe aplicar OCR.
    """
    return page.get_text("text").strip() == ""


def extract_blocks(page: fitz.Page) -> list[tuple[float, float, float, float, str]]:
    """
    Extrae bloques de texto con coordenadas de la página.

    Returns:
        Lista de tuplas (x0, y0, x1, y1, texto)
    """
    blocks = page.get_text("blocks")
    return [(b[0], b[1], b[2], b[3], b[4].strip()) for b in blocks if b[4].strip()]


def visualize_ocr_regions(page: fitz.Page, output_path: str = "ocr_regions.png") -> None:
    """
    Dibuja las regiones de texto detectadas por Tesseract en la imagen de una página y guarda el resultado.

    Args:
        page (fitz.Page): Página PDF a procesar.
        output_path (str): Ruta donde guardar la imagen con las cajas dibujadas.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))
    img = np.array(img_pil)

    # Convertir a RGB si es necesario
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    data = pytesseract.image_to_data(
        img, lang=OCR_LANG, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)

    n_boxes = len(data['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (data['left'][i], data['top']
                        [i], data['width'][i], data['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Guardar o mostrar la imagen
    Image.fromarray(img).save(output_path)
    logging.info(f"Regiones OCR visualizadas en: {output_path}")
