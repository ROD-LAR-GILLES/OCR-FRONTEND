"""
API REST para el sistema OCR-FRONTEND.
"""
from .routes import processing_routes
from .routes import health_routes
from .routes import document_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from infrastructure.logging_setup import logger
from infrastructure.storage_adapter import StorageAdapter
from infrastructure.document_adapter import DocumentAdapter

# Inicialización de la aplicación
app = FastAPI(
    title="OCR-FRONTEND API",
    description="API REST para el sistema de OCR y procesamiento de documentos",
    version="0.1.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio estático
app.mount("/static", StaticFiles(directory="static"), name="static")

# Importar rutas

# Registrar rutas
app.include_router(document_routes.router, prefix="/api")
app.include_router(health_routes.router, prefix="/api")
app.include_router(processing_routes.router, prefix="/api")
