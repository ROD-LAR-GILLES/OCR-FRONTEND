# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/tables.py
#  Python 3.11 • Detección y extracción de tablas
# ──────────────────────────────────────────────────────────────

"""
Funciones especializadas en la detección y extracción de tablas.
"""

from io import BytesIO
import cv2
import fitz
import numpy as np
from PIL import Image
from pytesseract import image_to_string

from .config import build_tesseract_config, DPI


def detect_table_regions(img: Image.Image):
    """
    Detecta regiones candidatas a ser tablas en la imagen (PIL) y retorna una lista de cajas (left, upper, right, lower).
    """
    img_gray = np.array(img.convert("L"))
    _, binary = cv2.threshold(
        img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Detección de líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horizontal_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    table_mask = cv2.add(horizontal_lines, vertical_lines)
    contours, _ = cv2.findContours(
        table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(cnt) for cnt in contours]
    # Opcional: filtrar por tamaño mínimo
    boxes = [box for box in boxes if box[2] > 50 and box[3] > 30]
    # Convertir a formato PIL: (left, upper, right, lower)
    regions = [(x, y, x + w, y + h) for (x, y, w, h) in boxes]
    return regions


def ocr_table_to_markdown(img: Image.Image) -> str:
    """
    Aplica OCR sobre una imagen de tabla y la convierte a formato Markdown simple.
    """
    config = build_tesseract_config(6)
    raw_text = image_to_string(img, lang="spa", config=config)
    lines = raw_text.strip().splitlines()
    lines = [line for line in lines if line.strip()]

    if len(lines) < 2:
        return ""

    # Separar por espacios o tabulaciones para obtener celdas
    header_cells = lines[0].split()
    header = "| " + " | ".join(header_cells) + " |"
    separator = "| " + " | ".join(["---"] * len(header_cells)) + " |"
    rows = []
    for line in lines[1:]:
        row_cells = line.split()
        # Si la fila tiene menos celdas que el header, rellenar
        if len(row_cells) < len(header_cells):
            row_cells += [""] * (len(header_cells) - len(row_cells))
        elif len(row_cells) > len(header_cells):
            row_cells = row_cells[:len(header_cells)]
        rows.append("| " + " | ".join(row_cells) + " |")
    return "\n".join([header, separator] + rows)


def has_visual_table(img_pil: Image.Image) -> bool:
    """
    Detecta si una imagen contiene una tabla visualmente, evaluando líneas horizontales/verticales.

    Args:
        img_pil (Image.Image): Imagen de la página.

    Returns:
        bool: True si se detecta estructura tabular, False si no.
    """
    img = np.array(img_pil.convert("L"))
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Detección de líneas
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=50, maxLineGap=10)
    if lines is None:
        return False

    horizontal = 0
    vertical = 0
    for x1, y1, x2, y2 in lines[:, 0]:
        if abs(y2 - y1) < 10:  # Horizontal
            horizontal += 1
        elif abs(x2 - x1) < 10:  # Vertical
            vertical += 1

    return horizontal >= 2 and vertical >= 2


def extract_tables_from_page(page: fitz.Page) -> list[str]:
    """
    Detecta visualmente tablas en una página PDF y extrae su contenido en formato Markdown.

    Returns:
        list[str]: Lista de tablas extraídas como strings Markdown.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))
    img_gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)

    # Binarización y detección de bordes
    _, binary = cv2.threshold(
        img_gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detección de líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

    detect_horizontal = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    detect_vertical = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    table_mask = cv2.add(detect_horizontal, detect_vertical)

    # Encontrar contornos (tablas candidatas)
    contours, _ = cv2.findContours(
        table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tables_md = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < 100 or h < 50:
            continue  # ignora cuadros pequeños

        table_img = img_gray[y:y + h, x:x + w]
        table_pil = Image.fromarray(table_img)
        md_table = ocr_table_to_markdown(table_pil)

        if md_table.strip():
            tables_md.append(md_table.strip())

    return tables_md
