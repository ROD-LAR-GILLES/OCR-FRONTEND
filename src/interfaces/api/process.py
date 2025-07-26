"""
Endpoints relacionados con el procesamiento de documentos.
"""
from typing import Optional
from fastapi import HTTPException
from pathlib import Path
import json
import time

from infrastructure.logging_setup import logger
from domain.use_cases.validate_pdf import ValidatePDFUseCase
from adapters.pymupdf_adapter import extract_markdown
from config import config

from . import app, UPLOAD_DIR
from .adapters import storage_adapter, document_adapter


@app.get("/api/process/{doc_id}")
async def process_document(doc_id: str, llm_mode: Optional[str] = None):
    """Procesa un documento previamente subido."""
    logger.info(f"Iniciando procesamiento del documento: {doc_id}")

    doc_dir = UPLOAD_DIR / doc_id
    pdf_path = doc_dir / "document.pdf"

    if not doc_dir.exists() or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    original_mode = config.llm_mode
    if llm_mode:
        config.llm_mode = llm_mode

    try:
        result = await _process_document(doc_id, pdf_path, doc_dir)
        return result
    except Exception as e:
        await _handle_processing_error(e, doc_id, pdf_path, doc_dir)
        raise
    finally:
        if llm_mode:
            config.llm_mode = original_mode


async def _process_document(doc_id: str, pdf_path: Path, doc_dir: Path):
    """Implementación del procesamiento del documento."""
    update_progress = _create_progress_updater(doc_dir)

    update_progress("iniciando", 0, "Iniciando procesamiento del documento")
    validate_pdf_use_case = ValidatePDFUseCase(document_port=document_adapter)
    validation_result = validate_pdf_use_case.execute(pdf_path)

    if not validation_result.get("valid", False):
        update_progress("error", -1, "Documento PDF inválido")
        raise HTTPException(status_code=422, detail="Documento inválido")

    update_progress("extrayendo", 25, "Extrayendo texto del PDF")
    markdown_content = extract_markdown(pdf_path)

    if not markdown_content or len(markdown_content.strip()) < 10:
        raise HTTPException(
            status_code=422, detail="No se pudo extraer contenido del PDF")

    update_progress("guardando", 75, "Guardando resultado")
    output_path = storage_adapter.save_markdown(doc_id, markdown_content)

    update_progress("completado", 100, "Procesamiento completado exitosamente")

    return {
        "document_id": doc_id,
        "status": "processed",
        "output_path": str(output_path),
        "message": "Documento procesado exitosamente",
        "content_stats": {
            "characters": len(markdown_content),
            "pages": validation_result.get("total_pages", "unknown"),
            "scanned_pages": validation_result.get("scanned_pages", "unknown")
        },
        "timestamp": time.time()
    }


def _create_progress_updater(doc_dir: Path):
    """Crea una función para actualizar el progreso del procesamiento."""
    progress_file = doc_dir / "progress.json"

    def update_progress(stage: str, progress: int, message: str, details: str = None):
        progress_data = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "details": details or "",
            "timestamp": time.time(),
            "status": "success" if progress >= 0 else "error"
        }
        try:
            with open(progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)
            logger.info(
                f"Progreso actualizado: {stage} - {progress}% - {message}")
        except Exception as e:
            logger.error(f"Error guardando progreso: {e}")

    return update_progress


async def _handle_processing_error(error: Exception, doc_id: str, pdf_path: Path, doc_dir: Path):
    """Maneja errores durante el procesamiento del documento."""
    error_msg = f"Error en el procesamiento: {str(error)}"

    update_progress = _create_progress_updater(doc_dir)
    update_progress("error", -1, error_msg)

    diagnostic_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "document_id": doc_id,
        "file_exists": pdf_path.exists(),
        "file_size": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "timestamp": time.time()
    }

    try:
        with open(doc_dir / "error_diagnostic.json", "w") as f:
            json.dump(diagnostic_info, f, indent=2)
    except Exception as diag_error:
        logger.error(f"No se pudo guardar diagnóstico: {diag_error}")


