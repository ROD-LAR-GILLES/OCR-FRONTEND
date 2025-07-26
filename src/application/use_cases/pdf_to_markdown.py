"""
Caso de uso mejorado para convertir archivos PDF a formato Markdown.

Este módulo implementa la lógica de negocio mejorada para convertir documentos PDF
a formato Markdown, con manejo de errores centralizado y mejor separación de responsabilidades.
"""
from pathlib import Path
from typing import Dict, Any

from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort
from shared.utils.error_handling import (
    DocumentError, StorageError, LLMError, ErrorContext, ErrorHandler
)


class PDFToMarkdownUseCase:
    """Caso de uso mejorado para la conversión de PDF a Markdown."""

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
