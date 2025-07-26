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
from infrastructure.document_adapter import DocumentAdapter

# Importaciones de configuración
from interfaces.config_menu import ConfigMenu
from config import config

# ───────────────────────── Inicialización ──────────────────────────
# Crear instancias necesarias
storage_adapter = StorageAdapter()
document_adapter = DocumentAdapter()

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
    print(f"\nIniciando procesamiento de: {pdf_path.name}")
    print("-" * 60)

    logger.info(f"Convirtiendo a Markdown: {pdf_path}")
    try:
        # Paso 1: Validar el PDF
        print("Paso 1/4: Validando PDF...")
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=document_adapter)
        validation_result = validate_pdf_use_case.execute(pdf_path)

        if not validation_result["valid"]:
            print(f"[ERROR] PDF inválido: {validation_result['message']}")
            return

        print(f"[OK] {validation_result['message']}")
        print(f"Páginas totales: {validation_result['total_pages']}")
        print(f"Páginas digitales: {validation_result['digital_pages']}")
        print(f"Páginas escaneadas: {validation_result['scanned_pages']}")

        # Paso 2: Preparar procesamiento
        print("\nPaso 2/4: Preparando procesamiento...")
        pdf_to_markdown_use_case = PDFToMarkdownUseCase(
            document_port=document_adapter,
            storage_port=storage_adapter,
            llm_port=None  # TODO: Implementar LLMPort
        )
        print("[OK] Casos de uso inicializados")

        # Paso 3: Extraer contenido
        print("\nPaso 3/4: Extrayendo contenido del PDF...")
        print("   - Analizando estructura del documento...")
        markdown_content = extract_markdown(pdf_path)

        if len(markdown_content) > 1000:
            preview = markdown_content[:200] + "..."
        else:
            preview = markdown_content[:200]

        print(f"[OK] Contenido extraído ({len(markdown_content)} caracteres)")
        print(f"Vista previa: {preview}")

        # Paso 4: Guardar resultado
        print("\nPaso 4/4: Guardando resultado...")
        output_path = storage_adapter.save_markdown(
            pdf_path.stem, markdown_content)

        print("-" * 60)
        print(f"[SUCCESS] Procesamiento completado exitosamente!")
        print(f"Archivo generado: {output_path}")
        print(f"Tamaño del contenido: {len(markdown_content)} caracteres")

    except Exception as e:
        logger.exception("Error en la conversión de PDF")
        print(f"\n[ERROR] Fallo en la conversión: {e}")
        print("Revisa los logs para más detalles")


def _show_cache_stats() -> None:
    """Muestra estadísticas de la caché OCR."""
    print("\nObteniendo estadísticas de caché...")
    try:
        stats = ocr_cache.get_stats()
        print("\n=== Estadísticas de Caché OCR ===")
        print("-" * 40)
        print(f"Total de entradas: {stats.get('total_entries', 0)}")

        size_kb = stats.get('total_text_size_bytes', 0) / 1024
        print(f"Tamaño aproximado: {size_kb:.2f} KB")

        last_update = stats.get('last_update', 'Nunca')
        print(f"Última actualización: {last_update}")

        memory_size = stats.get('memory_cache_size', 0)
        print(f"Caché en memoria: {memory_size} entradas")

        if stats.get('total_entries', 0) > 0:
            print("[INFO] La caché está optimizando el rendimiento del OCR")
        else:
            print("[INFO] La caché está vacía - se poblará con el uso")

    except Exception as e:
        logger.exception("Error obteniendo estadísticas de caché")
        print(f"[ERROR] Error al obtener estadísticas: {e}")
        print("Revisa los logs para más detalles")


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
        print("\n[INFO] No se encontraron PDFs en el directorio ./pdfs")
        print("[TIP] Coloca archivos PDF en el directorio 'pdfs' para procesarlos")
        return None

    print(
        f"\nPDFs disponibles ({len(files)} archivo{'s' if len(files) != 1 else ''}):")
    print("-" * 60)
    for i, pdf in enumerate(files, 1):
        # Obtener información adicional del archivo
        pdf_path = PDF_DIR / pdf
        try:
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            size_str = f"({size_mb:.1f} MB)"
        except:
            size_str = "(tamaño desconocido)"

        print(f"  {i:2d}. {pdf} {size_str}")

    print("-" * 60)

    try:
        sel = input("Seleccione un número: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            selected_file = files[int(sel) - 1]
            print(f"[OK] Seleccionado: {selected_file}")
            return selected_file
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
                print("\nEscaneando directorio de PDFs...")
                files = list_pdfs()
                if files:
                    print(
                        f"\nPDFs encontrados ({len(files)} archivo{'s' if len(files) != 1 else ''}):")
                    print("-" * 50)
                    for i, pdf in enumerate(files, 1):
                        # Obtener tamaño del archivo
                        pdf_path = PDF_DIR / pdf
                        try:
                            size_mb = pdf_path.stat().st_size / (1024 * 1024)
                            size_str = f"({size_mb:.1f} MB)"
                        except:
                            size_str = "(tamaño desconocido)"

                        print(f"  {i:2d}. {pdf} {size_str}")
                    print("-" * 50)
                    print(
                        f"[INFO] Usa la opción 2 para procesar cualquiera de estos archivos")
                else:
                    print(
                        "\n[INFO] No se encontraron PDFs en el directorio ./pdfs")
                    print(
                        "[TIP] Coloca archivos PDF en el directorio 'pdfs' para procesarlos")
            case "2":
                if pdf := select_pdf():
                    _convert_pdf(PDF_DIR / pdf)
            case "3":
                if pdf := select_pdf():
                    print(f"\nValidando PDF: {pdf}")
                    print("-" * 50)
                    try:
                        print("Analizando estructura del documento...")
                        validate_pdf_use_case = ValidatePDFUseCase(
                            document_port=document_adapter)
                        result = validate_pdf_use_case.execute(PDF_DIR / pdf)

                        print("\n=== Resultados de validación ===")
                        status = "[OK]" if result['valid'] else "[ERROR]"
                        print(
                            f"{status} Validez: {'Válido' if result['valid'] else 'Inválido'}")
                        print(f"Mensaje: {result['message']}")
                        print(f"Páginas totales: {result['total_pages']}")
                        print(f"Páginas digitales: {result['digital_pages']}")
                        print(f"Páginas escaneadas: {result['scanned_pages']}")

                        if result['valid']:
                            print(
                                "[INFO] El documento está listo para procesamiento")
                        else:
                            print(
                                "[WARNING] El documento requiere revisión antes del procesamiento")

                    except Exception as e:
                        logger.exception("Error en la validación de PDF")
                        print(f"[ERROR] Error al validar PDF: {e}")
                        print("Revisa los logs para más detalles")
            case "4":
                ConfigMenu.show_provider_menu()
            case "5":
                _show_cache_stats()
            case "6":
                print("\nHasta luego!")
                sys.exit(0)
            case _:
                print("[ERROR] Opción inválida")
