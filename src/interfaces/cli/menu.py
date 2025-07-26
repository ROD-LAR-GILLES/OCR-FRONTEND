"""
Main Menu - Menú principal de la interfaz CLI.
"""

import sys
from interfaces.config_menu import ConfigMenu
from .helpers import show_llm_status
from .pdf_handler import select_pdf
from .processing import convert_pdf
from .cache_manager import show_cache_menu
from . import PDF_DIR


def main_loop() -> None:
    """Bucle principal del menú con configuración LLM integrada."""
    while True:
        print("\n=== OCR-PYMUPDF ===")
        show_llm_status()
        print("\nOpciones disponibles:")
        print("1. Convertir PDF a Markdown")
        print("2. Configuración")
        print("3. Gestión de caché")
        print("4. Información del sistema")
        print("5. Salir")

        choice = input("\nSeleccione una opción (1-5): ").strip()

        match choice:
            case "1":
                handle_pdf_conversion()
            case "2":
                ConfigMenu.show_provider_menu()
            case "3":
                show_cache_menu()
            case "4":
                show_system_info()
            case "5":
                print("\n¡Hasta luego!")
                sys.exit(0)
            case _:
                print("[ERROR] Opción inválida")


def handle_pdf_conversion():
    """Maneja el proceso de conversión de PDF."""
    if pdf := select_pdf():
        convert_pdf(PDF_DIR / pdf)
    else:
        print("\n[INFO] No se seleccionó ningún archivo")


def show_system_info():
    """Muestra información del sistema."""
    print("\n=== Información del Sistema ===")
    print("-" * 40)

    # Información de directorios
    print(f"Directorio de PDFs: {PDF_DIR}")
    print(f"PDFs disponibles: {len(list(PDF_DIR.glob('*.pdf')))}")

    # Información de módulos
    try:
        import fitz
        print(f"PyMuPDF versión: {fitz.version}")
    except ImportError:
        print("PyMuPDF: No disponible")

    try:
        from adapters import get_language_detector
        detector = get_language_detector()
        print(
            f"Detector de idioma: {'Disponible' if detector else 'No disponible'}")
    except ImportError:
        print("Detector de idioma: No disponible")

    # Información de configuración
    from config import config
    print(f"Modo LLM: {config.llm_mode}")
    print(f"Proveedor LLM: {config.llm_provider}")

    print("-" * 40)


def show_help():
    """Muestra ayuda sobre el uso del sistema."""
    print("\n=== Ayuda del Sistema OCR-PYMUPDF ===")
    print("-" * 50)
    print("Este sistema permite convertir archivos PDF a formato Markdown")
    print("utilizando OCR (reconocimiento óptico de caracteres) cuando sea necesario.")
    print()
    print("INSTRUCCIONES:")
    print("1. Coloca archivos PDF en el directorio './pdfs'")
    print("2. Ejecuta la opción 1 para convertir PDFs")
    print("3. Los archivos resultantes se guardan automáticamente")
    print()
    print("CONFIGURACIÓN:")
    print("- Usa la opción 2 para configurar el procesamiento LLM")
    print("- La opción 3 permite gestionar la caché OCR")
    print()
    print("SOLUCIÓN DE PROBLEMAS:")
    print("- Verifica que los PDFs no estén corruptos")
    print("- Asegúrate de tener permisos de escritura")
    print("- Consulta los logs para errores detallados")
    print("-" * 50)
