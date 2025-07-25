"""
Motor principal OCR y configuración.

Este módulo contiene el motor principal del OCR y la configuración central.
"""

import logging
from io import BytesIO
from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

from adapters.llm_services import LLMRefiner

# ───────────────────── CONFIGURACIÓN ─────────────────────
DPI = 300
TESSERACT_CONFIG = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG = "spa"
CORRECTIONS_PATH = Path("src/shared/storage/data/corrections.csv")

# Configurar logger
logger = logging.getLogger(__name__)

# Inicializar el refinador LLM
llm_refiner = LLMRefiner()


def build_tesseract_config(psm: int) -> str:
    """
    Construye la configuración de Tesseract OCR personalizada.

    Args:
        psm (int): Page Segmentation Mode para Tesseract.

    Returns:
        str: Cadena de configuración completa.
    """
    parts = [
        f"--psm {psm}",
        "--oem 3",
        f"-c user_defined_dpi={DPI}"
    ]

    # Archivos personalizados de usuario (si existen)
    words_path = Path("src/shared/storage/data/legal_words.txt")
    patterns_path = Path("src/shared/storage/data/legal_patterns.txt")

    if words_path.exists():
        parts.append(f"--user-words {words_path}")
    if patterns_path.exists():
        parts.append(f"--user-patterns {patterns_path}")

    return " ".join(parts)


def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página PDF.

    Args:
        page: Página PDF de PyMuPDF

    Returns:
        str: Texto extraído y procesado
    """
    # Importar aquí para evitar referencias circulares
    from .ocr_image import correct_rotation, estimate_psm_for_page, has_visual_table
    from .ocr_image import extract_tables_from_page, ocr_table_to_markdown, create_mask_without_tables
    from .ocr_text import cleanup_text, apply_manual_corrections, detect_lists, detect_structured_headings

    # 1) Render
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_data = pix.tobytes("png")
    img = Image.open(BytesIO(img_data))

    # 2) Corregir rotación automáticamente
    img = correct_rotation(img)

    # 3) Detectar el mejor PSM (modo de segmentación de página)
    psm = estimate_psm_for_page(page, img)
    config = build_tesseract_config(psm)

    # 4) Detectar si hay tablas
    has_tables = has_visual_table(img)

    # 5) Ejecutar OCR
    logger.info(f"Ejecutando OCR con config: {config}")
    if has_tables:
        # Extraer tablas primero
        logger.info("Página contiene tablas. Extrayendo...")
        tables = extract_tables_from_page(img)
        if tables:
            # Convertir tablas a Markdown
            table_md = "\n\n".join([ocr_table_to_markdown(t) for t in tables])
            logger.info(f"Tablas extraídas: {len(tables)}")

            # Ejecutar OCR en el resto de la página (sin tablas)
            mask = create_mask_without_tables(img, tables)
            text = pytesseract.image_to_string(
                mask, lang=OCR_LANG, config=config)

            # Combinar texto y tablas
            result = f"{text}\n\n{table_md}"
        else:
            # Si falló la extracción de tablas, procesar toda la página
            text = pytesseract.image_to_string(
                img, lang=OCR_LANG, config=config)
            result = text
    else:
        # OCR normal (sin tablas)
        text = pytesseract.image_to_string(img, lang=OCR_LANG, config=config)
        result = text

    # 6) Postprocesamiento
    result = cleanup_text(result)
    result = apply_manual_corrections(result)

    # 7) Detección y formato de listas
    result = detect_lists(result)

    # 8) Detección de encabezados estructurados
    result = detect_structured_headings(result)

    # 9) Refinamiento LLM (opcional)
    if llm_refiner.is_enabled():
        try:
            refined_text = llm_refiner.refine_ocr_text(result)
            if refined_text:
                logger.info("Texto refinado por LLM")
                result = refined_text
        except Exception as e:
            logger.error(f"Error en refinamiento LLM: {e}")

    return result


def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR revisando si contiene texto seleccionable.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        bool: True si no hay texto y se debe aplicar OCR.
    """
    text = page.get_text().strip()
    return len(text) < 50  # Si hay menos de 50 caracteres, aplicar OCR


def extract_blocks(page: fitz.Page) -> list:
    """
    Extrae bloques de texto de la página.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        list: Lista de bloques de texto.
    """
    return page.get_text("blocks")


def extract_text_from_pdf(page: fitz.Page) -> str:
    """
    Extrae texto de una página PDF usando OCR si es necesario.

    Args:
        page (fitz.Page): Página de PDF a procesar

    Returns:
        str: Texto extraído y procesado
    """
    return perform_ocr_on_page(page)


def extract_text_from_image(image_path: str) -> str:
    """
    Extrae texto de una imagen usando OCR.

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        str: Texto extraído y procesado
    """
    # Importar aquí para evitar referencias circulares
    from .ocr_text import cleanup_text, apply_manual_corrections

    img = Image.open(image_path)
    config = build_tesseract_config(6)  # PSM 6 para imágenes
    text = pytesseract.image_to_string(img, lang=OCR_LANG, config=config)

    # Postprocesamiento
    text = cleanup_text(text)
    text = apply_manual_corrections(text)

    return text


def process_pdf_file(pdf_path: str) -> dict:
    """
    Procesa un archivo PDF completo.

    Args:
        pdf_path (str): Ruta al archivo PDF

    Returns:
        dict: Diccionario con el texto extraído por página
    """
    result = {}
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            page_num = i + 1
            logger.info(f"Procesando página {page_num}/{len(doc)}")

            if needs_ocr(page):
                logger.info(f"Aplicando OCR a la página {page_num}")
                text = perform_ocr_on_page(page)
            else:
                logger.info(
                    f"Extrayendo texto existente de la página {page_num}")
                text = page.get_text()

            result[page_num] = text

        doc.close()
        return result
    except Exception as e:
        logger.error(f"Error procesando PDF {pdf_path}: {e}")
        return {"error": str(e)}


def visualize_ocr_regions(img: Image.Image, regions: list) -> Image.Image:
    """
    Visualiza regiones OCR sobre la imagen para depuración.

    Args:
        img (Image.Image): Imagen original.
        regions (list): Lista de regiones (x, y, w, h).

    Returns:
        Image.Image: Imagen con regiones marcadas.
    """
    img_np = np.array(img.copy())
    for x, y, w, h in regions:
        cv2.rectangle(img_np, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return Image.fromarray(img_np)
