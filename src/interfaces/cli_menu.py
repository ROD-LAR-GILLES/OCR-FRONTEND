"""
OCR-PYMUPDF - Interfaz de línea de comandos.

Esta interfaz proporciona acceso interactivo a todas las funciones
del sistema OCR, incluyendo:
1. Listado y selección de PDFs
2. Conversión a Markdown
3. Validación de documentos
4. Configuración del sistema
5. Gestión de caché OCR
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
# Importaciones del dominio
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.use_cases.validate_pdf import ValidatePDFUseCase

# Importaciones de adaptadores
from adapters.pymupdf_adapter import extract_markdown
from adapters import LLMProviderFactory, get_language_detector

# Importaciones de infraestructura
from infrastructure import logger, ocr_cache
from infrastructure.storage_adapter import StorageAdapter

# Importaciones de configuración
from interfaces.config_menu import ConfigMenu
from config import config

# ───────────────────────── Inicialización ──────────────────────────
# Crear instancias necesarias
storage_adapter = StorageAdapter()

# ───────────────────────── Helpers ──────────────────────────


def _show_llm_status() -> None:
    """Muestra el estado actual de la configuración LLM."""
    provider = config.llm_provider
    if not provider:
        provider = "auto"

    mode = config.llm_mode
    status = "Desactivado" if mode == "off" else f"Activado ({provider}, modo: {mode})"
    print(f"\nProcesamiento LLM: {status}")


def _convert_pdf(pdf_path: Path) -> None:
    """
    Convierte un PDF a Markdown usando los casos de uso del dominio.

    Args:
        pdf_path: Ruta al archivo PDF a convertir
    """
    logger.info(f"Convirtiendo a Markdown: {pdf_path}")
    try:
        # Validar el PDF primero
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=None)  # TODO: Implementar DocumentPort
        validation_result = validate_pdf_use_case.execute(pdf_path)

        if not validation_result["valid"]:
            print(f"[ERROR] PDF inválido: {validation_result['message']}")
            return

        print(f"[INFO] {validation_result['message']}")
        print(f"[INFO] Páginas totales: {validation_result['total_pages']}")
        print(
            f"[INFO] Páginas digitales: {validation_result['digital_pages']}")
        print(
            f"[INFO] Páginas escaneadas: {validation_result['scanned_pages']}")

        # Crear y ejecutar el caso de uso
        pdf_to_markdown_use_case = PDFToMarkdownUseCase(
            document_port=None,  # TODO: Implementar DocumentPort
            storage_port=storage_adapter,
            llm_port=None  # TODO: Implementar LLMPort
        )

        # Temporalmente, hasta que se completen los puertos
        # Extraer contenido markdown del PDF
        markdown_content = extract_markdown(pdf_path)

        # Guardar el resultado
        output_path = storage_adapter.save_markdown(
            pdf_path.stem, markdown_content)
        print(f"[OK] Markdown generado: {output_path}")

    except Exception as e:
        logger.exception("Error en la conversión de PDF")
        print(f"[ERROR] Fallo en la conversión: {e}")


def _show_cache_stats() -> None:
    """Muestra estadísticas de la caché OCR."""
    stats = ocr_cache.get_stats()
    print("\n=== Estadísticas de Caché OCR ===")
    print(f"Total de entradas: {stats.get('total_entries', 0)}")
    print(
        f"Tamaño aproximado: {stats.get('total_text_size_bytes', 0) / 1024:.2f} KB")
    print(f"Última actualización: {stats.get('last_update', 'Nunca')}")
    print(f"Caché en memoria: {stats.get('memory_cache_size', 0)} entradas")


# ───────────────────────── Gestión de PDFs ──────────────────────────
PDF_DIR = Path("pdfs")
PDF_DIR.mkdir(exist_ok=True)


def list_pdfs() -> List[str]:
    """Lista los PDFs disponibles en el directorio pdfs."""
    return [p.name for p in sorted(PDF_DIR.glob("*.pdf"))]


def select_pdf() -> Optional[str]:
    """Muestra un menú de selección de PDF."""
    files = list_pdfs()
    if not files:
        print("[INFO] No se encontraron PDFs en el directorio ./pdfs")
        return None

    print("\nAvailable PDFs:")
    for i, pdf in enumerate(files, 1):
        print(f"{i}. {pdf}")

    try:
        sel = input("\nSeleccione un número: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            return files[int(sel) - 1]
        print("[ERROR] Selección inválida")
        return None
    except (ValueError, IndexError):
        print("[ERROR] Selección inválida")
        return None

# ───────────────────────── Main Menu ──────────────────────────


def main_loop() -> None:
    """Bucle principal del menú con configuración LLM integrada."""
    while True:
        print("\n=== OCR-PYMUPDF ===")
        _show_llm_status()
        print("\nOpciones disponibles:")
        print("1. Listar PDFs")
        print("2. Convertir PDF a Markdown")
        print("3. Validar PDF")
        print("4. Configuración")
        print("5. Estadísticas de caché")
        print("6. Salir")

        match input("\nSeleccione una opción (1-6): ").strip():
            case "1":
                files = list_pdfs()
                if files:
                    print("\nPDFs encontrados:")
                    for pdf in files:
                        print(f" - {pdf}")
                else:
                    print("[INFO] No se encontraron PDFs en el directorio ./pdfs")
            case "2":
                if pdf := select_pdf():
                    _convert_pdf(PDF_DIR / pdf)
            case "3":
                if pdf := select_pdf():
                    try:
                        validate_pdf_use_case = ValidatePDFUseCase(
                            document_port=None)
                        result = validate_pdf_use_case.execute(PDF_DIR / pdf)

                        print("\n=== Resultados de validación ===")
                        print(
                            f"Validez: {'Válido' if result['valid'] else 'Inválido'}")
                        print(f"Mensaje: {result['message']}")
                        print(f"Páginas totales: {result['total_pages']}")
                        print(f"Páginas digitales: {result['digital_pages']}")
                        print(f"Páginas escaneadas: {result['scanned_pages']}")
                    except Exception as e:
                        logger.exception("Error en la validación de PDF")
                        print(f"[ERROR] Error al validar PDF: {e}")
            case "4":
                ConfigMenu.show_provider_menu()
            case "5":
                _show_cache_stats()
            case "6":
                print("\n¡Hasta luego!")
                sys.exit(0)
            case _:
                print("[ERROR] Opción inválida")
