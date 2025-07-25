"""
Processing Module - Funciones de procesamiento de documentos PDF.
"""

import time
from pathlib import Path

# Importaciones de la aplicación
from application.composition_root import DependencyContainer, composition_root

# Importaciones de infraestructura
from infrastructure.logging_setup import logger

# Importaciones locales
from .utils import show_progress, print_success_summary, print_error_details

# Crear contenedor de dependencias
container = DependencyContainer()


def convert_pdf(pdf_path: Path) -> None:
    """
    Convierte un PDF a Markdown usando los casos de uso del dominio.

    Args:
        pdf_path: Ruta al archivo PDF a procesar
    """
    try:
        # Paso 1: Validar PDF
        validation_result = _validate_pdf_step(pdf_path)

        # Paso 2: Preparar procesamiento
        _prepare_processing_step()

        # Paso 3: Extraer contenido
        markdown_content = _extract_content_step(pdf_path)

        # Paso 4: Guardar resultado
        output_path = _save_result_step(pdf_path, markdown_content)

        # Mostrar resumen de éxito
        print_success_summary(output_path, len(
            markdown_content), validation_result)

    except Exception as e:
        logger.exception("Error en la conversión de PDF")
        print_error_details(e, pdf_path)


def _validate_pdf_step(pdf_path: Path) -> dict:
    """Ejecuta el paso de validación del PDF."""
    show_progress("Validando PDF", 0, 4, "Iniciando validación...")

    # Obtener casos de uso del contenedor
    validate_pdf_use_case = composition_root.create_validate_pdf_use_case()

    print("Paso 1/4: Validando PDF...")
    print("   → Analizando estructura del documento...")
    validation_result = validate_pdf_use_case.execute(pdf_path)
    show_progress("Validando PDF", 1, 4, "Validación completada")

    return validation_result

    print(f"\n[✓] {validation_result['message']}")
    print(f"   → Páginas totales: {validation_result['total_pages']}")
    print(f"   → Páginas digitales: {validation_result['digital_pages']}")
    print(f"   → Páginas escaneadas: {validation_result['scanned_pages']}")

    return validation_result


def _prepare_processing_step():
    """Ejecuta el paso de preparación del procesamiento."""
    show_progress("Preparando", 1, 4, "Inicializando casos de uso...")
    print("\nPaso 2/4: Preparando procesamiento...")

    # Los casos de uso se obtienen del contenedor
    show_progress("Preparando", 2, 4, "Casos de uso inicializados")
    print("[✓] Casos de uso inicializados")


def _extract_content_step(pdf_path: Path) -> str:
    """Ejecuta el paso de extracción de contenido."""
    show_progress("Extrayendo", 2, 4, "Procesando documento...")
    print("\nPaso 3/4: Extrayendo contenido del PDF...")
    print("   → Analizando estructura del documento...")
    print("   → Aplicando OCR donde sea necesario...")
    print("   → Procesando tablas y elementos especiales...")

    # Simulamos progreso más detallado
    for i in range(3):
        time.sleep(0.5)  # Simulación de procesamiento
        show_progress("Extrayendo", 2 + (i * 0.3), 4,
                      f"Procesando página {i+1}...")

    # Obtener caso de uso del contenedor
    pdf_to_markdown_use_case = composition_root.create_pdf_to_markdown_use_case()
    markdown_content = pdf_to_markdown_use_case.execute(pdf_path)

    show_progress("Extrayendo", 3, 4, "Extracción completada")

    if len(markdown_content) > 1000:
        preview = markdown_content[:200] + "..."
    else:
        preview = markdown_content[:200]

    print(f"\n[✓] Contenido extraído ({len(markdown_content)} caracteres)")
    print(f"   → Vista previa: {preview}")

    return markdown_content


def _save_result_step(pdf_path: Path, markdown_content: str) -> Path:
    """Ejecuta el paso de guardado del resultado."""
    show_progress("Guardando", 3, 4, "Preparando archivo de salida...")
    print("\nPaso 4/4: Guardando resultado...")
    print("   → Generando archivo Markdown...")

    # Obtener adaptador de almacenamiento del contenedor
    storage_adapter = container.get_storage_port()
    output_path = storage_adapter.save_markdown(
        pdf_path.stem, markdown_content)
    show_progress("Guardando", 4, 4, "Archivo guardado exitosamente")

    return output_path
