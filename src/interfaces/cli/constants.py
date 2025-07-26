"""
Constantes globales para la aplicación CLI.

DEPRECADO: Las constantes de directorios se han movido a shared.constants.directories
"""

from shared.constants.directories import PDF_DIR

# Re-exportar para compatibilidad hacia atrás
__all__ = ['PDF_DIR']
