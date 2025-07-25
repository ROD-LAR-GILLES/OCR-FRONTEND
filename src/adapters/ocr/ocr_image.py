"""
Procesamiento de imágenes y tablas para OCR.

Este módulo contiene funciones para procesamiento de imágenes y detección/extracción de tablas.
"""

import logging
import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

from .ocr_engine import DPI, OCR_LANG, build_tesseract_config

# Configurar logger
logger = logging.getLogger(__name__)


def correct_rotation(img_pil: Image.Image) -> Image.Image:
    """
    Corrige la rotación de una imagen usando detección automática vía Tesseract OSD.

    Args:
        img_pil (Image.Image): Imagen original.

    Returns:
        Image.Image: Imagen rotada si se detectó desviación de ángulo.
    """
    try:
        img_np = np.array(img_pil)

        # Convertir a escala de grises si es necesario
        if len(img_np.shape) == 3 and img_np.shape[2] == 3:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Detectar orientación con Tesseract OSD
        osd = pytesseract.image_to_osd(img_np)
        angle = int(osd.split('Rotate: ')[1].split('\n')[0])

        if angle != 0:
            logger.info(f"Corrigiendo rotación: {angle}°")
            if angle == 90:
                img_pil = img_pil.transpose(Image.ROTATE_90)
            elif angle == 180:
                img_pil = img_pil.transpose(Image.ROTATE_180)
            elif angle == 270:
                img_pil = img_pil.transpose(Image.ROTATE_270)

        return img_pil
    except Exception as e:
        logger.warning(f"Error detectando rotación: {e}")
        return img_pil


def estimate_psm_for_page(page: fitz.Page, img: Image.Image) -> int:
    """
    Estima el mejor Page Segmentation Mode (PSM) para una página.

    Args:
        page (fitz.Page): Página PDF
        img (Image.Image): Imagen renderizada

    Returns:
        int: PSM recomendado (1-13)
    """
    # Análisis simplificado: intentar inferir si es página única o columnas
    width, height = img.size
    aspect_ratio = width / height

    # Verificar si tiene bloques de texto o si es mayormente imagen
    text = page.get_text().strip()
    text_blocks = page.get_text("blocks")
    has_text = len(text) > 100
    block_count = len(text_blocks)

    # Detectar posible estructura de columnas
    columns = 1
    if block_count > 3:
        # Analizar distribución horizontal de bloques
        x_positions = []
        for block in text_blocks:
            x_positions.append(block[0])  # x0
            x_positions.append(block[2])  # x1

        x_positions.sort()
        x_ranges = set()
        for pos in x_positions:
            range_id = int(pos / (width * 0.2))  # Dividir en 5 rangos
            x_ranges.add(range_id)

        if len(x_ranges) >= 3:
            columns = 2

    # Seleccionar PSM basado en análisis
    if not has_text:
        return 3  # Auto + OSD (para páginas sin texto o con poco texto)
    elif columns > 1:
        return 1  # Auto con orientación y OSD (páginas con columnas)
    elif aspect_ratio > 1.3:
        return 6  # Bloque uniforme de texto (para páginas regulares)
    else:
        return 4  # Texto continuo (para páginas con párrafos grandes)


def has_visual_table(img: Image.Image) -> bool:
    """
    Detecta si una imagen probablemente contiene tablas usando análisis visual.

    Args:
        img (Image.Image): Imagen a analizar

    Returns:
        bool: True si se detectaron posibles tablas
    """
    # Convertir a escala de grises y binarizar
    img_gray = np.array(img.convert("L"))
    _, binary = cv2.threshold(
        img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detectar líneas horizontales y verticales (características de tablas)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)

    # Combinar para detectar intersecciones
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    # Contar píxeles de líneas
    line_pixels = cv2.countNonZero(table_mask)
    total_pixels = img_gray.size

    # Si hay suficientes líneas en proporción al tamaño, probablemente hay tabla
    line_ratio = line_pixels / total_pixels

    return line_ratio > 0.005  # Umbral ajustable


