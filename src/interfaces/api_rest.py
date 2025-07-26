"""
Entry point for the OCR-FRONTEND API.

Este módulo sirve como punto de entrada para iniciar el servidor API.
La funcionalidad principal se ha movido a los módulos específicos en el paquete api/.
"""

import uvicorn
from infrastructure.logging_setup import logger
from .api import app
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

    def update_progress(stage: str, progress: int, message: str, details: str = None):
        """Actualiza el archivo de progreso con información detallada."""
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
                f"Progreso {doc_id}: {stage} - {progress}% - {message}")
            if details:
                logger.info(f"Detalles {doc_id}: {details}")
        except Exception as e:
            logger.error(f"Error guardando progreso para {doc_id}: {e}")

    try:
        update_progress(
            "iniciando", 0, "Iniciando procesamiento del documento",
            "Preparando entorno y validando parámetros")

        # Validación inicial más detallada
        logger.info(f"Extrayendo contenido del PDF: {doc_id}")
        update_progress("validando", 10, "Validando documento PDF",
                        "Verificando integridad y estructura del archivo")

        # Agregar validación explícita
        try:
            validate_pdf_use_case = ValidatePDFUseCase(
                document_port=document_adapter)
            validation_result = validate_pdf_use_case.execute(pdf_path)

            if not validation_result.get("valid", False):
                update_progress("error", -1, "Documento PDF inválido",
                                f"Error de validación: {validation_result.get('message', 'Documento corrupto o ilegible')}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Documento inválido: {validation_result.get('message', 'PDF corrupto')}")

            update_progress("validado", 20, "Documento validado correctamente",
                            f"Total: {validation_result['total_pages']} páginas, "
                            f"Escaneadas: {validation_result['scanned_pages']}, "
                            f"Digitales: {validation_result['digital_pages']}")

        except HTTPException:
            raise
        except Exception as e:
            update_progress("error", -1, "Error en validación", str(e))
            raise

        update_progress("extrayendo", 25, "Extrayendo texto del PDF",
                        "Aplicando OCR y extracción de texto según el tipo de página")

        # TODO: Implementar llamada al caso de uso real cuando se completen los puertos
        # Por ahora, usamos el adaptador directamente
        from adapters.pymupdf_adapter import extract_markdown

        update_progress("procesando", 50,
                        "Aplicando OCR y extracción de texto",
                        "Procesando páginas individuales y detectando tablas")

        try:
            markdown_content = extract_markdown(pdf_path)

            if not markdown_content or len(markdown_content.strip()) < 10:
                update_progress("error", -1, "Contenido vacío o insuficiente",
                                "El PDF no contiene texto extraíble o está completamente vacío")
                raise HTTPException(
                    status_code=422,
                    detail="El documento no contiene contenido procesable")

            logger.info(f"Extracción de contenido completada: {doc_id}")

        except HTTPException:
            raise
        except Exception as e:
            update_progress(
                "error", -1, "Error en extracción de contenido", str(e))
            raise

        update_progress("guardando", 75, "Guardando resultado",
                        "Generando archivo Markdown y metadatos")

        # Guardar resultado
        try:
            output_path = storage_adapter.save_markdown(
                doc_id, markdown_content)
            logger.info(f"Resultado guardado en: {output_path}")

        except Exception as e:
            update_progress("error", -1, "Error guardando resultado", str(e))
            raise

        update_progress("completado", 100,
                        "Procesamiento completado exitosamente",
                        f"Archivo generado: {output_path.name}, "
                        f"Tamaño: {len(markdown_content)} caracteres")

        return {
            "document_id": doc_id,
            "status": "processed",
            "output_path": str(output_path),
            "llm_mode": llm_mode or original_mode,
            "message": "Documento procesado exitosamente",
            "content_stats": {
                "characters": len(markdown_content),
                "pages": validation_result.get("total_pages", "unknown"),
                "scanned_pages": validation_result.get("scanned_pages", "unknown")
            },
            "timestamp": time.time()
        }
    except Exception as e:
        error_msg = f"Error en el procesamiento: {str(e)}"
        error_details = f"Tipo: {type(e).__name__}, Documento: {doc_id}, Archivo: {pdf_path.name}"
        update_progress("error", -1, error_msg, error_details)
        logger.exception(f"Error procesando documento {doc_id}: {e}")

        # Proporcionar información de diagnóstico más detallada
        diagnostic_info = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "document_id": doc_id,
            "file_exists": pdf_path.exists(),
            "file_size": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "timestamp": time.time()
        }

        # Guardar información de diagnóstico
        try:
            with open(doc_dir / "error_diagnostic.json", "w") as f:
                json.dump(diagnostic_info, f, indent=2)
        except Exception as diag_error:
            logger.error(f"No se pudo guardar diagnóstico: {diag_error}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al procesar el documento",
                "message": str(e),
                "type": type(e).__name__,
                "document_id": doc_id,
                "diagnostic_saved": True
            })
    finally:
        # Restaurar modo LLM original
        if llm_mode:
            logger.info(f"Restaurando modo LLM original: {original_mode}")
            config.llm_mode = original_mode


