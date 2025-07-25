"""
Adaptadores para la arquitectura hexagonal.

Este módulo contiene implementaciones de las interfaces definidas en domain/ports/.
Los adaptadores proporcionan la capa de comunicación entre el dominio y las bibliotecas/servicios externos.
"""

# Exportaciones principales para facilitar imports
from .document_processing import (
    extract_markdown,
    perform_ocr_on_page,
    needs_ocr,
    TableDetector,
    run_parallel_ocr
)
from .llm_services import LLMRefiner
from .language_services import (
    LanguageDetector,
    get_language_detector,
    LanguageDetectorFactory,
    FastTextLanguageDetector
)

# Proveedor Factory
from .providers.llm_factory import LLMProviderFactory

__all__ = [
    'extract_markdown',           # Función principal para extraer Markdown de PDFs
    'perform_ocr_on_page',        # Función para OCR en una página
    'needs_ocr',                  # Función para determinar si una página necesita OCR
    'run_parallel_ocr',           # Función para ejecutar OCR en paralelo
    'LLMRefiner',                 # Clase para refinamiento de texto con LLMs
    'TableDetector',              # Detector de tablas en imágenes
    # Detectores de idiomas
    'LanguageDetector',           # Detector básico
    'FastTextLanguageDetector',   # Detector avanzado con FastText
    'get_language_detector',      # Función para obtener un detector según configuración
    'LanguageDetectorFactory',    # Fábrica para crear detectores de idiomas
    'LLMProviderFactory',         # Fábrica para crear proveedores LLM
]
