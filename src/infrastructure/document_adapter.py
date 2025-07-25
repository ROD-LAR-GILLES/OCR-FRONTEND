"""
Adaptador concreto para el procesamiento de documentos PDF.
Implementa DocumentPort usando PyMuPDF para operaciones básicas de documentos.
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any
import fitz
from domain.ports.document_port import DocumentPort
from infrastructure.logging_setup import logger


class DocumentAdapter(DocumentPort):
    """Implementación concreta del puerto de documentos usando PyMuPDF."""

    def extract_markdown(self, pdf_path: Path) -> str:
        """
        Extrae contenido de un PDF y lo convierte a Markdown.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            str: Contenido del PDF en formato Markdown
        """
        # Por ahora, delegamos a la implementación existente
        from adapters.document_processing import extract_markdown
        return extract_markdown(pdf_path)

    def extract_pages(self, pdf_path: Path) -> List[str]:
        """
        Extrae el contenido de todas las páginas de un PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[str]: Lista de contenido por página
        """
        try:
            doc = fitz.open(pdf_path)
            pages_content = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_content.append(text.strip())

            doc.close()
            return pages_content

        except Exception as e:
            logger.error(f"Error extrayendo páginas de {pdf_path}: {e}")
            raise

    def extract_tables(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extrae todas las tablas encontradas en el PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            List[Tuple[int, str]]: Lista de (número_página, tabla_markdown)
        """
        try:
            doc = fitz.open(pdf_path)
            tables = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                # Usar la función existente de extracción de tablas
                from adapters.document_processing import extract_tables_from_page
                page_tables = extract_tables_from_page(page)

                for table in page_tables:
                    tables.append((page_num + 1, table))

            doc.close()
            return tables

        except Exception as e:
            logger.error(f"Error extrayendo tablas de {pdf_path}: {e}")
            return []

    def get_document_info(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Obtiene información básica del documento PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con información del documento
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata

            info = {
                "total_pages": len(doc),
                "metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "creationDate": metadata.get("creationDate", ""),
                    "modDate": metadata.get("modDate", "")
                }
            }

            doc.close()
            return info

        except Exception as e:
            logger.error(f"Error obteniendo información de {pdf_path}: {e}")
            raise

    def get_page_info(self, pdf_path: Path, page_num: int) -> Dict[str, Any]:
        """
        Obtiene información específica de una página.

        Args:
            pdf_path: Ruta al archivo PDF
            page_num: Número de página (1-indexado)

        Returns:
            Dict con información de la página
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num - 1]  # fitz usa 0-indexado

            # Obtener texto seleccionable
            text = page.get_text().strip()

            # Determinar si la página está escaneada
            # Si no hay texto seleccionable, probablemente está escaneada
            is_scanned = len(text) < 50  # Umbral arbitrario

            # Obtener dimensiones de la página
            rect = page.rect

            info = {
                "page_number": page_num,
                "is_scanned": is_scanned,
                "has_text": len(text) > 0,
                "text_length": len(text),
                "width": rect.width,
                "height": rect.height,
                "rotation": page.rotation
            }

            doc.close()
            return info

        except Exception as e:
            logger.error(
                f"Error obteniendo información de página {page_num} en {pdf_path}: {e}")
            raise

    def analyze_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Analiza todas las páginas de un documento PDF y proporciona información detallada.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Lista de diccionarios con información de cada página
        """
        try:
            doc = fitz.open(pdf_path)
            results = []

            for page_num in range(len(doc)):
                # Las páginas son 0-indexadas en PyMuPDF pero 1-indexadas en nuestra API
                page_info = self.get_page_info(pdf_path, page_num + 1)
                results.append(page_info)

            doc.close()
            return results

        except Exception as e:
            logger.error(f"Error analizando páginas de {pdf_path}: {e}")
            raise

    def get_document_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Obtiene metadata del documento PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con metadata del documento
        """
        info = self.get_document_info(pdf_path)
        return {
            'page_count': info['total_pages'],
            'metadata': info['metadata']
        }