@app.get("/api/progress/{doc_id}")
async def get_progress(doc_id: str):
    """Obtiene el progreso del procesamiento de un documento."""
    doc_dir = UPLOAD_DIR / doc_id
    progress_file = doc_dir / "progress.json"
    error_diagnostic_file = doc_dir / "error_diagnostic.json"

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    doc_info = {
        "document_id": doc_id,
        "directory_exists": doc_dir.exists(),
        "pdf_exists": (doc_dir / "document.pdf").exists(),
        "created_at": doc_dir.stat().st_ctime if doc_dir.exists() else None
    }

    if not progress_file.exists():
        return {
            **doc_info,
            "stage": "no_iniciado",
            "progress": 0,
            "message": "Procesamiento no iniciado",
            "status": "waiting",
            "timestamp": None
        }

    try:
        with open(progress_file, "r") as f:
            progress_data = json.load(f)

        result = {**doc_info, **progress_data}

        if progress_data.get("status") == "error" and error_diagnostic_file.exists():
            try:
                with open(error_diagnostic_file, "r") as f:
                    diagnostic_data = json.load(f)
                result["diagnostic"] = diagnostic_data
            except Exception as e:
                logger.error(f"Error leyendo diagnóstico para {doc_id}: {e}")

        if 0 < progress_data.get("progress", 0) < 100:
            elapsed = time.time() - progress_data.get("timestamp", time.time())
            if progress_data.get("progress", 0) > 0:
                estimated_total = elapsed * \
                    (100 / progress_data.get("progress", 1))
                estimated_remaining = max(0, estimated_total - elapsed)
                result["time_estimate"] = {
                    "elapsed_seconds": round(elapsed, 1),
                    "estimated_remaining_seconds": round(estimated_remaining, 1),
                    "estimated_total_seconds": round(estimated_total, 1)
                }

        return result

    except Exception as e:
        logger.error(f"Error leyendo progreso para {doc_id}: {e}")
        return {
            **doc_info,
            "stage": "error",
            "progress": -1,
            "message": "Error al leer progreso",
            "status": "error",
            "timestamp": time.time()
        }


@app.get("/api/process/{doc_id}")
async def process_document(doc_id: str, llm_mode: Optional[str] = None):
    """Procesa un documento previamente subido."""
    logger.info(f"Iniciando procesamiento del documento: {doc_id}")

    doc_dir = UPLOAD_DIR / doc_id
    pdf_path = doc_dir / "document.pdf"
    progress_file = doc_dir / "progress.json"

    if not doc_dir.exists() or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    original_mode = config.llm_mode
    if llm_mode:
        config.llm_mode = llm_mode

    try:
        result = await _process_document(doc_id, pdf_path, doc_dir)
        return result
    except Exception as e:
        await _handle_processing_error(e, doc_id, pdf_path, doc_dir)
        raise
    finally:
        if llm_mode:
            config.llm_mode = original_mode


async def _process_document(doc_id: str, pdf_path: Path, doc_dir: Path):
    """Implementación del procesamiento del documento."""
    update_progress = _create_progress_updater(doc_dir)

    update_progress("iniciando", 0, "Iniciando procesamiento del documento")
    validate_pdf_use_case = ValidatePDFUseCase(document_port=document_adapter)
    validation_result = validate_pdf_use_case.execute(pdf_path)

    update_progress("extrayendo", 25, "Extrayendo texto del PDF")
    markdown_content = extract_markdown(pdf_path)

    if not markdown_content or len(markdown_content.strip()) < 10:
        raise HTTPException(
            status_code=422, detail="No se pudo extraer contenido del PDF")

    update_progress("guardando", 75, "Guardando resultado")
    output_path = storage_adapter.save_markdown(doc_id, markdown_content)

    update_progress("completado", 100, "Procesamiento completado exitosamente")

    return {
        "document_id": doc_id,
        "status": "processed",
        "output_path": str(output_path),
        "message": "Documento procesado exitosamente",
        "content_stats": {
            "characters": len(markdown_content),
            "pages": validation_result.get("total_pages", "unknown"),
            "scanned_pages": validation_result.get("scanned_pages", "unknown")
        },
        "timestamp": time.time()
    }


def _create_progress_updater(doc_dir: Path):
    """Crea una función para actualizar el progreso del procesamiento."""
    progress_file = doc_dir / "progress.json"

    def update_progress(stage: str, progress: int, message: str, details: str = None):
        progress_data = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "details": details or "",
            "timestamp": time.time(),
            "status": "success" if progress >= 0 else "error"
        }
        try:
            with open(progress_file, "w") as f:
                json.dump(progress_data, f)
            logger.info(
                f"Progreso actualizado: {stage} - {progress}% - {message}")
        except Exception as e:
            logger.error(f"Error guardando progreso: {e}")

    return update_progress


async def _handle_processing_error(error: Exception, doc_id: str, pdf_path: Path, doc_dir: Path):
    """Maneja errores durante el procesamiento del documento."""
    error_msg = f"Error en el procesamiento: {str(error)}"
    error_details = f"Tipo: {type(error).__name__}, Documento: {doc_id}, Archivo: {pdf_path.name}"

    update_progress = _create_progress_updater(doc_dir)
    update_progress("error", -1, error_msg, error_details)

    diagnostic_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "document_id": doc_id,
        "file_exists": pdf_path.exists(),
        "file_size": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "timestamp": time.time()
    }

    try:
        with open(doc_dir / "error_diagnostic.json", "w") as f:
            json.dump(diagnostic_info, f, indent=2)
    except Exception as diag_error:
        logger.error(f"No se pudo guardar diagnóstico: {diag_error}")
