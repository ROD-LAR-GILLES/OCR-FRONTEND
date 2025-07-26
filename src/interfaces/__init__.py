"""
Interfaces del sistema OCR.

Este módulo contiene las interfaces de usuario que permiten interactuar
con la aplicación, incluyendo CLI y API REST.
"""

from .cli_menu import main_loop
from .cli import list_pdfs, select_pdf
from .config_menu import ConfigMenu

# La API REST se carga condicionalmente para no requerir dependencias
# si solo se usa la CLI
try:
    from .api_rest import start_api
    __all__ = ["main_loop", "list_pdfs",
               "select_pdf", "ConfigMenu", "start_api"]
except ImportError:
    # FastAPI no está instalado, solo exponemos las interfaces CLI
    __all__ = ["main_loop", "list_pdfs", "select_pdf", "ConfigMenu"]
