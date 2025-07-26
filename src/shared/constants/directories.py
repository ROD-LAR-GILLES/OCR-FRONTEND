"""
Constantes de directorios centralizadas.

Este módulo centraliza todas las definiciones de rutas y directorios
utilizados en la aplicación, eliminando la duplicación entre módulos.
"""
from pathlib import Path
from typing import Dict

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Directorios principales


class Directories:
    """Constantes de directorios del sistema."""

    # Directorios de entrada
    PDFS = PROJECT_ROOT / "pdfs"
    UPLOADS = PROJECT_ROOT / "uploads"

    # Directorios de salida
    OUTPUT = PROJECT_ROOT / "output"
    RESULT = PROJECT_ROOT / "result"

    # Directorios de datos
    DATA = PROJECT_ROOT / "data"
    CACHE = DATA / "cache"
    MODELS = DATA / "models"

    # Directorios de logs
    LOGS = PROJECT_ROOT / "logs"

    # Directorios estáticos
    STATIC = PROJECT_ROOT / "static"

    @classmethod
    def ensure_all_exist(cls) -> None:
        """Asegura que todos los directorios existan."""
        directories = [
            cls.PDFS, cls.UPLOADS, cls.OUTPUT, cls.RESULT,
            cls.DATA, cls.CACHE, cls.MODELS, cls.LOGS, cls.STATIC
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_all_paths(cls) -> Dict[str, Path]:
        """Retorna un diccionario con todas las rutas."""
        return {
            'pdfs': cls.PDFS,
            'uploads': cls.UPLOADS,
            'output': cls.OUTPUT,
            'result': cls.RESULT,
            'data': cls.DATA,
            'cache': cls.CACHE,
            'models': cls.MODELS,
            'logs': cls.LOGS,
            'static': cls.STATIC
        }


# Alias para compatibilidad hacia atrás
PDF_DIR = Directories.PDFS
UPLOAD_DIR = Directories.UPLOADS
OUTPUT_DIR = Directories.OUTPUT
RESULT_DIR = Directories.RESULT
DATA_DIR = Directories.DATA
CACHE_DIR = Directories.CACHE
MODELS_DIR = Directories.MODELS
LOGS_DIR = Directories.LOGS
STATIC_DIR = Directories.STATIC
