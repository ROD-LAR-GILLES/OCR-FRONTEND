"""
Casos de uso para procesamiento de PDF.

Este módulo implementa todos los casos de uso relacionados con
el procesamiento de documentos PDF, incluyendo validación, conversión a Markdown,
y otras operaciones sobre archivos PDF.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Union, Generic, TypeVar, TYPE_CHECKING

# Usamos TYPE_CHECKING para evitar importaciones circulares
if TYPE_CHECKING:
    from application.composition_root import DependencyContainer

# Importaciones de dominio
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort

# Importaciones de utilidades
from shared.utils.error_handling import (
    DocumentError, StorageError, LLMError, ValidationError, ErrorContext, ErrorHandler
)

# Definición de tipos genéricos para entrada y salida
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')


class UseCase(Generic[InputT, OutputT], ABC):
    """
    Clase base abstracta para todos los casos de uso.

    Define la estructura común que deben seguir todos los casos de uso,
    siguiendo el principio de inversión de dependencias.
    """

    @abstractmethod
    def execute(self, input_data: InputT) -> OutputT:
        """
        Ejecuta el caso de uso con los datos de entrada especificados.

        Args:
            input_data: Datos de entrada específicos para el caso de uso

        Returns:
            Resultado de la ejecución del caso de uso
        """
        pass


class PDFToMarkdownUseCase(UseCase[Path, Dict[str, Any]]):
    """Caso de uso para la conversión de PDF a Markdown."""

    def __init__(
        self,
        document_port: DocumentPort,
        storage_port: StoragePort,
        llm_port: LLMPort
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            document_port: Puerto para operaciones con documentos
            storage_port: Puerto para almacenamiento
            llm_port: Puerto para refinamiento con LLM
        """
        self.document_port = document_port
        self.storage_port = storage_port
        self.llm_port = llm_port

    def execute(self, pdf_path: Path, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convierte un archivo PDF en un archivo Markdown con manejo mejorado de errores.

        Args:
            pdf_path: Ruta al archivo PDF de entrada
            options: Opciones de procesamiento (refine_with_llm, detect_language, etc.)

        Returns:
            Dict[str, Any]: Resultado del procesamiento con metadata

        Raises:
            DocumentError: Si hay problemas al procesar el PDF
            StorageError: Si hay problemas al guardar el resultado
            LLMError: Si hay problemas con el refinamiento del texto
        """
        if options is None:
            options = {}

        context = ErrorContext(
            operation="pdf_to_markdown_conversion",
            file_path=str(pdf_path),
            user_action="convert_pdf_to_markdown"
        )

        try:
            # Validar que el archivo existe
            if not pdf_path.exists():
                raise DocumentError(
                    f"El archivo PDF no existe: {pdf_path}",
                    context
                )

            # Extraer contenido del PDF
            try:
                raw_markdown = self.document_port.extract_markdown(pdf_path)
                if not raw_markdown or raw_markdown.strip() == "":
                    raise DocumentError(
                        "No se pudo extraer contenido del PDF",
                        context
                    )
            except Exception as e:
                raise ErrorHandler.handle_exception(
                    e,
                    "extracción de contenido PDF"
                )

            # Procesar con LLM si está habilitado
            refined_markdown = raw_markdown
            llm_used = False

            if options.get('refine_with_llm', False):
                try:
                    refined_markdown = self.llm_port.format_markdown(
                        raw_markdown)
                    llm_used = True
                except Exception as e:
                    # Si falla el LLM, continuar con el contenido original
                    # pero registrar el error
                    llm_error = ErrorHandler.handle_exception(
                        e,
                        "refinamiento con LLM"
                    )
                    # En lugar de fallar, continuar con el contenido original
                    refined_markdown = raw_markdown
                    llm_used = False

            # Guardar el resultado
            try:
                md_path = self.storage_port.save_markdown(
                    pdf_path.stem,
                    refined_markdown
                )
            except Exception as e:
                raise ErrorHandler.handle_exception(
                    e,
                    "guardado de archivo Markdown"
                )

            # Retornar resultado con metadata
            return {
                'success': True,
                'output_path': md_path,
                'input_file': str(pdf_path),
                'content_length': len(refined_markdown),
                'llm_used': llm_used,
                'processing_options': options,
                'metadata': {
                    'file_size': pdf_path.stat().st_size if pdf_path.exists() else 0,
                    'created_at': md_path.stat().st_mtime if md_path.exists() else None
                }
            }

        except (DocumentError, StorageError, LLMError):
            # Re-raise application errors as-is
            raise
        except Exception as e:
            # Handle unexpected errors
            raise ErrorHandler.handle_exception(
                e,
                "conversión PDF a Markdown"
            )


class ValidatePDFUseCase(UseCase[Path, Dict[str, Any]]):
    """Caso de uso para validar documentos PDF."""

    def __init__(self, document_port: DocumentPort):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            document_port: Puerto para operaciones con documentos
        """
        self.document_port = document_port

    def execute(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Valida un documento PDF para determinar si puede ser procesado.

        Args:
            pdf_path: Ruta al archivo PDF a validar

        Returns:
            Dict[str, Any]: Resultado detallado de la validación

        Raises:
            ValidationError: Si hay problemas en la validación
            DocumentError: Si hay problemas al acceder al documento
        """
        context = ErrorContext(
            operation="pdf_validation",
            file_path=str(pdf_path),
            user_action="validate_pdf"
        )

        try:
            # Validaciones básicas
            validation_result = {
                'valid': False,
                'file_path': str(pdf_path),
                'file_exists': False,
                'is_pdf': False,
                'readable': False,
                'file_size': 0,
                'total_pages': 0,
                'digital_pages': 0,
                'scanned_pages': 0,
                'can_extract_text': False,
                'needs_ocr': False,
                'issues': [],
                'recommendations': []
            }

            # Verificar que el archivo existe
            if not pdf_path.exists():
                validation_result['issues'].append("El archivo no existe")
                raise ValidationError(
                    f"El archivo PDF no existe: {pdf_path}",
                    context
                )

            validation_result['file_exists'] = True
            validation_result['file_size'] = pdf_path.stat().st_size

            # Verificar que es un archivo PDF
            if not pdf_path.suffix.lower() == '.pdf':
                validation_result['issues'].append(
                    "El archivo no tiene extensión .pdf")
                raise ValidationError(
                    f"El archivo no es un PDF válido: {pdf_path}",
                    context
                )

            validation_result['is_pdf'] = True

            # Verificar que es legible
            try:
                metadata = self.document_port.get_document_metadata(pdf_path)
                validation_result['readable'] = True
                validation_result['total_pages'] = metadata.get(
                    'page_count', 0)
            except Exception as e:
                validation_result['issues'].append(
                    "No se puede leer el archivo PDF")
                raise ValidationError(
                    f"No se puede leer el archivo PDF: {e}",
                    context,
                    e
                )

            # Analizar contenido de las páginas
            try:
                pages_analysis = self.document_port.analyze_pages(pdf_path)

                digital_pages = 0
                scanned_pages = 0

                for page_info in pages_analysis:
                    if page_info.get('has_text', False):
                        digital_pages += 1
                    else:
                        scanned_pages += 1

                validation_result['digital_pages'] = digital_pages
                validation_result['scanned_pages'] = scanned_pages
                validation_result['can_extract_text'] = digital_pages > 0
                validation_result['needs_ocr'] = scanned_pages > 0

            except Exception as e:
                validation_result['issues'].append(
                    "Error al analizar el contenido del PDF")
                # No es un error crítico, continuar con validación parcial

            # Generar recomendaciones
            if validation_result['scanned_pages'] > 0:
                validation_result['recommendations'].append(
                    "Este documento contiene páginas escaneadas que requerirán OCR"
                )

            if validation_result['digital_pages'] > 0:
                validation_result['recommendations'].append(
                    "Este documento tiene texto digital que se puede extraer directamente"
                )

            if validation_result['file_size'] > 50 * 1024 * 1024:  # 50MB
                validation_result['recommendations'].append(
                    "Archivo grande: el procesamiento puede tomar más tiempo"
                )

            if validation_result['total_pages'] > 100:
                validation_result['recommendations'].append(
                    "Documento extenso: considere procesamiento por lotes"
                )

            # Determinar si es válido para procesamiento
            validation_result['valid'] = (
                validation_result['file_exists'] and
                validation_result['is_pdf'] and
                validation_result['readable'] and
                validation_result['total_pages'] > 0 and
                len(validation_result['issues']) == 0
            )

            return validation_result

        except (ValidationError, DocumentError):
            # Re-raise application errors as-is
            raise
        except Exception as e:
            # Handle unexpected errors
            raise ErrorHandler.handle_exception(
                e,
                "validación de PDF"
            )


class UseCaseFactory:
    """
    Factoría para crear instancias de casos de uso.

    Esta clase facilita la creación de casos de uso con sus dependencias
    correctamente configuradas, siguiendo el patrón Factory.
    """

    def __init__(self, container: 'DependencyContainer'):
        """
        Inicializa la factoría con un contenedor de dependencias.

        Args:
            container: Contenedor con las dependencias necesarias
        """
        self._container = container

    def create_pdf_to_markdown_use_case(self) -> PDFToMarkdownUseCase:
        """
        Crea una instancia del caso de uso para convertir PDF a Markdown.

        Returns:
            Instancia configurada del caso de uso
        """
        return PDFToMarkdownUseCase(
            document_port=self._container.get_document_port(),
            storage_port=self._container.get_storage_port(),
            llm_port=self._container.get_llm_port()
        )

    def create_validate_pdf_use_case(self) -> ValidatePDFUseCase:
        """
        Crea una instancia del caso de uso para validar PDFs.

        Returns:
            Instancia configurada del caso de uso
        """
        return ValidatePDFUseCase(
            document_port=self._container.get_document_port()
        )

    def process_pdf_complete(self, pdf_path: Path, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo de procesamiento de un PDF.

        Este método orquesta la ejecución de múltiples casos de uso para
        realizar un procesamiento completo de un documento PDF.

        Args:
            pdf_path: Ruta al PDF a procesar
            options: Opciones de procesamiento

        Returns:
            Resultado del procesamiento
        """
        # Crear opciones predeterminadas si no se proporcionan
        if options is None:
            options = {}

        # Validar el PDF primero
        validate_use_case = self.create_validate_pdf_use_case()
        validation_result = validate_use_case.execute(pdf_path)

        # Si la validación es exitosa, convertir a Markdown
        if validation_result['is_valid']:
            convert_use_case = self.create_pdf_to_markdown_use_case()
            result = convert_use_case.execute(pdf_path, options)
            result.update({'validation': validation_result})
            return result

        # Si no es válido, devolver solo el resultado de validación
        return {
            'success': False,
            'validation': validation_result,
            'error': validation_result.get('error_message', 'Documento no válido')
        }
