"""
Gestión centralizada de configuración.

Este módulo implementa un sistema unificado de configuración que elimina
la duplicación entre múltiples módulos de configuración existentes.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


@dataclass(frozen=True)
class OCRConfig:
    """Configuración del sistema OCR."""
    dpi: int = int(os.getenv('OCR_DPI', '300'))
    language: str = os.getenv('OCR_LANG', 'spa')
    psm: int = int(os.getenv('OCR_PSM', '3'))
    oem: int = int(os.getenv('OCR_OEM', '3'))
    timeout: int = int(os.getenv('OCR_TIMEOUT', '60'))


@dataclass(frozen=True)
class LLMConfig:
    """Configuración de LLM."""
    mode: str = os.getenv('LLM_MODE', 'prompt')
    provider: Optional[str] = os.getenv('LLM_PROVIDER')
    temperature: float = float(os.getenv('LLM_TEMPERATURE', '0.1'))
    max_tokens: int = int(os.getenv('LLM_MAX_TOKENS', '500'))
    timeout: int = int(os.getenv('LLM_TIMEOUT', '30'))


@dataclass(frozen=True)
class OpenAIConfig:
    """Configuración específica de OpenAI."""
    api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    org_id: Optional[str] = os.getenv('OPENAI_ORG_ID')
    model: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    max_retries: int = int(os.getenv('OPENAI_MAX_RETRIES', '3'))


@dataclass(frozen=True)
class GeminiConfig:
    """Configuración específica de Google Gemini."""
    api_key: Optional[str] = os.getenv('GEMINI_API_KEY')
    model: str = os.getenv('GEMINI_MODEL', 'gemini-pro')
    max_retries: int = int(os.getenv('GEMINI_MAX_RETRIES', '3'))


@dataclass(frozen=True)
class APIConfig:
    """Configuración de la API REST."""
    host: str = os.getenv('API_HOST', '127.0.0.1')
    port: int = int(os.getenv('API_PORT', '8000'))
    debug: bool = os.getenv('API_DEBUG', 'false').lower() == 'true'
    cors_origins: List[str] = field(
        default_factory=lambda: os.getenv('CORS_ORIGINS', '*').split(','))


@dataclass(frozen=True)
class LoggingConfig:
    """Configuración del sistema de logging."""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    format: str = os.getenv('LOG_FORMAT', 'detailed')
    max_file_size: str = os.getenv('LOG_MAX_SIZE', '10MB')
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))


class AppConfig:
    """Configuración unificada de la aplicación."""

    def __init__(self):
        self.ocr = OCRConfig()
        self.llm = LLMConfig()
        self.openai = OpenAIConfig()
        self.gemini = GeminiConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()

    def is_llm_enabled(self) -> bool:
        """Verifica si el procesamiento LLM está habilitado."""
        return self.llm.mode != 'off' and self.llm.provider is not None

    def get_available_llm_providers(self) -> list:
        """Retorna una lista de proveedores LLM disponibles."""
        providers = []
        if self.openai.api_key:
            providers.append('openai')
        if self.gemini.api_key:
            providers.append('gemini')
        return providers

    def get_llm_provider_config(self, provider: str) -> Dict[str, Any]:
        """Obtiene la configuración específica de un proveedor LLM."""
        if provider == 'openai':
            return {
                'api_key': self.openai.api_key,
                'org_id': self.openai.org_id,
                'model': self.openai.model,
                'max_retries': self.openai.max_retries,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens,
                'timeout': self.llm.timeout
            }
        elif provider == 'gemini':
            return {
                'api_key': self.gemini.api_key,
                'model': self.gemini.model,
                'max_retries': self.gemini.max_retries,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens,
                'timeout': self.llm.timeout
            }
        else:
            raise ValueError(f"Provider desconocido: {provider}")

    def validate_configuration(self) -> Dict[str, bool]:
        """Valida la configuración actual."""
        validation = {
            'ocr_valid': self.ocr.dpi > 0 and self.ocr.language.strip() != '',
            'api_valid': 1 <= self.api.port <= 65535,
            'logging_valid': self.logging.level in ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            'llm_valid': True
        }

        if self.is_llm_enabled():
            available_providers = self.get_available_llm_providers()
            validation['llm_valid'] = (
                self.llm.provider in available_providers and
                len(available_providers) > 0
            )

        return validation

    # Propiedad de compatibilidad para código antiguo
    @property
    def language(self):
        """Propiedad de compatibilidad para código antiguo que accede a config.language"""
        return {
            "default_language": self.ocr.language,
            "min_confidence": 0.7,
            "use_fasttext": True,
            "fasttext_model_path": "src/shared/storage/data/models/fasttext/lid.176.ftz",
            "supported_languages": ["es", "en", "zh", "fr", "de"]
        }


# Instancia global de configuración
config = AppConfig()
