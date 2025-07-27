"""
Composition Root mejorado para inyección de dependencias.

Este módulo implementa el patrón Composition Root de manera más robusta,
centralizando toda la creación e inyección de dependencias.
"""
from typing import Dict, Any, Optional
from pathlib import Path

# Puertos del dominio
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort

# Casos de uso de la aplicación
from application.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from application.use_cases.validate_pdf import ValidatePDFUseCase

# Servicios de aplicación
from application.services.configuration_service import ConfigurationService

# Adaptadores de infraestructura
from infrastructure.document_adapter import DocumentAdapter
from infrastructure.storage_adapter import StorageAdapter

# Adaptadores de LLM
from adapters.llm_refiner import LLMRefiner

# Configuración centralizada
from shared.constants.config import config
from shared.constants.directories import Directories
from shared.utils.error_handling import ConfigurationError, ErrorContext


class DependencyContainer:
    """Contenedor de dependencias para inyección."""

    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._configuration_service: Optional[ConfigurationService] = None

        # Asegurar que los directorios existan
        Directories.ensure_all_exist()

    @property
    def configuration_service(self) -> ConfigurationService:
        """Obtiene el servicio de configuración."""
        if self._configuration_service is None:
            self._configuration_service = ConfigurationService()
        return self._configuration_service

    def get_document_port(self) -> DocumentPort:
        """Obtiene una instancia del puerto de documentos."""
        if 'document_port' not in self._instances:
            self._instances['document_port'] = DocumentAdapter()
        return self._instances['document_port']

    def get_storage_port(self) -> StoragePort:
        """Obtiene una instancia del puerto de almacenamiento."""
        if 'storage_port' not in self._instances:
            self._instances['storage_port'] = StorageAdapter()
        return self._instances['storage_port']

    def get_storage_adapter(self) -> StorageAdapter:
        """Obtiene una instancia del adaptador de almacenamiento (alias para compatibilidad)."""
        return self.get_storage_port()

    def get_llm_port(self) -> LLMPort:
        """Obtiene una instancia del puerto LLM."""
        if 'llm_port' not in self._instances:
            try:
                # Configurar el refinador LLM basado en la configuración actual
                llm_config = self.configuration_service.get_llm_configuration()

                if llm_config['is_enabled'] and llm_config['provider']:
                    provider_config = config.get_llm_provider_config(
                        llm_config['provider'])
                    self._instances['llm_port'] = LLMRefiner(
                        provider=llm_config['provider'],
                        config=provider_config
                    )
                else:
                    # Crear un adaptador LLM deshabilitado
                    self._instances['llm_port'] = LLMRefiner(
                        provider=None,
                        config={}
                    )

            except Exception as e:
                context = ErrorContext(
                    operation="create_llm_port",
                    additional_data={
                        'llm_config': self.configuration_service.get_llm_configuration()}
                )
                raise ConfigurationError(
                    f"No se pudo crear el puerto LLM: {e}",
                    context,
                    e
                )

        return self._instances['llm_port']

    def get_pdf_to_markdown_use_case(self) -> PDFToMarkdownUseCase:
        """Obtiene una instancia del caso de uso PDF a Markdown."""
        return PDFToMarkdownUseCase(
            document_port=self.get_document_port(),
            storage_port=self.get_storage_port(),
            llm_port=self.get_llm_port()
        )

    def get_validate_pdf_use_case(self) -> ValidatePDFUseCase:
        """Obtiene una instancia del caso de uso de validación de PDF."""
        return ValidatePDFUseCase(
            document_port=self.get_document_port()
        )

    def reconfigure_llm(self, provider: str, provider_config: Dict[str, Any]) -> None:
        """
        Reconfigura el proveedor LLM.

        Args:
            provider: Nombre del proveedor
            provider_config: Configuración del proveedor
        """
        try:
            # Actualizar configuración persistente
            self.configuration_service.update_llm_provider(
                provider, provider_config)

            # Resetear instancia del puerto LLM para forzar recreación
            if 'llm_port' in self._instances:
                del self._instances['llm_port']

            # Crear nueva instancia con la configuración actualizada
            self.get_llm_port()

        except Exception as e:
            context = ErrorContext(
                operation="reconfigure_llm",
                additional_data={'provider': provider,
                                 'config': provider_config}
            )
            raise ConfigurationError(
                f"No se pudo reconfigurar el LLM: {e}",
                context,
                e
            )

    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado del sistema y sus dependencias.

        Returns:
            Dict[str, Any]: Estado del sistema
        """
        return self.configuration_service.get_system_status()

    def reset_all_instances(self) -> None:
        """Resetea todas las instancias almacenadas."""
        self._instances.clear()
        self._configuration_service = None


class CompositionRoot:
    """Composition Root principal para la aplicación."""

    def __init__(self):
        self.container = DependencyContainer()

    def create_cli_application(self):
        """
        Crea la aplicación CLI con todas las dependencias inyectadas.

        Returns:
            Función main_loop configurada con dependencias
        """
        from interfaces.cli.menu import main_loop

        # Inyectar dependencias en el módulo CLI
        return lambda: main_loop(
            pdf_to_markdown_use_case=self.container.get_pdf_to_markdown_use_case(),
            validate_pdf_use_case=self.container.get_validate_pdf_use_case(),
            configuration_service=self.container.configuration_service
        )

    def get_use_case(self, use_case_name: str):
        """
        Obtiene un caso de uso específico por nombre.

        Args:
            use_case_name: Nombre del caso de uso

        Returns:
            Instancia del caso de uso
        """
        use_cases = {
            'pdf_to_markdown': self.container.get_pdf_to_markdown_use_case,
            'validate_pdf': self.container.get_validate_pdf_use_case
        }

        if use_case_name not in use_cases:
            raise ValueError(f"Caso de uso desconocido: {use_case_name}")

        return use_cases[use_case_name]()


# Instancia global del composition root
composition_root = CompositionRoot()
