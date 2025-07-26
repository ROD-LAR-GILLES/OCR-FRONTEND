# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/image_processing.py
#  Python 3.11 • Preprocesamiento de imágenes
# ──────────────────────────────────────────────────────────────

"""
Funciones para preprocesamiento y análisis de imágenes.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image


def correct_rotation(img_pil: Image.Image) -> Image.Image:
    """
    Corrige la rotación de una imagen usando detección automática vía Tesseract OSD.

    Args:
        img_pil (Image.Image): Imagen original.

    Returns:
        Image.Image: Imagen rotada si se detectó desviación de ángulo.
    """
    try:
        osd = pytesseract.image_to_osd(img_pil)
        angle = int([line for line in osd.split('\n')
                    if 'Rotate' in line][0].split(':')[-1])
        if angle != 0:
            return img_pil.rotate(-angle, expand=True)
    except Exception:
        pass  # Si falla, seguimos con la imagen original
    return img_pil


def estimate_psm_for_page(img_pil: Image.Image) -> int:
    """
    Estima automáticamente el valor de PSM (Page Segmentation Mode) para Tesseract
    según las características visuales de la imagen renderizada.

    Heurística:
        - Pocas líneas -> PSM 7 (una sola línea)
        - Muchas columnas visibles -> PSM 4 (flujo de columnas)
        - Distribución moderada -> PSM 6 (bloques uniformes)
        - Muy ruidoso o disperso -> PSM 11 (OCR general)

    Args:
        img_pil (Image.Image): Imagen renderizada de la página.

    Returns:
        int: Valor de PSM sugerido.
    """
    img = np.array(img_pil.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(
        255 - binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_boxes = len(contours)

    if num_boxes < 5:
        return 7
    elif num_boxes > 50:
        return 11
    elif 20 < num_boxes <= 50:
        return 4
    else:
        return 6
