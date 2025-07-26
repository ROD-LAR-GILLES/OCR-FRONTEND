"""
Menú Principal CLI - Lógica de navegación y menú principal.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import fitz
except ImportError:
    fitz = None

from loguru import logger

from adapters import get_language_detector
from config import config
from interfaces.config_menu import ConfigMenu
from .constants import PDF_DIR
from .helpers import show_llm_status
from .pdf_handler import select_pdf
from .processing import convert_pdf


def main_loop() -> None:
    """Bucle principal del menú con configuración LLM integrada."""
    while True:
        print("\n=== OCR-PYMUPDF ===")
        show_llm_status()
        print("\nOpciones disponibles:")
        print("1. Convertir PDF a Markdown")
        print("2. Configuración")
        print("   2.1. Cambiar proveedor LLM")
        print("   2.2. Cambiar modo LLM")
        print("3. Información del sistema")
        print("4. Salir")

        choice = input("\nSeleccione una opción (1-4): ").strip()

        match choice:
            case "1":
                handle_pdf_conversion()
            case "2":
                ConfigMenu.show_provider_menu()
            case "3":
                show_system_info()
            case "4":
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
    if fitz:
        print(f"PyMuPDF versión: {fitz.version}")
    else:
        print("PyMuPDF: No disponible")

    try:
        detector = get_language_detector()
        print(
            f"Detector de idioma: {'Disponible' if detector else 'No disponible'}")
    except ImportError:
        print("Detector de idioma: No disponible")

    # Información de configuración
    print(f"Modo LLM: {config.llm_mode}")
    print(f"Proveedor LLM: {config.llm_provider}")

    print("-" * 40)
