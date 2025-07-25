"""
Menú Principal CLI - Lógica de navegación y menú principal.
"""

import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    fitz = None

from adapters import get_language_detector
from shared.util.config import config
from interfaces.config_menu import ConfigMenu
from .pdf_management import pdf_manager, select_pdf
from .processing import convert_pdf
from shared.constants.directories import PDF_DIR


def main_loop() -> None:
    """Bucle principal del menú con configuración LLM integrada."""
    while True:
        print("\n=== OCR-PYMUPDF ===")

        # Mostrar información del sistema siempre
        print("\n----------- Información del Sistema ------------")
        print("------------------------------------------------")
        print(f"Directorio de PDFs:         {PDF_DIR}")
        pdf_stats = pdf_manager.get_directory_stats()
        print(f"PDFs disponibles:           {pdf_stats['total_files']}")
        print(f"PDFs válidos:               {pdf_stats['valid_pdfs']}")
        print(
            f"Tamaño total:               {pdf_stats['total_size_mb']:.1f} MB")

        if fitz:
            print(f"PyMuPDF versión:           {fitz.version}")
        else:
            print("PyMuPDF:                   No disponible")

        try:
            detector = get_language_detector()
            print(
                f"Detector de idioma:         {'Disponible' if detector else 'No disponible'}")
        except ImportError:
            print("Detector de idioma:         No disponible")

        print(f"Modo LLM:                   {config.llm.mode}")
        print(f"Proveedor LLM:              {config.llm.provider}")
        print("------------------------------------------------")

        print("\nOpciones disponibles:")
        print("1. Convertir PDF a Markdown")
        print("2. Configuración")
        print("3. Salir")

        choice = input("\nSeleccione una opción (1-3): ").strip()

        match choice:
            case "1":
                handle_pdf_conversion()
            case "2":
                ConfigMenu.show_provider_menu()
            case "3":
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
