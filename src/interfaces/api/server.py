"""
Módulo principal de la API REST.

Este módulo inicializa y configura la API FastAPI.
"""
import uvicorn
from infrastructure.logging_setup import logger
from . import app


def start_api():
    """Inicia el servidor API."""
    logger.info("Iniciando servidor API en puerto 8000")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError:
        logger.error(
            "uvicorn no está instalado. Instálelo con: pip install uvicorn")
        print("Error: uvicorn no está instalado. Instálelo con: pip install uvicorn")
    except Exception as e:
        logger.error(f"Error iniciando servidor API: {e}")
        print(f"Error iniciando servidor API: {e}")


if __name__ == "__main__":
    start_api()
