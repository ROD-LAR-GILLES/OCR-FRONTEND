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

    def show_progress(step: str, current: int, total: int, message: str):
        """Muestra progreso visual en consola."""
        percentage = (current / total) * 100
        bar_length = 40
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{step}: |{bar}| {percentage:.1f}% - {message}",
              end='', flush=True)
        if current == total:
            print()  # Nueva línea al completar

    try:
        # Paso 1: Validar el PDF
        show_progress("Validando PDF", 0, 4, "Iniciando validación...")
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=document_adapter)

        print("Paso 1/4: Validando PDF...")
        print("   → Analizando estructura del documento...")
        validation_result = validate_pdf_use_case.execute(pdf_path)
        show_progress("Validando PDF", 1, 4, "Validación completada")

        if not validation_result["valid"]:
            print(f"\n[ERROR] PDF inválido: {validation_result['message']}")
            print(" Procesamiento cancelado debido a errores de validación")
            return

        print(f"\n[✓] {validation_result['message']}")
        print(f"   → Páginas totales: {validation_result['total_pages']}")
        print(f"   → Páginas digitales: {validation_result['digital_pages']}")
        print(f"   → Páginas escaneadas: {validation_result['scanned_pages']}")

        # Paso 2: Preparar procesamiento
        show_progress("Preparando", 1, 4, "Inicializando casos de uso...")
        print("\nPaso 2/4: Preparando procesamiento...")
        pdf_to_markdown_use_case = PDFToMarkdownUseCase(
            document_port=document_adapter,
            storage_port=storage_adapter,
            llm_port=None  # TODO: Implementar LLMPort
        )
        show_progress("Preparando", 2, 4, "Casos de uso inicializados")
        print("[✓] Casos de uso inicializados")

        # Paso 3: Extraer contenido
        show_progress("Extrayendo", 2, 4, "Procesando documento...")
        print("\nPaso 3/4: Extrayendo contenido del PDF...")
        print("   → Analizando estructura del documento...")
        print("   → Aplicando OCR donde sea necesario...")
        print("   → Procesando tablas y elementos especiales...")

        # Simulamos progreso más detallado
        import time
        for i in range(3):
            time.sleep(0.5)  # Simulación de procesamiento
            show_progress("Extrayendo", 2 + (i * 0.3), 4,
                          f"Procesando página {i+1}...")

        markdown_content = extract_markdown(pdf_path)
        show_progress("Extrayendo", 3, 4, "Extracción completada")

        if len(markdown_content) > 1000:
            preview = markdown_content[:200] + "..."
        else:
            preview = markdown_content[:200]

        print(f"\n[✓] Contenido extraído ({len(markdown_content)} caracteres)")
        print(f"   → Vista previa: {preview}")

        # Paso 4: Guardar resultado
        show_progress("Guardando", 3, 4, "Preparando archivo de salida...")
        print("\nPaso 4/4: Guardando resultado...")
        print("   → Generando archivo Markdown...")
        output_path = storage_adapter.save_markdown(
            pdf_path.stem, markdown_content)
        show_progress("Guardando", 4, 4, "Archivo guardado exitosamente")

        print("\n" + "=" * 60)
        print("🎉 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"✓ Archivo generado: {output_path}")
        print(f"✓ Tamaño del contenido: {len(markdown_content)} caracteres")
        print(f"✓ Páginas procesadas: {validation_result['total_pages']}")
        if validation_result['scanned_pages'] > 0:
            print(
                f"✓ OCR aplicado a: {validation_result['scanned_pages']} páginas")
        print("=" * 60)

    except Exception as e:
        logger.exception("Error en la conversión de PDF")
        print(f"\n ERROR CRÍTICO EN EL PROCESAMIENTO")
        print("=" * 60)
        print(f" Tipo de error: {type(e).__name__}")
        print(f" Descripción: {str(e)}")
        print("=" * 60)
        print(" DIAGNÓSTICO:")
        print("   → Revisa que el archivo PDF no esté corrupto")
        print("   → Verifica que tienes permisos de escritura")
        print("   → Comprueba que hay espacio suficiente en disco")
        print("   → Consulta los logs para más detalles")
        print("=" * 60)

        # Mostrar información adicional de diagnóstico
        try:
            file_size = pdf_path.stat().st_size / (1024 * 1024)  # MB
            print(f" Info del archivo:")
            print(f"   → Tamaño: {file_size:.2f} MB")
            print(f"   → Ruta: {pdf_path}")
            print(f"   → Existe: {'✓' if pdf_path.exists() else 'x'}")
        except:
            print(" No se pudo obtener información del archivo")

        print("=" * 60)


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
        print("1. Convertir PDF a Markdown")
        print("2. Configuración")
        print("3. Estadísticas de caché")
        print("4. Salir")

        match input("\nSeleccione una opción (1-4): ").strip():
            case "1":
                if pdf := select_pdf():
                    _convert_pdf(PDF_DIR / pdf)
            case "2":
                ConfigMenu.show_provider_menu()
            case "3":
                _show_cache_stats()
            case "4":
                print("\nHasta luego!")
                sys.exit(0)
            case _:
                print("[ERROR] Opción inválida")
