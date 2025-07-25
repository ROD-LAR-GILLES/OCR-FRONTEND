"""
Servicio de gestión de configuración.

Este servicio centraliza toda la lógica de configuración y manejo de estado,
eliminando la duplicación entre múltiples módulos de configuración.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from shared.util.config import config, AppConfig
from shared.constants.directories import Directories
from shared.utils.error_handling import ConfigurationError, ErrorContext


class ConfigurationService:
    """Servicio para gestionar la configuración de la aplicación."""

    def __init__(self):
        self._config_file = Directories.DATA / "app_config.json"
        self._ensure_config_directory()

    def _ensure_config_directory(self) -> None:
        """Asegura que el directorio de configuración exista."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)

    def save_configuration(self, config_data: Dict[str, Any]) -> None:
        """
        Guarda la configuración en un archivo JSON.

        Args:
            config_data: Datos de configuración a guardar

        Raises:
            ConfigurationError: Si hay un error al guardar la configuración
        """
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            context = ErrorContext(
                operation="save_configuration",
                file_path=str(self._config_file)
            )
            raise ConfigurationError(
                f"No se pudo guardar la configuración: {e}",
                context,
                e
            )

    def load_configuration(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo JSON.

        Returns:
            Dict[str, Any]: Datos de configuración cargados

        Raises:
            ConfigurationError: Si hay un error al cargar la configuración
        """
        try:
            if not self._config_file.exists():
                return {}

            with open(self._config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            context = ErrorContext(
                operation="load_configuration",
                file_path=str(self._config_file)
            )
            raise ConfigurationError(
                f"No se pudo cargar la configuración: {e}",
                context,
                e
            )

    def get_llm_configuration(self) -> Dict[str, Any]:
        """
        Obtiene la configuración específica de LLM.

        Returns:
            Dict[str, Any]: Configuración de LLM
        """
        return {
            'mode': config.llm.mode,
            'provider': config.llm.provider,
            'temperature': config.llm.temperature,
            'max_tokens': config.llm.max_tokens,
            'timeout': config.llm.timeout,
            'available_providers': config.get_available_llm_providers(),
            'is_enabled': config.is_llm_enabled()
        }

    def update_llm_provider(self, provider: str, settings: Dict[str, Any]) -> None:
        """
        Actualiza la configuración del proveedor LLM.

        Args:
            provider: Nombre del proveedor ('openai', 'gemini', etc.)
            settings: Configuración específica del proveedor

        Raises:
            ConfigurationError: Si el proveedor no es válido
        """
        try:
            saved_config = self.load_configuration()

            if 'llm' not in saved_config:
                saved_config['llm'] = {}

            saved_config['llm']['provider'] = provider
            saved_config['llm']['settings'] = settings

            self.save_configuration(saved_config)
        except Exception as e:
            context = ErrorContext(
                operation="update_llm_provider",
                additional_data={'provider': provider, 'settings': settings}
            )
            raise ConfigurationError(
                f"No se pudo actualizar el proveedor LLM: {e}",
                context,
                e
            )

    def get_ocr_configuration(self) -> Dict[str, Any]:
        """
        Obtiene la configuración específica de OCR.

        Returns:
            Dict[str, Any]: Configuración de OCR
        """
        return asdict(config.ocr)

    def get_api_configuration(self) -> Dict[str, Any]:
        """
        Obtiene la configuración específica de la API.

        Returns:
            Dict[str, Any]: Configuración de la API
        """
        return asdict(config.api)

    def validate_current_configuration(self) -> Dict[str, Any]:
        """
        Valida la configuración actual y retorna un reporte.

        Returns:
            Dict[str, Any]: Reporte de validación
        """
        validation = config.validate_configuration()

        issues = []
        for component, is_valid in validation.items():
            if not is_valid:
                issues.append(f"Configuración inválida en {component}")

        return {
            'is_valid': all(validation.values()),
            'validation_details': validation,
            'issues': issues,
            'available_llm_providers': config.get_available_llm_providers(),
            'llm_enabled': config.is_llm_enabled()
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado completo del sistema.

        Returns:
            Dict[str, Any]: Estado del sistema
        """
        directories_status = {}
        for name, path in Directories.get_all_paths().items():
            directories_status[name] = {
                'exists': path.exists(),
                'is_directory': path.is_dir() if path.exists() else False,
                'writable': path.is_dir() and os.access(path, os.W_OK) if path.exists() else False,
                'path': str(path)
            }

        return {
            'directories': directories_status,
            'configuration': self.validate_current_configuration(),
            'llm': self.get_llm_configuration(),
            'ocr': self.get_ocr_configuration(),
            'api': self.get_api_configuration()
        }


# Instancia global del servicio
configuration_service = ConfigurationService()
