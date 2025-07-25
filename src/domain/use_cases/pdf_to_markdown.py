"""
Caso de uso para convertir archivos PDF a formato Markdown.

Este módulo implementa la lógica de negocio para convertir documentos PDF a formato Markdown,
utilizando OCR cuando es necesario y refinando el texto con LLM.
"""
from pathlib import Path
from typing import Protocol
from domain.ports.document_port import DocumentPort
from domain.ports.storage_port import StoragePort
from domain.ports.llm_port import LLMPort

class PDFToMarkdownUseCase:
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

    def execute(self, pdf_path: Path) -> Path:
        """
        Convierte un archivo PDF en un archivo Markdown, utilizando extracción inteligente
        y refinamiento con LLM.

        Args:
            pdf_path: Ruta al archivo PDF de entrada.

        Returns:
            Path: Ruta al archivo Markdown generado.
            
        Raises:
            DocumentError: Si hay problemas al procesar el PDF
            StorageError: Si hay problemas al guardar el resultado
            LLMError: Si hay problemas con el refinamiento del texto
        """
        # Extraer contenido del PDF
        raw_markdown = self.document_port.extract_markdown(pdf_path)
        
        # Refinar el contenido con LLM
        refined_markdown = self.llm_port.format_markdown(raw_markdown)
        
        # Guardar el resultado
        md_path = self.storage_port.save_markdown(pdf_path.stem, refined_markdown)
        return md_path
