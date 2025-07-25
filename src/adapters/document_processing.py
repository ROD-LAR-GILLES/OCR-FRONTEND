"""
Adaptadores para el procesamiento de documentos.

Este módulo contiene todas las implementaciones relacionadas con el procesamiento de documentos:
- Extracción de texto de PDFs
- OCR (Reconocimiento Óptico de Caracteres)
- Procesamiento en paralelo
- Detección de tablas
"""

from __future__ import annotations
import io
import os
from pathlib import Path
from typing import List, Tuple, Dict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

# Dependencias externas
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
import cv2
import numpy as np
from PIL import Image
from loguru import logger

# Imports internos
from shared.util.config import config, AppConfig
from .ocr import *  # Importamos del módulo OCR refactorizado
from .llm_services import LLMRefiner

# Instancia de configuración
app_config = AppConfig()

# Alias para compatibilidad con código anterior
perform_ocr_on_page = extract_text_from_pdf

# ===== Detector de Tablas =====


@dataclass
class TableValidationResult:
    is_valid: bool
    confidence: float
    num_rows: int
    num_cols: int


class TableDetector:
    """
    Detector y validador de estructuras de tablas en imágenes.
    """

    def __init__(self):
        self.min_confidence = 0.7

    def validate_table_structure(self, region: np.ndarray) -> TableValidationResult:
        """Valida la estructura de una tabla candidata."""
        # Detectar líneas
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100,
                                minLineLength=100, maxLineGap=10)

        if lines is None:
            return TableValidationResult(False, 0.0, 0, 0)

        # Separar líneas horizontales y verticales
        h_lines = []
        v_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 10:  # horizontal
                h_lines.append((min(x1, x2), max(x1, x2), y1))
            elif abs(x2 - x1) < 10:  # vertical
                v_lines.append((x1, min(y1, y2), max(y1, y2)))

        # Calcular filas y columnas
        num_rows = len(set(l[2] for l in h_lines))
        num_cols = len(set(l[0] for l in v_lines))

        # Calcular confianza
        min_expected = 2  # mínimo 2 filas y 2 columnas
        confidence = min(
            1.0, (num_rows/min_expected + num_cols/min_expected) / 2)

        return TableValidationResult(
            is_valid=confidence >= self.min_confidence,
            confidence=confidence,
            num_rows=num_rows,
            num_cols=num_cols
        )


# ===== Funciones de OCR =====

def needs_ocr(page, threshold=10):
    """
    Determina si una página requiere OCR basado en la cantidad de texto extraíble.

    Args:
        page: Página de PyMuPDF
        threshold: Umbral mínimo de caracteres para considerar que no necesita OCR

    Returns:
        bool: True si necesita OCR, False si no
    """
    text = page.get_text().strip()
    return len(text) < threshold


def _ocr_single(args: tuple[str, int]) -> str:
    """
    Función auxiliar para procesamiento en paralelo.
    Ejecuta OCR en una sola página de un PDF.
    """
    pdf_path, page_idx = args
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_idx)
        return perform_ocr_on_page(page)


def run_parallel_ocr(pdf_path: Path) -> list[str]:
    """
    Ejecuta OCR en paralelo para todas las páginas de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF

    Returns:
        list[str]: Texto OCR por página, en orden
    """
    from loguru import logger
    import multiprocessing as mp

    with fitz.open(pdf_path) as doc:
        n_pages = len(doc)
        logger.info(f"Procesando {n_pages} páginas en paralelo")

        # Para evitar problemas en Windows, usar spawn
        ctx = mp.get_context('spawn')

        # Crear pool con máximo de cores físicos - 1 (para no bloquear)
        n_cores = max(1, os.cpu_count() or 2 - 1)
        logger.debug(f"Usando {n_cores} cores para OCR")

        tasks = [(str(pdf_path.absolute()), i) for i in range(n_pages)]
        with ProcessPoolExecutor(max_workers=n_cores, mp_context=ctx) as executor:
            results = list(executor.map(_ocr_single, tasks))

    return results


# ===== Extracción de Markdown =====

def extract_markdown(pdf_path: Path, use_ocr: bool = True) -> str:
    """
    Extrae el contenido de un PDF y lo convierte a formato Markdown.

    Args:
        pdf_path: Ruta al archivo PDF
        use_ocr: Si debe usar OCR cuando no hay texto seleccionable

    Returns:
        str: Contenido del PDF en formato Markdown
    """
    if not fitz:
        raise ImportError("PyMuPDF (fitz) no está instalado. "
                          "Instálalo con: pip install pymupdf")

    logger.info(f"Extrayendo contenido de {pdf_path}")

    # Comprobar si el archivo existe
    if not pdf_path.exists():
        logger.error(f"El archivo {pdf_path} no existe")
        return f"Error: El archivo {pdf_path} no existe"

    try:
        # Inicializar el refinador de LLM si está configurado
        llm_refiner = None
        if config.get("USE_LLM_REFINER", False):
            llm_refiner = LLMRefiner()

        # Procesar el PDF con o sin OCR
        if use_ocr:
            # Para PDFs grandes, procesamos en paralelo
            if pdf_path.stat().st_size > 5 * 1024 * 1024:  # 5MB
                logger.info(
                    f"PDF grande detectado, usando procesamiento paralelo")
                text_pages = run_parallel_ocr(pdf_path)
                result = "\n\n".join(text_pages)
            else:
                # Abrir el PDF
                doc = fitz.open(pdf_path)
                result = []

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    page_text = page.get_text().strip()

                    # Si no hay suficiente texto, aplicar OCR
                    if needs_ocr(page):
                        logger.info(f"Aplicando OCR a la página {page_num+1}")
                        page_text = perform_ocr_on_page(page)

                    result.append(page_text)

                doc.close()
                result = "\n\n".join(result)
        else:
            # Extracción simple sin OCR
            doc = fitz.open(pdf_path)
            result = "\n\n".join([page.get_text() for page in doc])
            doc.close()

        # Refinar con LLM si está disponible
        if llm_refiner:
            logger.info("Refinando texto con LLM")
            result = llm_refiner.refine(result)

        return result

    except Exception as e:
        logger.exception(f"Error procesando {pdf_path}: {e}")
        return f"Error: {str(e)}"
