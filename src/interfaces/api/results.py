"""
Endpoints relacionados con la obtención de resultados y documentos.
"""
from fastapi import HTTPException
from fastapi.responses import FileResponse
import json
import time
from pathlib import Path

from infrastructure.logging_setup import logger
from . import app, UPLOAD_DIR


@app.get("/api/result/{doc_id}")
async def get_result(doc_id: str, format: str = "markdown"):
    """Obtiene el resultado de un documento procesado."""
    logger.info(
        f"Solicitando resultado para documento {doc_id} en formato {format}")

    doc_dir = UPLOAD_DIR / doc_id
    if not doc_dir.exists():
        logger.error(f"Documento no encontrado: {doc_id}")
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if format == "markdown":
        return _handle_markdown_response(doc_id, doc_dir)
    elif format == "json":
        return _handle_json_response(doc_id, doc_dir)
    else:
        logger.error(f"Formato no soportado: {format}")
        raise HTTPException(status_code=400, detail="Formato no soportado")


@app.get("/api/documents")
async def list_documents():
    """Lista todos los documentos procesados."""
    logger.info("Solicitando lista de documentos")
    try:
        documents = _get_documents_info()
        logger.info(f"Encontrados {len(documents)} documentos")
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al listar documentos: {str(e)}")


def _handle_markdown_response(doc_id: str, doc_dir: Path):
    """Maneja la respuesta para formato markdown."""
    markdown_file = doc_dir / f"{doc_id}.md"
    if not markdown_file.exists():
        logger.warning(
            f"Archivo Markdown no encontrado para documento: {doc_id}")
        raise HTTPException(
            status_code=404, detail="Resultado no disponible. Procese el documento primero.")

    logger.info(f"Enviando archivo Markdown: {markdown_file}")
    return FileResponse(markdown_file, media_type="text/markdown")


def _handle_json_response(doc_id: str, doc_dir: Path):
    """Maneja la respuesta para formato JSON."""
    json_file = doc_dir / f"{doc_id}.json"
    if not json_file.exists():
        logger.warning(f"Archivo JSON no encontrado para documento: {doc_id}")
        raise HTTPException(
            status_code=404, detail="Resultado JSON no disponible")

    logger.info(f"Enviando archivo JSON: {json_file}")
    return FileResponse(json_file, media_type="application/json")


def _get_documents_info():
    """Obtiene información detallada de todos los documentos."""
    documents = []

    for doc_dir in UPLOAD_DIR.iterdir():
        if doc_dir.is_dir():
            doc_id = doc_dir.name
            doc_info = _get_single_document_info(doc_id, doc_dir)
            documents.append(doc_info)

    return documents


def _get_single_document_info(doc_id: str, doc_dir: Path):
    """Obtiene información detallada de un documento específico."""
    validation_file = doc_dir / "validation.json"
    markdown_file = doc_dir / f"{doc_id}.md"
    progress_file = doc_dir / "progress.json"

    doc_info = {
        "document_id": doc_id,
        "uploaded_at": doc_dir.stat().st_ctime,
        "processed": markdown_file.exists(),
        "validated": validation_file.exists()
    }

    # Añadir información de validación
    if validation_file.exists():
        try:
            with open(validation_file, "r") as f:
                doc_info["validation"] = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo validación para {doc_id}: {e}")
            doc_info["validation"] = {"error": "Formato inválido"}

    # Añadir información de progreso
    if progress_file.exists():
        try:
            with open(progress_file, "r") as f:
                doc_info["progress"] = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo progreso para {doc_id}: {e}")
            doc_info["progress"] = {"error": "No disponible"}

    return doc_info


@app.get("/api/result/{doc_id}")
async def get_result(doc_id: str, format: str = "markdown"):
    """Obtiene el resultado de un documento procesado."""
    logger.info(
        f"Solicitando resultado para documento {doc_id} en formato {format}")

    doc_dir = UPLOAD_DIR / doc_id
    if not doc_dir.exists():
        logger.error(f"Documento no encontrado: {doc_id}")
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if format == "markdown":
        return _handle_markdown_response(doc_id, doc_dir)
    elif format == "json":
        return _handle_json_response(doc_id, doc_dir)
    else:
        logger.error(f"Formato no soportado: {format}")
        raise HTTPException(status_code=400, detail="Formato no soportado")


@app.get("/api/documents")
async def list_documents():
    """Lista todos los documentos procesados."""
    logger.info("Solicitando lista de documentos")
    try:
        documents = _get_documents_info()
        logger.info(f"Encontrados {len(documents)} documentos")
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al listar documentos: {str(e)}")


def _handle_markdown_response(doc_id: str, doc_dir: Path):
    """Maneja la respuesta para formato markdown."""
    markdown_file = doc_dir / f"{doc_id}.md"
    if not markdown_file.exists():
        logger.warning(
            f"Archivo Markdown no encontrado para documento: {doc_id}")
        raise HTTPException(
            status_code=404, detail="Resultado no disponible. Procese el documento primero.")

    logger.info(f"Enviando archivo Markdown: {markdown_file}")
    return FileResponse(markdown_file, media_type="text/markdown")


def _handle_json_response(doc_id: str, doc_dir: Path):
    """Maneja la respuesta para formato JSON."""
    json_file = doc_dir / f"{doc_id}.json"
    if not json_file.exists():
        logger.warning(f"Archivo JSON no encontrado para documento: {doc_id}")
        raise HTTPException(
            status_code=404, detail="Resultado JSON no disponible")

    logger.info(f"Enviando archivo JSON: {json_file}")
    return FileResponse(json_file, media_type="application/json")


def _get_documents_info():
    """Obtiene información detallada de todos los documentos."""
    documents = []

    for doc_dir in UPLOAD_DIR.iterdir():
        if doc_dir.is_dir():
            doc_id = doc_dir.name
            doc_info = _get_single_document_info(doc_id, doc_dir)
            documents.append(doc_info)

    return documents


def _get_single_document_info(doc_id: str, doc_dir: Path):
    """Obtiene información detallada de un documento específico."""
    validation_file = doc_dir / "validation.json"
    markdown_file = doc_dir / f"{doc_id}.md"
    progress_file = doc_dir / "progress.json"

    doc_info = {
        "document_id": doc_id,
        "uploaded_at": doc_dir.stat().st_ctime,
        "processed": markdown_file.exists(),
        "validated": validation_file.exists()
    }

    # Añadir información de validación
    if validation_file.exists():
        try:
            with open(validation_file, "r") as f:
                doc_info["validation"] = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo validación para {doc_id}: {e}")
            doc_info["validation"] = {"error": "Formato inválido"}

    # Añadir información de progreso
    if progress_file.exists():
        try:
            with open(progress_file, "r") as f:
                doc_info["progress"] = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo progreso para {doc_id}: {e}")
            doc_info["progress"] = {"error": "No disponible"}

    return doc_info
