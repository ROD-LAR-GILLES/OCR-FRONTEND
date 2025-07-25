"""
Parallel OCR helper (pickle-safe).

Each worker receives (pdf_path, page_index), opens the PDF locally,
and runs perform_ocr_on_page on that single page.
"""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import fitz  # PyMuPDF

from adapters.ocr_adapter import perform_ocr_on_page


def _ocr_single(args: tuple[str, int]) -> str:
    pdf_path, page_idx = args
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_idx)
        return perform_ocr_on_page(page)


def run_parallel(pdf_path: Path) -> list[str]:
    """
    Ejecuta OCR en paralelo para todas las páginas de *pdf_path*.

    Returns
    -------
    list[str]
        Texto OCR por página, en orden.
    """
    from loguru import logger
    
    pdf_path = str(pdf_path)  # asegurar serializable
    with fitz.open(pdf_path) as doc:
        total_pages = doc.page_count
        indices = list(range(total_pages))
        logger.info(f"Iniciando procesamiento OCR paralelo de {total_pages} páginas")

    results = []
    with ProcessPoolExecutor() as pool:
        futures = list(pool.map(_ocr_single, [(pdf_path, i) for i in indices]))
        for i, text in enumerate(futures, 1):
            results.append(text)
            progress = (i / total_pages) * 100
            logger.info(f"Progreso OCR: {progress:.1f}% ({i}/{total_pages} páginas)")
    
    return results