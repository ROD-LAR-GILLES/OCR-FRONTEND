"""
Composition Root para la aplicación.

Este módulo implementa el patrón Composition Root, donde se crea
y configura toda la estructura de dependencias de la aplicación.
También incluye el contenedor de dependencias centralizado.
"""
from typing import Dict, Any, Optional
from pathlib import Path

# Importaciones de dominio
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort

# Importaciones de casos de uso
from application.pdf_use_cases import PDFToMarkdownUseCase, ValidatePDFUseCase, UseCaseFactory

# Importaciones de aplicación
from application.configuration_service import ConfigurationService

# Importaciones de infraestructura
from infrastructure.document_adapter import DocumentAdapter
from infrastructure.storage_adapter import StorageAdapter

# Importaciones de adaptadores
from adapters.llm_services import LLMRefiner

# Importaciones de utilidades compartidas
from shared.util.config import config
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

    def reset(self) -> None:
        """Reinicia todas las instancias (útil para pruebas)."""
        self._instances = {}
        self._configuration_service = None


class CompositionRoot:
    """
    Composition Root para la aplicación.

    Esta clase es responsable de crear y configurar todos los casos
    de uso y componentes de la aplicación.
    """

    def __init__(self, container: DependencyContainer):
        """
        Inicializa el Composition Root con un contenedor de dependencias.

        Args:
            container: Contenedor de dependencias a utilizar
        """
        self._container = container

    def create_pdf_to_markdown_use_case(self) -> PDFToMarkdownUseCase:
        """
        Crea un caso de uso para convertir PDF a Markdown.

        Returns:
            Una nueva instancia configurada del caso de uso
        """
        return PDFToMarkdownUseCase(
            document_port=self._container.get_document_port(),
            storage_port=self._container.get_storage_port(),
            llm_port=self._container.get_llm_port()
        )

    def create_validate_pdf_use_case(self) -> ValidatePDFUseCase:
        """
        Crea un caso de uso para validar documentos PDF.

        Returns:
            Una nueva instancia configurada del caso de uso
        """
        return ValidatePDFUseCase(
            document_port=self._container.get_document_port()
        )

    def process_pdf(self, pdf_path: Path, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa un PDF completo, desde la validación hasta la conversión a Markdown.

        Args:
            pdf_path: Ruta al archivo PDF a procesar
            options: Opciones de procesamiento

        Returns:
            Resultados del procesamiento
        """
        # Crear opciones predeterminadas si no se proporcionan
        if options is None:
            options = {}

        # Obtener configuración actual si no se especifica
        if 'refine_with_llm' not in options:
            llm_config = self._container.configuration_service.get_llm_configuration()
            options['refine_with_llm'] = llm_config['is_enabled']

        # Ejecutar validación primero
        validate_use_case = self.create_validate_pdf_use_case()
        validation_result = validate_use_case.execute(pdf_path)

        # Si la validación es exitosa, convertir a Markdown
        if validation_result['is_valid']:
            convert_use_case = self.create_pdf_to_markdown_use_case()
            result = convert_use_case.execute(pdf_path, options)

            # Combinar resultados
            result.update({
                'validation': validation_result
            })
            return result

        # Si no es válido, devolver solo el resultado de la validación
        return {
            'success': False,
            'validation': validation_result,
            'error': validation_result.get('error_message', 'Documento no válido')
        }


# Instancias globales de fácil acceso
container = DependencyContainer()
composition_root = CompositionRoot(container)
