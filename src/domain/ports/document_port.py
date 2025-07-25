"""
Puerto para el procesamiento de documentos PDF.
Define la interfaz que deben implementar los adaptadores de documentos.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Dict, Any


class DocumentPort(ABC):
    """Interfaz abstracta para procesamiento de documentos PDF."""

    @abstractmethod
    def extract_markdown(self, pdf_path: Path) -> str:
        """
        Extrae contenido de un PDF y lo convierte a Markdown.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            str: Contenido en formato Markdown
        """
        pass

    @abstractmethod
    def extract_pages(self, pdf_path: Path) -> List[str]:
        """
        Extrae el contenido de todas las páginas de un PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[str]: Lista de contenido por página
        """
        pass

    @abstractmethod
    def extract_tables(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extrae todas las tablas encontradas en el PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[Tuple[int, str]]: Lista de (número_página, tabla_markdown)
        """
        pass

    @abstractmethod
    def get_document_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Obtiene metadata del documento PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con metadata del documento:
            {
                "page_count": int,
                "metadata": Dict
            }
        """
        pass

    @abstractmethod
    def analyze_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Analiza todas las páginas de un documento PDF y proporciona información detallada.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Lista de diccionarios con información de cada página
        """
        pass
        """
        Extrae todas las tablas encontradas en el PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[Tuple[int, str]]: Lista de (número_página, tabla_markdown)
        """
        pass

    @abstractmethod
    def get_document_info(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Obtiene información básica del documento PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con información del documento:
            {
                "total_pages": int,
                "metadata": Dict
            }
        """
        pass

    @abstractmethod
    def get_page_info(self, pdf_path: Path, page_num: int) -> Dict[str, Any]:
        """
        Obtiene información específica de una página.

        Args:
            pdf_path: Ruta al archivo PDF
            page_num: Número de página (1-indexado)

        Returns:
            Dict con información de la página:
            {
                "page_number": int,
                "is_scanned": bool,
                "has_text": bool,
                "text_length": int
            }
        """
        pass
