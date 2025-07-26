"""
Endpoints principales de la API REST.
"""
import json
import shutil
import time
import uuid
from pathlib import Path

from fastapi import File, HTTPException, UploadFile

from domain.use_cases.validate_pdf import ValidatePDFUseCase
from infrastructure.logging_setup import logger
from . import UPLOAD_DIR, app
from .adapters import document_adapter, storage_adapter


@app.get("/")
async def root():
    """Endpoint raíz que proporciona información básica sobre la API."""
    logger.info("Acceso al endpoint raíz")
    return {
        "name": "OCR-FRONTEND API",
        "version": "0.1.0",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "upload": "/api/upload",
            "process": "/api/process/{doc_id}",
            "progress": "/api/progress/{doc_id}",
            "result": "/api/result/{doc_id}",
            "documents": "/api/documents",
            "status": "/api/status"
        },
        "timestamp": time.time()
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Sube un archivo PDF para procesamiento OCR."""
    logger.info(f"Iniciando carga de archivo: {file.filename}")

    if not file.filename.endswith('.pdf'):
        logger.error(f"Tipo de archivo inválido: {file.filename}")
        raise HTTPException(
            status_code=400, detail="Solo se aceptan archivos PDF")

    doc_id = str(uuid.uuid4())
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(exist_ok=True)
    pdf_path = doc_dir / "document.pdf"

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error al guardar archivo: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al guardar archivo: {str(e)}")

    try:
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=document_adapter)
        validation_result = validate_pdf_use_case.execute(pdf_path)

        with open(doc_dir / "validation.json", "w") as f:
            json.dump(validation_result, f)

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "validation": validation_result,
            "message": "Archivo cargado y validado exitosamente",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.exception(f"Error validando PDF {doc_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el PDF: {str(e)}")


# Adapters
storage_adapter = StorageAdapter()
document_adapter = DocumentAdapter()


@app.get("/")
async def root():
    """Endpoint raíz que proporciona información básica sobre la API."""
    logger.info("Acceso al endpoint raíz")
    return {
        "name": "OCR-FRONTEND API",
        "version": "0.1.0",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "upload": "/api/upload",
            "process": "/api/process/{doc_id}",
            "progress": "/api/progress/{doc_id}",
            "result": "/api/result/{doc_id}",
            "documents": "/api/documents",
            "status": "/api/status"
        },
        "timestamp": time.time()
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Sube un archivo PDF para procesamiento OCR."""
    logger.info(f"Iniciando carga de archivo: {file.filename}")

    if not file.filename.endswith('.pdf'):
        logger.error(f"Tipo de archivo inválido: {file.filename}")
        raise HTTPException(
            status_code=400, detail="Solo se aceptan archivos PDF")

    doc_id = str(uuid.uuid4())
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(exist_ok=True)
    pdf_path = doc_dir / "document.pdf"

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error al guardar archivo: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al guardar archivo: {str(e)}")

    try:
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=document_adapter)
        validation_result = validate_pdf_use_case.execute(pdf_path)

        with open(doc_dir / "validation.json", "w") as f:
            json.dump(validation_result, f)

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "validation": validation_result,
            "message": "Archivo cargado y validado exitosamente",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.exception(f"Error validando PDF {doc_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
