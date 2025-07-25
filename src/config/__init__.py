"""
Configuración centralizada para el sistema OCR.

Este módulo proporciona acceso a todas las configuraciones del sistema,
organizadas por categorías y con valores por defecto sensatos.
"""

# Configuración de API y credenciales
from .api_settings import load_api_settings

# Configuración del detector de idiomas
from .language_detection import get_config as get_language_config, SimpleLanguageDetector

# Configuración de LLM
from .llm_config import LLMConfig
from .state import LLM_MODE, LLM_PROVIDER

# Configuración de OCR
from .ocr_settings import OCRSettings

# Configuración general
from .settings import Settings, settings

# Configuración unificada (punto de entrada principal recomendado)
from .app_config import AppConfig, config

__all__ = [
    # Configuración unificada (recomendada)
    'AppConfig',
    'config',

    # API y credenciales
    'load_api_settings',

    # Detección de idiomas
    'get_language_config',
    'SimpleLanguageDetector',

    # Configuración LLM
    'LLMConfig',
    'LLM_MODE',
    'LLM_PROVIDER',

    # Configuración OCR
    'OCRSettings',

    # Configuración general
    'Settings',
    'settings',
]