@app.get("/api/progress/{doc_id}")
async def get_progress(doc_id: str):
    """
    Obtiene el progreso del procesamiento de un documento con información detallada.

    Args:
        doc_id: ID del documento

    Returns:
        JSON con información completa de progreso y diagnóstico
    """
    doc_dir = UPLOAD_DIR / doc_id
    progress_file = doc_dir / "progress.json"
    error_diagnostic_file = doc_dir / "error_diagnostic.json"

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Información básica del documento
    doc_info = {
        "document_id": doc_id,
        "directory_exists": doc_dir.exists(),
        "pdf_exists": (doc_dir / "document.pdf").exists(),
        "created_at": doc_dir.stat().st_ctime if doc_dir.exists() else None
    }

    # Si no hay archivo de progreso
    if not progress_file.exists():
        return {
            **doc_info,
            "stage": "no_iniciado",
            "progress": 0,
            "message": "Procesamiento no iniciado",
            "details": "El documento ha sido subido pero el procesamiento no ha comenzado",
            "status": "waiting",
            "timestamp": None
        }

    try:
        with open(progress_file, "r") as f:
            progress_data = json.load(f)

        # Agregar información adicional
        result = {
            **doc_info,
            **progress_data
        }

        # Si hay error, incluir información de diagnóstico
        if progress_data.get("status") == "error" and error_diagnostic_file.exists():
            try:
                with open(error_diagnostic_file, "r") as f:
                    diagnostic_data = json.load(f)
                result["diagnostic"] = diagnostic_data
            except Exception as e:
                logger.error(f"Error leyendo diagnóstico para {doc_id}: {e}")
                result["diagnostic"] = {
                    "error": "No se pudo leer el diagnóstico"}

        # Agregar estimación de tiempo si está en progreso
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
            "details": f"Error del sistema: {str(e)}",
            "status": "error",
            "timestamp": time.time()
        }


@app.get("/api/logs/{doc_id}")
async def get_processing_logs(doc_id: str, lines: int = 50):
    """
    Obtiene los logs de procesamiento de un documento específico.

    Args:
        doc_id: ID del documento
        lines: Número de líneas de log a retornar (default: 50)

    Returns:
        JSON con los logs del procesamiento
    """
    doc_dir = UPLOAD_DIR / doc_id

    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Buscar archivos de log relacionados con este documento
    log_entries = []

    try:
        # Leer logs del sistema (esto es un ejemplo, en producción usarías un sistema de logs más robusto)
        import subprocess

        # Buscar en logs del sistema por el document_id
        try:
            result = subprocess.run(
                ["grep", "-n", doc_id, "/var/log/app.log"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                log_entries.extend(result.stdout.strip().split('\n'))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Si no hay logs del sistema, buscar en archivos locales
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

        # Limitar número de líneas
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


@app.get("/api/health")
async def health_check():
    """
    Endpoint de salud del sistema con información detallada.

    Returns:
        JSON con estado del sistema y componentes
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        # Verificar componentes del sistema
        components_to_check = [
            ("storage", storage_adapter),
            ("document_adapter", document_adapter),
            ("upload_directory", UPLOAD_DIR)
        ]

        for component_name, component in components_to_check:
            try:
                if component_name == "upload_directory":
                    # Verificar directorio
                    component_status = {
                        "status": "healthy" if component.exists() else "error",
                        "exists": component.exists(),
                        "writable": component.exists() and component.is_dir(),
                        "path": str(component)
                    }
                else:
                    # Para otros componentes, verificar que existen
                    component_status = {
                        "status": "healthy" if component else "error",
                        "available": bool(component)
                    }

                health_status["components"][component_name] = component_status

            except Exception as e:
                health_status["components"][component_name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["status"] = "degraded"

        # Verificar dependencias críticas
        try:
            import fitz
            health_status["components"]["pymupdf"] = {
                "status": "healthy", "version": fitz.version}
        except ImportError as e:
            health_status["components"]["pymupdf"] = {
                "status": "error", "error": str(e)}
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
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
