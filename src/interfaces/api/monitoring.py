"""
Endpoints de monitoreo y estado del sistema.
"""
from fastapi import HTTPException
import json
import time
import subprocess
from pathlib import Path

from infrastructure.logging_setup import logger
from config import config
from . import app, UPLOAD_DIR
from .adapters import storage_adapter, document_adapter


@app.get("/api/status")
async def get_system_status():
    """Endpoint para verificar el estado del sistema."""
    try:
        directories_status = _check_directories_status()
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
            },
            "config": {
                "llm_mode": getattr(config, 'llm_mode', 'unknown'),
                "llm_provider": getattr(config, 'llm_provider', 'unknown')
            }
        }
    except Exception as e:
        logger.error(f"Error verificando estado del sistema: {e}")
        return {
            "system": "OCR-FRONTEND",
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }


@app.get("/api/health")
async def health_check():
    """Endpoint de salud del sistema con información detallada."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        health_status["components"] = _check_components_status()

        return health_status
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }


@app.get("/api/logs/{doc_id}")
async def get_processing_logs(doc_id: str, lines: int = 50):
    """Obtiene los logs de procesamiento de un documento específico."""
    doc_dir = UPLOAD_DIR / doc_id

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    log_entries = []

    try:
        # Buscar en logs del sistema por el document_id
        try:
            result = subprocess.run(
                ["grep", "-n", doc_id, "/var/log/app.log"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                log_entries.extend(result.stdout.strip().split('\n'))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Buscar en archivos de progreso y error
        progress_file = doc_dir / "progress.json"
        error_file = doc_dir / "error_diagnostic.json"

        if progress_file.exists():
            with open(progress_file, "r") as f:
                progress_data = json.load(f)
                timestamp = progress_data.get("timestamp", time.time())
                stage = progress_data.get("stage", "unknown")
                message = progress_data.get("message", "")
                log_entries.append(
                    f"[{timestamp}] PROGRESS: {stage} - {message}")

        if error_file.exists():
            with open(error_file, "r") as f:
                error_data = json.load(f)
                timestamp = error_data.get("timestamp", time.time())
                error_type = error_data.get("error_type", "Unknown")
                error_msg = error_data.get("error_message", "")
                log_entries.append(
                    f"[{timestamp}] ERROR: {error_type} - {error_msg}")

        log_entries = log_entries[-lines:] if log_entries else []

        return {
            "document_id": doc_id,
            "log_entries": log_entries,
            "total_entries": len(log_entries),
            "requested_lines": lines,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Error obteniendo logs para {doc_id}: {e}")
        return {
            "document_id": doc_id,
            "log_entries": [f"Error obteniendo logs: {str(e)}"],
            "total_entries": 0,
            "requested_lines": lines,
            "timestamp": time.time(),
            "error": str(e)
        }


def _check_directories_status():
    """Verifica el estado de los directorios del sistema."""
    directories = {
        "uploads": UPLOAD_DIR,
        "static": Path("static"),
        "result": Path("result"),
        "logs": Path("logs")
    }

    return {
        name: {
            "exists": path.exists(),
            "path": str(path),
            "writable": path.exists() and path.is_dir()
        }
        for name, path in directories.items()
    }


def _check_components_status():
    """Verifica el estado de los componentes del sistema."""
    components = {}

    # Verificar componentes básicos
    for component_name, component in [
        ("storage", storage_adapter),
        ("document_adapter", document_adapter),
        ("upload_directory", UPLOAD_DIR)
    ]:
        try:
            if component_name == "upload_directory":
                components[component_name] = {
                    "status": "healthy" if component.exists() else "error",
                    "exists": component.exists(),
                    "writable": component.exists() and component.is_dir(),
                    "path": str(component)
                }
            else:
                components[component_name] = {
                    "status": "healthy" if component else "error",
                    "available": bool(component)
                }
        except Exception as e:
            components[component_name] = {
                "status": "error",
                "error": str(e)
            }

    # Verificar dependencias críticas
    try:
        import fitz
        components["pymupdf"] = {
            "status": "healthy",
            "version": fitz.version
        }
    except ImportError as e:
        components["pymupdf"] = {
            "status": "error",
            "error": str(e)
        }

    return components


@app.get("/api/status")
async def get_system_status():
    """Endpoint para verificar el estado del sistema."""
    try:
        directories_status = _check_directories_status()
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
        logger.error(f"Error verificando estado del sistema: {e}")
        return {
            "system": "OCR-FRONTEND",
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }


@app.get("/api/health")
async def health_check():
    """Endpoint de salud del sistema con información detallada."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        health_status["components"] = _check_components_status()

        return health_status
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }


def _check_directories_status():
    """Verifica el estado de los directorios del sistema."""
    directories = {
        "uploads": UPLOAD_DIR,
        "static": Path("static"),
        "result": Path("result"),
        "logs": Path("logs")
    }

    return {
        name: {
            "exists": path.exists(),
            "path": str(path),
            "writable": path.exists() and path.is_dir()
        }
        for name, path in directories.items()
    }


def _check_components_status():
    """Verifica el estado de los componentes del sistema."""
    components = {}

    # Verificar componentes básicos
    for component_name, component in [
        ("storage", storage_adapter),
        ("document_adapter", document_adapter),
        ("upload_directory", UPLOAD_DIR)
    ]:
        try:
            if component_name == "upload_directory":
                components[component_name] = {
                    "status": "healthy" if component.exists() else "error",
                    "exists": component.exists(),
                    "writable": component.exists() and component.is_dir(),
                    "path": str(component)
                }
            else:
                components[component_name] = {
                    "status": "healthy" if component else "error",
                    "available": bool(component)
                }
        except Exception as e:
            components[component_name] = {
                "status": "error",
                "error": str(e)
            }

    # Verificar dependencias críticas
    try:
        import fitz
        components["pymupdf"] = {
            "status": "healthy",
            "version": fitz.version
        }
    except ImportError as e:
        components["pymupdf"] = {
            "status": "error",
            "error": str(e)
        }

    return components
