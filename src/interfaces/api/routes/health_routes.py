"""Rutas relacionadas con el estado del sistema."""
from fastapi import APIRouter
from pathlib import Path
import time

from infrastructure.logging_setup import logger

router = APIRouter()
UPLOAD_DIR = Path("uploads")


@router.get("/health")
async def health_check():
    """Endpoint de salud del sistema con información detallada."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        # Verificar directorios necesarios
        directories_status = {}
        for dir_name, dir_path in [
            ("uploads", UPLOAD_DIR),
            ("static", Path("static")),
            ("result", Path("result")),
            ("logs", Path("logs"))
        ]:
            directories_status[dir_name] = {
                "exists": dir_path.exists(),
                "path": str(dir_path),
                "writable": dir_path.exists() and dir_path.is_dir()
            }

        # Contar documentos
        total_docs = len([d for d in UPLOAD_DIR.iterdir()
                         if d.is_dir()]) if UPLOAD_DIR.exists() else 0

        return {
            "system": "OCR-FRONTEND",
            "status": "healthy",
            "timestamp": time.time(),
            "directories": directories_status,
            "statistics": {
                "total_documents": total_docs,
                "upload_directory": str(UPLOAD_DIR)
            }
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }
