"""
Fábrica de proveedores LLM.

Este módulo implementa el patrón Factory para crear instancias
de diferentes proveedores LLM basados en la configuración.
"""

from adapters.providers.gemini_provider import GeminiProvider
from adapters.providers.openai_provider import OpenAIProvider
from typing import Dict, Any, Optional, Type
from domain.ports.llm_provider import LLMProvider
from shared.util.config import AppConfig
from infrastructure.logging_setup import logger

# Instancia de configuración
app_config = AppConfig()

# Importaciones adelantadas para mejorar rendimiento


class LLMProviderFactory:
    """Fábrica para crear instancias de proveedores LLM."""

    # Registro de proveedores disponibles
    _providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider
    }

    # Caché de proveedores ya inicializados
    _provider_cache = {}

    @classmethod
    def create_provider(cls, provider_type: str = None) -> Optional[LLMProvider]:
        """
        Crea una instancia del proveedor LLM especificado.

        Args:
            provider_type: Tipo de proveedor ("openai" o "gemini")
                           Si es None, se intentará determinar basado en las claves disponibles.

        Returns:
            Una instancia de LLMProvider inicializada o None si falla.
        """
        try:
            # Verificar si ya existe en caché
            if provider_type and provider_type in cls._provider_cache:
                logger.debug(f"Usando proveedor {provider_type} desde caché")
                return cls._provider_cache[provider_type]

            # Cargar configuración
            api_config = {
                "openai": {
                    "api_key": app_config.openai.api_key,
                    "org_id": app_config.openai.org_id,
                    "model": app_config.openai.model,
                    "max_retries": app_config.openai.max_retries
                },
                "gemini": {
                    "api_key": app_config.gemini.api_key,
                    "model": app_config.gemini.model,
                    "max_retries": app_config.gemini.max_retries
                }
            }

            # Determinar proveedor automáticamente si no se especifica
            if not provider_type:
                if "openai" in api_config and api_config["openai"].get("api_key"):
                    provider_type = "openai"
                elif "gemini" in api_config and api_config["gemini"].get("api_key"):
                    provider_type = "gemini"
                else:
                    logger.warning(
                        "No se encontró ninguna configuración de API válida")
                    return None

            # Crear e inicializar el proveedor apropiado
            if provider_type in cls._providers:
                provider_class = cls._providers[provider_type]
                provider = provider_class()

                # Inicializar con la configuración correspondiente
                if provider_type in api_config:
                    provider.initialize(api_config[provider_type])

                    # Guardar en caché
                    cls._provider_cache[provider_type] = provider
                    return provider
                else:
                    logger.error(
                        f"Configuración no encontrada para {provider_type}")
                    return None
            else:
                logger.error(f"Tipo de proveedor desconocido: {provider_type}")
                return None

        except Exception as e:
            logger.error(f"Error al crear proveedor LLM: {e}")
            return None

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Registra un nuevo tipo de proveedor en la fábrica.

        Args:
            name: Nombre único para el proveedor
            provider_class: Clase que implementa LLMProvider
        """
        cls._providers[name] = provider_class
        logger.info(f"Proveedor {name} registrado en la fábrica LLM")
