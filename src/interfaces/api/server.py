"""
Módulo principal de la API REST.

Este módulo inicializa y configura la API FastAPI usando la configuración centralizada.
"""
import uvicorn
from infrastructure.logging_setup import logger
from shared.constants.config import config
from . import app


def start_api():
    """Inicia el servidor API usando la configuración centralizada."""
    api_config = config.api
    logger.info(f"Iniciando servidor API en {api_config.host}:{api_config.port}")
    
    try:
        uvicorn.run(
            app, 
            host=api_config.host, 
            port=api_config.port, 
            log_level="info",
            debug=api_config.debug
        )
    except ImportError:
        logger.error(
            "uvicorn no está instalado. Instálelo con: pip install uvicorn")
        print("Error: uvicorn no está instalado. Instálelo con: pip install uvicorn")
    except Exception as e:
        logger.error(f"Error iniciando servidor API: {e}")
        print(f"Error iniciando servidor API: {e}")


if __name__ == "__main__":
    start_api()
