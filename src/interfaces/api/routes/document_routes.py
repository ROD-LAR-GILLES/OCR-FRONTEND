"""Rutas relacionadas con la gestión de documentos."""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import time

from infrastructure.logging_setup import logger
from infrastructure.storage_adapter import StorageAdapter

router = APIRouter()
storage_adapter = StorageAdapter()

UPLOAD_DIR = Path("uploads")


@router.get("/documents")
async def list_documents():
    """Lista todos los documentos procesados."""
    logger.info("Solicitando lista de documentos")
    documents = []

    try:
        for doc_dir in UPLOAD_DIR.iterdir():
            if doc_dir.is_dir():
                doc_id = doc_dir.name
                validation_file = doc_dir / "validation.json"
                markdown_file = doc_dir / f"{doc_id}.md"
                progress_file = doc_dir / "progress.json"

                doc_info = {
                    "document_id": doc_id,
                    "uploaded_at": doc_dir.stat().st_ctime,
                    "processed": markdown_file.exists(),
                    "validated": validation_file.exists()
                }

                if validation_file.exists():
                    try:
                        with open(validation_file, "r") as f:
                            doc_info["validation"] = json.load(f)
                    except Exception as e:
                        logger.error(
                            f"Error leyendo validación para {doc_id}: {e}")
                        doc_info["validation"] = {"error": "Formato inválido"}

                if progress_file.exists():
                    try:
                        with open(progress_file, "r") as f:
                            doc_info["progress"] = json.load(f)
                    except Exception as e:
                        logger.error(
                            f"Error leyendo progreso para {doc_id}: {e}")
                        doc_info["progress"] = {"error": "No disponible"}

                documents.append(doc_info)

        logger.info(f"Encontrados {len(documents)} documentos")
        return {"documents": documents, "total": len(documents)}

    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar documentos: {str(e)}"
        )
