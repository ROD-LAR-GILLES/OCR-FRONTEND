"""
Interfaces del sistema OCR.

Este módulo contiene las interfaces de usuario que permiten interactuar
con la aplicación usando la CLI.
"""

from .cli_menu import main_loop
from .cli import list_pdfs, select_pdf
from .config_menu import ConfigMenu

__all__ = ["main_loop", "list_pdfs", "select_pdf", "ConfigMenu"]
