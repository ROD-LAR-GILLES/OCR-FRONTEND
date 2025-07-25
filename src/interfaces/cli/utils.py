"""
CLI Utilities - Utilidades consolidadas para la interfaz CLI.

Este módulo consolida helpers, constantes y utilidades compartidas
para reducir la fragmentación excesiva de archivos pequeños.
"""
from pathlib import Path
from shared.util.config import config
from shared.constants.directories import PDF_DIR


def show_llm_status() -> None:
    """Muestra el estado actual de la configuración LLM."""
    provider = config.llm.provider
    if not provider:
        provider = "auto"

    mode = config.llm.mode
    status = "Desactivado" if mode == "off" else f"Activado ({provider}, modo: {mode})"
    print(f"\nProcesamiento LLM: {status}")


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


def print_success_summary(output_path: Path, content_length: int, validation_result: dict):
    """Imprime un resumen exitoso del procesamiento."""
    print("\n" + "=" * 60)
    print(" PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"✓ Archivo generado: {output_path}")
    print(f"✓ Tamaño del contenido: {content_length} caracteres")
    print(f"✓ Páginas procesadas: {validation_result['total_pages']}")
    if validation_result['scanned_pages'] > 0:
        print(
            f"✓ OCR aplicado a: {validation_result['scanned_pages']} páginas")
    print("=" * 60)


def print_error_details(error: Exception, pdf_path: Path):
    """Imprime detalles del error de manera organizada."""
    print(f"\n ERROR CRÍTICO EN EL PROCESAMIENTO")
    print("=" * 60)
    print(f" Tipo de error: {type(error).__name__}")
    print(f" Descripción: {str(error)}")
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


# Constantes CLI (consolidadas)
CLI_PDF_DIR = PDF_DIR  # Alias para compatibilidad hacia atrás

__all__ = [
    'show_llm_status',
    'show_progress',
    'print_success_summary',
    'print_error_details',
    'CLI_PDF_DIR'
]
