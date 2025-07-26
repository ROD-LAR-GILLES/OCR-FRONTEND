"""Rutas relacionadas con el procesamiento de documentos."""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import json
import time
import uuid
import shutil

from infrastructure.logging_setup import logger
from infrastructure.storage_adapter import StorageAdapter
from infrastructure.document_adapter import DocumentAdapter
from domain.use_cases.validate_pdf import ValidatePDFUseCase
from config import config

router = APIRouter()

# Adapters
storage_adapter = StorageAdapter()
document_adapter = DocumentAdapter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint para subir archivos PDF."""
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
        logger.exception(f"Error procesando PDF {doc_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el PDF: {str(e)}")


@router.get("/process/{doc_id}")
async def process_document(doc_id: str):
    """Endpoint para procesar un documento."""
    # Aquí iría la lógica de procesamiento
    pass


@router.get("/result/{doc_id}")
async def get_result(doc_id: str, format: str = "markdown"):
    """Endpoint para obtener el resultado del procesamiento."""
    logger.info(
        f"Solicitando resultado para documento {doc_id} en formato {format}")

    doc_dir = UPLOAD_DIR / doc_id
    if not doc_dir.exists():
        logger.error(f"Documento no encontrado: {doc_id}")
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if format == "markdown":
        markdown_file = doc_dir / f"{doc_id}.md"
        if not markdown_file.exists():
            logger.warning(
                f"Archivo Markdown no encontrado para documento: {doc_id}")
            raise HTTPException(
                status_code=404,
                detail="Resultado no disponible. Procese el documento primero."
            )
        return FileResponse(markdown_file, media_type="text/markdown")

    elif format == "json":
        json_file = doc_dir / f"{doc_id}.json"
        if not json_file.exists():
            logger.warning(
                f"Archivo JSON no encontrado para documento: {doc_id}")
            raise HTTPException(
                status_code=404, detail="Resultado JSON no disponible")
        return FileResponse(json_file, media_type="application/json")

    else:
        logger.error(f"Formato no soportado: {format}")
        raise HTTPException(status_code=400, detail="Formato no soportado")
