"""
Adaptadores para la arquitectura hexagonal.

Este módulo contiene implementaciones de las interfaces definidas en domain/ports/.
Los adaptadores proporcionan la capa de comunicación entre el dominio y las bibliotecas/servicios externos.
"""

# Exportaciones principales para facilitar imports
from .pymupdf_adapter import extract_markdown
from .ocr_adapter import perform_ocr_on_page, needs_ocr
from .llm_refiner import LLMRefiner
from .table_detector import TableDetector
from .language_detector import LanguageDetector
from .language_factory import get_language_detector, LanguageDetectorFactory

# Proveedor Factory
from .providers.llm_factory import LLMProviderFactory

__all__ = [
    'extract_markdown',           # Función principal para extraer Markdown de PDFs
    'perform_ocr_on_page',        # Función para OCR en una página
    'needs_ocr',                  # Función para determinar si una página necesita OCR
    'LLMRefiner',                 # Clase para refinamiento de texto con LLMs
    'TableDetector',              # Detector de tablas en imágenes
    # Detector de idiomas (implementación estándar)
    'LanguageDetector',
    'get_language_detector',      # Función para obtener un detector según configuración
    'LanguageDetectorFactory',    # Fábrica para crear detectores de idiomas
    'LLMProviderFactory',         # Fábrica para crear proveedores LLM
]