def detect_table_regions(img: Image.Image) -> list:
    """
    Detecta regiones candidatas a ser tablas en la imagen.

    Args:
        img (Image.Image): Imagen a analizar

    Returns:
        list: Lista de coordenadas de tablas [(x, y, w, h), ...]
    """
    img_gray = np.array(img.convert("L"))
    _, binary = cv2.threshold(
        img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detectar líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)

    # Combinar líneas
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    # Dilatar para conectar regiones cercanas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    table_mask = cv2.dilate(table_mask, kernel, iterations=3)

    # Encontrar contornos de posibles tablas
    contours, _ = cv2.findContours(
        table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar contornos pequeños
    min_area = img_gray.size * 0.005  # Área mínima (0.5% de la imagen)
    table_regions = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h >= min_area:
            # Expandir un poco los límites para asegurar capturar toda la tabla
            x = max(0, x - 10)
            y = max(0, y - 10)
            w = min(img_gray.shape[1] - x, w + 20)
            h = min(img_gray.shape[0] - y, h + 20)
            table_regions.append((x, y, w, h))

    return table_regions


def extract_tables_from_page(img: Image.Image) -> list:
    """
    Extrae imágenes de tablas de una página.

    Args:
        img (Image.Image): Imagen de la página

    Returns:
        list: Lista de imágenes de tablas (PIL.Image)
    """
    table_regions = detect_table_regions(img)
    if not table_regions:
        return []

    # Extraer imágenes de tablas
    table_images = []
    for x, y, w, h in table_regions:
        table_img = img.crop((x, y, x + w, y + h))
        table_images.append(table_img)

    return table_images


def create_mask_without_tables(img: Image.Image, table_regions: list) -> Image.Image:
    """
    Crea una máscara para procesar la imagen sin las regiones de tablas.

    Args:
        img (Image.Image): Imagen original
        table_regions (list): Lista de coordenadas de tablas [(x, y, w, h), ...]

    Returns:
        Image.Image: Imagen con regiones de tablas enmascaradas
    """
    mask = np.array(img.copy())

    # Pintar de blanco las regiones de tablas
    for table_img in table_regions:
        x, y, w, h = table_img.getbbox()
        mask[y:y+h, x:x+w] = 255

    return Image.fromarray(mask)


def ocr_table_to_markdown(table_img: Image.Image) -> str:
    """
    Convierte una imagen de tabla a formato Markdown.

    Args:
        table_img (Image.Image): Imagen de la tabla

    Returns:
        str: Tabla en formato Markdown
    """
    # Detección de celdas
    cells = detect_table_cells(table_img)
    if not cells:
        # Si no se detectaron celdas, intentar OCR directo
        text = pytesseract.image_to_string(
            table_img, lang=OCR_LANG, config='--psm 6')
        return f"```\n{text}\n```"

    # Extraer texto de cada celda
    rows = {}
    for (row, col), cell_img in cells.items():
        text = pytesseract.image_to_string(
            cell_img, lang=OCR_LANG, config='--psm 6').strip()
        if row not in rows:
            rows[row] = {}
        rows[row][col] = text

    # Determinar número de columnas
    max_cols = 0
    for row_data in rows.values():
        max_cols = max(max_cols, max(row_data.keys(), default=0) + 1)

    # Generar markdown
    md_table = []

    # Encabezados
    header_row = " | ".join(["Columna " + str(i+1) for i in range(max_cols)])
    md_table.append(header_row)

    # Separador
    separator = " | ".join(["---" for _ in range(max_cols)])
    md_table.append(separator)

    # Filas de datos
    for row_idx in sorted(rows.keys()):
        cols = []
        for col_idx in range(max_cols):
            cell_text = rows[row_idx].get(col_idx, "")
            cols.append(cell_text)
        md_table.append(" | ".join(cols))

    return "\n".join(md_table)


def detect_table_cells(table_img: Image.Image) -> dict:
    """
    Detecta celdas individuales en una imagen de tabla.

    Args:
        table_img (Image.Image): Imagen de la tabla

    Returns:
        dict: Diccionario {(fila, columna): imagen_celda}
    """
    # Convertir a escala de grises y binarizar
    img_gray = np.array(table_img.convert("L"))
    _, binary = cv2.threshold(
        img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detectar líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)

    # Combinar líneas
    grid_lines = cv2.add(horizontal_lines, vertical_lines)

    # Dilatar líneas para asegurar conexiones
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    grid_lines = cv2.dilate(grid_lines, kernel, iterations=1)

    # Encontrar contornos de celdas (áreas encerradas por líneas)
    # Invertir la imagen para encontrar áreas encerradas
    inverted_grid = cv2.bitwise_not(grid_lines)
    contours, _ = cv2.findContours(
        inverted_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar contornos pequeños
    min_area = 100  # Área mínima para considerar una celda
    cell_contours = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            cell_contours.append(contour)

    # Si no hay suficientes celdas, probablemente no es una tabla estructurada
    if len(cell_contours) < 4:  # Mínimo para una tabla 2x2
        return {}

    # Extraer coordenadas de celdas y ordenarlas por posición
    cell_coords = []
    for contour in cell_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cell_coords.append((x, y, w, h))

    # Ordenar por coordenada Y para agrupar filas
    cell_coords.sort(key=lambda c: c[1])

    # Agrupar celdas en filas
    rows = []
    current_row = []
    current_y = cell_coords[0][1]

    for cell in cell_coords:
        x, y, w, h = cell
        # Si el cambio en Y es significativo, es una nueva fila
        if abs(y - current_y) > 10:
            if current_row:
                # Ordenar la fila actual por X antes de añadirla
                current_row.sort(key=lambda c: c[0])
                rows.append(current_row)
            current_row = [cell]
            current_y = y
        else:
            current_row.append(cell)

    # Añadir la última fila
    if current_row:
        current_row.sort(key=lambda c: c[0])
        rows.append(current_row)

    # Convertir a diccionario de celdas {(fila, columna): imagen}
    cells = {}
    table_img_np = np.array(table_img)

    for row_idx, row in enumerate(rows):
        for col_idx, (x, y, w, h) in enumerate(row):
            # Recortar la celda
            cell_img = table_img_np[y:y+h, x:x+w]
            cells[(row_idx, col_idx)] = Image.fromarray(cell_img)

    return cells
