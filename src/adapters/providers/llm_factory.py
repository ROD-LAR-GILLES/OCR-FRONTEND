"""
Fábrica de proveedores LLM.

Este módulo implementa el patrón Factory para crear instancias
de diferentes proveedores LLM basados en la configuración.
"""

from typing import Dict, Any, Optional
from domain.ports.llm_provider import LLMProvider
from config.api_settings import load_api_settings
from infrastructure.logging_setup import logger

class LLMProviderFactory:
    """Fábrica para crear instancias de proveedores LLM."""
    
    @staticmethod
    def create_provider(provider_type: str = None) -> Optional[LLMProvider]:
        """
        Crea una instancia del proveedor LLM especificado.
        
        Args:
            provider_type: Tipo de proveedor ("openai" o "gemini")
                           Si es None, se intentará determinar basado en las claves disponibles.
                           
        Returns:
            Una instancia de LLMProvider inicializada o None si falla.
        """
        try:
            # Cargar configuración
            api_config = load_api_settings()
            
            # Determinar proveedor automáticamente si no se especifica
            if not provider_type:
                if "openai" in api_config and api_config["openai"].get("api_key"):
                    provider_type = "openai"
                elif "gemini" in api_config and api_config["gemini"].get("api_key"):
                    provider_type = "gemini"
                else:
                    logger.warning("No se encontró ninguna configuración de API válida")
                    return None
            
            # Crear e inicializar el proveedor apropiado
            if provider_type == "openai":
                from adapters.providers.openai_provider import OpenAIProvider
                provider = OpenAIProvider()
                provider.initialize(api_config["openai"])
                return provider
            elif provider_type == "gemini":
                from adapters.providers.gemini_provider import GeminiProvider
                provider = GeminiProvider()
                provider.initialize(api_config["gemini"])
                return provider
            else:
                logger.error(f"Tipo de proveedor desconocido: {provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error al crear proveedor LLM: {e}")
            return None
