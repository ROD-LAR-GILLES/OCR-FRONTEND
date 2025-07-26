"""Modelos de datos para la API."""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class DocumentResponse(BaseModel):
    """Modelo para la respuesta de documentos."""
    document_id: str
    filename: str
    status: str
    validation: Dict[str, Any]
    message: str
    timestamp: float


class ValidationResult(BaseModel):
    """Modelo para el resultado de validación."""
    valid: bool
    total_pages: int
    scanned_pages: int
    digital_pages: int
    message: str
    metadata: Dict[str, Any]


class ProcessingProgress(BaseModel):
    """Modelo para el progreso del procesamiento."""
    stage: str
    progress: int
    message: str
    details: Optional[str]
    status: str
    timestamp: float


class HealthStatus(BaseModel):
    """Modelo para el estado de salud del sistema."""
    status: str
    timestamp: float
    components: Dict[str, Dict[str, Any]]
    error: Optional[str]
