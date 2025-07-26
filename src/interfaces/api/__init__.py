"""
Módulo de inicialización para la API REST.
"""
from . import endpoints, process, monitoring, results
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Inicialización
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

# Crear directorios necesarios
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Montar directorio estático para la interfaz web
app.mount("/static", StaticFiles(directory="static"), name="static")

# Importar rutas después de la inicialización para evitar importaciones circulares
