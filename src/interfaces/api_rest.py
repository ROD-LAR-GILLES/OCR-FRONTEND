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
import json
import time

# Importaciones del dominio
from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from domain.use_cases.validate_pdf import ValidatePDFUseCase

# Importaciones de infraestructura
from infrastructure.logging_setup import logger
from infrastructure.storage_adapter import StorageAdapter
from infrastructure.document_adapter import DocumentAdapter

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
document_adapter = DocumentAdapter()

# Montar directorio estático para la interfaz web
app.mount("/static", StaticFiles(directory="static"), name="static")


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


@app.get("/api/status")
async def get_system_status():
    """Endpoint para verificar el estado del sistema."""
    logger.info("Verificando estado del sistema")

    try:
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


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Sube un archivo PDF para procesamiento OCR.

    Args:
        file: Archivo PDF a procesar

    Returns:
        JSON con el ID del documento y estado
    """
    logger.info(f"Iniciando carga de archivo: {file.filename}")

    if not file.filename.endswith('.pdf'):
        logger.error(f"Tipo de archivo inválido: {file.filename}")
        raise HTTPException(
            status_code=400, detail="Solo se aceptan archivos PDF")

    # Generar ID único para el documento
    doc_id = str(uuid.uuid4())
    logger.info(f"Generado ID de documento: {doc_id}")

    # Crear directorio para este documento
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(exist_ok=True)
    logger.info(f"Creado directorio de trabajo: {doc_dir}")

    # Guardar el archivo
    pdf_path = doc_dir / f"document.pdf"
    logger.info(f"Guardando archivo PDF en: {pdf_path}")

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Archivo guardado exitosamente: {pdf_path}")
    except Exception as e:
        logger.error(f"Error al guardar archivo: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al guardar archivo: {str(e)}")

    # Validar el PDF
    logger.info(f"Iniciando validación del PDF: {doc_id}")
    try:
        validate_pdf_use_case = ValidatePDFUseCase(
            document_port=document_adapter)
        validation_result = validate_pdf_use_case.execute(pdf_path)
        logger.info(f"Validación completada para documento: {doc_id}")

        # Guardar resultado de validación
        with open(doc_dir / "validation.json", "w") as f:
            json.dump(validation_result, f)
        logger.info(f"Resultado de validación guardado: {doc_id}")

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
    logger.info(f"Iniciando procesamiento del documento: {doc_id}")

    doc_dir = UPLOAD_DIR / doc_id
    pdf_path = doc_dir / "document.pdf"

    if not doc_dir.exists() or not pdf_path.exists():
        logger.error(f"Documento no encontrado: {doc_id}")
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    logger.info(f"Documento encontrado, iniciando procesamiento: {pdf_path}")

    # Configurar modo LLM si se especifica
    original_mode = config.llm_mode
    if llm_mode:
        logger.info(f"Configurando modo LLM: {llm_mode}")
        config.llm_mode = llm_mode

    # Guardar estado de progreso
    progress_file = doc_dir / "progress.json"

    def update_progress(stage: str, progress: int, message: str):
        """Actualiza el archivo de progreso."""
        progress_data = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": time.time()
        }
        with open(progress_file, "w") as f:
            json.dump(progress_data, f)
        logger.info(f"Progreso {doc_id}: {stage} - {progress}% - {message}")

    try:
        update_progress(
            "iniciando", 0, "Iniciando procesamiento del documento")

        logger.info(f"Extrayendo contenido del PDF: {doc_id}")
        update_progress("extrayendo", 25, "Extrayendo texto del PDF")

        # TODO: Implementar llamada al caso de uso real cuando se completen los puertos
        # Por ahora, usamos el adaptador directamente
        from adapters.pymupdf_adapter import extract_markdown

        update_progress("procesando", 50,
                        "Aplicando OCR y extracción de texto")
        markdown_content = extract_markdown(pdf_path)
        logger.info(f"Extracción de contenido completada: {doc_id}")

        update_progress("guardando", 75, "Guardando resultado")

        # Guardar resultado
        output_path = storage_adapter.save_markdown(doc_id, markdown_content)
        logger.info(f"Resultado guardado en: {output_path}")

        update_progress("completado", 100,
                        "Procesamiento completado exitosamente")

        return {
            "document_id": doc_id,
            "status": "processed",
            "output_path": str(output_path),
            "llm_mode": llm_mode or original_mode,
            "message": "Documento procesado exitosamente",
            "timestamp": time.time()
        }
    except Exception as e:
        error_msg = f"Error en el procesamiento: {str(e)}"
        update_progress("error", -1, error_msg)
        logger.exception(f"Error procesando documento {doc_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el documento: {str(e)}")
    finally:
        # Restaurar modo LLM original
        if llm_mode:
            logger.info(f"Restaurando modo LLM original: {original_mode}")
            config.llm_mode = original_mode


# Nuevo endpoint para obtener el progreso de procesamiento
@app.get("/api/progress/{doc_id}")
async def get_progress(doc_id: str):
    """
    Obtiene el progreso del procesamiento de un documento.

    Args:
        doc_id: ID del documento

    Returns:
        JSON con información de progreso
    """
    doc_dir = UPLOAD_DIR / doc_id
    progress_file = doc_dir / "progress.json"

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if not progress_file.exists():
        return {
            "document_id": doc_id,
            "stage": "no_iniciado",
            "progress": 0,
            "message": "Procesamiento no iniciado",
            "timestamp": None
        }

    try:
        with open(progress_file, "r") as f:
            progress_data = json.load(f)
        return {
            "document_id": doc_id,
            **progress_data
        }
    except Exception as e:
        logger.error(f"Error leyendo progreso para {doc_id}: {e}")
        return {
            "document_id": doc_id,
            "stage": "error",
            "progress": -1,
            "message": "Error al leer progreso",
            "timestamp": time.time()
        }


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
                status_code=404, detail="Resultado no disponible. Procese el documento primero.")

        logger.info(f"Enviando archivo Markdown: {markdown_file}")
        return FileResponse(markdown_file, media_type="text/markdown")

    elif format == "json":
        json_file = doc_dir / f"{doc_id}.json"
        if not json_file.exists():
            logger.warning(
                f"Archivo JSON no encontrado para documento: {doc_id}")
            raise HTTPException(
                status_code=404, detail="Resultado JSON no disponible")

        logger.info(f"Enviando archivo JSON: {json_file}")
        return FileResponse(json_file, media_type="application/json")

    else:
        logger.error(f"Formato no soportado: {format}")
        raise HTTPException(status_code=400, detail="Formato no soportado")


@app.get("/api/documents")
async def list_documents():
    """
    Lista todos los documentos procesados.

    Returns:
        Lista de documentos con sus metadatos
    """
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

                # Añadir información de validación si está disponible
                if validation_file.exists():
                    try:
                        with open(validation_file, "r") as f:
                            doc_info["validation"] = json.load(f)
                    except Exception as e:
                        logger.error(
                            f"Error leyendo validación para {doc_id}: {e}")
                        doc_info["validation"] = {"error": "Formato inválido"}

                # Añadir información de progreso si está disponible
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
            status_code=500, detail=f"Error al listar documentos: {str(e)}")


def start_api():
    """Inicia el servidor API."""
    logger.info("Iniciando servidor API en puerto 8000")
    try:
        import uvicorn
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
