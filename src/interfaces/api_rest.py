"""
API REST para el sistema OCR-FRONTEND.

Este módulo proporciona una API REST para el sistema OCR-FRONTEND,
permitiendo el procesamiento de documentos PDF a través de una interfaz HTTP.

Características:
- Endpoint para cargar y procesar PDFs
- Endpoint para obtener resultados en formato Markdown o JSON
- Soporte para autenticación JWT
- Documentación automática con Swagger/OpenAPI
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid
import shutil

# Importaciones del dominio
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.use_cases.validate_pdf import ValidatePDFUseCase

# Importaciones de infraestructura
from infrastructure.logging_setup import logger
from infrastructure.storage_adapter import StorageAdapter

# Configuración
from config import config

# Inicialización
app = FastAPI(
    title="OCR-FRONTEND API",
    description="API REST para el sistema de OCR y procesamiento de documentos",
    version="0.1.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorios necesarios
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Adapters
storage_adapter = StorageAdapter()

# Montar directorio estático para la interfaz web
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Endpoint raíz que proporciona información básica sobre la API."""
    return {
        "name": "OCR-FRONTEND API",
        "version": "0.1.0",
        "status": "online",
        "documentation": "/docs"
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Sube un archivo PDF para procesamiento OCR.

    Args:
        file: Archivo PDF a procesar

    Returns:
        JSON con el ID del documento y estado
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Solo se aceptan archivos PDF")

    # Generar ID único para el documento
    doc_id = str(uuid.uuid4())

    # Crear directorio para este documento
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(exist_ok=True)

    # Guardar el archivo
    pdf_path = doc_dir / f"document.pdf"
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validar el PDF
    try:
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=None)  # TODO: Implementar DocumentPort
        validation_result = validate_pdf_use_case.execute(pdf_path)

        # Guardar resultado de validación
        with open(doc_dir / "validation.json", "w") as f:
            import json
            json.dump(validation_result, f)

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "validation": validation_result
        }
    except Exception as e:
        logger.exception(f"Error validando PDF: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el PDF: {str(e)}")


@app.get("/api/process/{doc_id}")
async def process_document(doc_id: str, llm_mode: Optional[str] = None):
    """
    Procesa un documento previamente subido.

    Args:
        doc_id: ID del documento a procesar
        llm_mode: Modo de procesamiento LLM (summary, full, legal, off)

    Returns:
        JSON con el estado del procesamiento
    """
    doc_dir = UPLOAD_DIR / doc_id
    pdf_path = doc_dir / "document.pdf"

    if not doc_dir.exists() or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Configurar modo LLM si se especifica
    original_mode = config.llm_mode
    if llm_mode:
        config.llm_mode = llm_mode

    try:
        # TODO: Implementar llamada al caso de uso real cuando se completen los puertos
        # Por ahora, usamos el adaptador directamente
        from adapters.pymupdf_adapter import extract_markdown
        markdown_content = extract_markdown(pdf_path)

        # Guardar resultado
        output_path = storage_adapter.save_markdown(
            doc_id, markdown_content, output_dir=doc_dir)

        return {
            "document_id": doc_id,
            "status": "processed",
            "output_path": str(output_path),
            "llm_mode": llm_mode or original_mode
        }
    except Exception as e:
        logger.exception(f"Error procesando documento {doc_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el documento: {str(e)}")
    finally:
        # Restaurar modo LLM original
        if llm_mode:
            config.llm_mode = original_mode


@app.get("/api/result/{doc_id}")
async def get_result(doc_id: str, format: str = "markdown"):
    """
    Obtiene el resultado de un documento procesado.

    Args:
        doc_id: ID del documento
        format: Formato de salida (markdown, json)

    Returns:
        Archivo de resultado o JSON con metadatos
    """
    doc_dir = UPLOAD_DIR / doc_id

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if format == "markdown":
        markdown_file = doc_dir / f"{doc_id}.md"
        if not markdown_file.exists():
            raise HTTPException(
                status_code=404, detail="Resultado no disponible. Procese el documento primero.")
        return FileResponse(markdown_file, media_type="text/markdown")

    elif format == "json":
        json_file = doc_dir / f"{doc_id}.json"
        if not json_file.exists():
            raise HTTPException(
                status_code=404, detail="Resultado JSON no disponible")
        return FileResponse(json_file, media_type="application/json")

    else:
        raise HTTPException(status_code=400, detail="Formato no soportado")


@app.get("/api/documents")
async def list_documents():
    """
    Lista todos los documentos procesados.

    Returns:
        Lista de documentos con sus metadatos
    """
    documents = []

    for doc_dir in UPLOAD_DIR.iterdir():
        if doc_dir.is_dir():
            doc_id = doc_dir.name
            validation_file = doc_dir / "validation.json"
            markdown_file = doc_dir / f"{doc_id}.md"

            doc_info = {
                "document_id": doc_id,
                "uploaded_at": doc_dir.stat().st_ctime,
                "processed": markdown_file.exists(),
                "validated": validation_file.exists()
            }

            # Añadir información de validación si está disponible
            if validation_file.exists():
                import json
                with open(validation_file, "r") as f:
                    try:
                        doc_info["validation"] = json.load(f)
                    except:
                        doc_info["validation"] = {"error": "Formato inválido"}

            documents.append(doc_info)

    return {"documents": documents}


def start_api():
    """Inicia el servidor API."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_api()
