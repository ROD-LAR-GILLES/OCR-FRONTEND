"""
Caso de uso para validar documentos PDF.

Este módulo implementa la lógica para validar si un documento PDF
puede ser procesado correctamente por el sistema OCR.
"""
from pathlib import Path
from typing import Dict, Any
from domain.ports.document_port import DocumentPort
from domain.exceptions import DocumentError


class ValidatePDFUseCase:
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
            pdf_path: Ruta al archivo PDF a validar.

        Returns:
            Dict con información sobre la validación:
            {
                "valid": bool,
                "total_pages": int,
                "scanned_pages": int,
                "digital_pages": int,
                "message": str,
                "metadata": Dict
            }

        Raises:
            DocumentError: Si hay problemas al acceder al documento
        """
        try:
            # Obtener información básica del documento
            doc_info = self.document_port.get_document_info(pdf_path)

            # Analizar páginas para detectar contenido escaneado vs digital
            total_pages = doc_info.get("total_pages", 0)
            scanned_pages = 0
            digital_pages = 0

            for page_num in range(1, total_pages + 1):
                page_info = self.document_port.get_page_info(
                    pdf_path, page_num)
                if page_info.get("is_scanned", False):
                    scanned_pages += 1
                else:
                    digital_pages += 1

            # Determinar si el documento es válido para procesamiento
            valid = total_pages > 0
            message = "Documento válido para procesamiento."

            if scanned_pages > 0:
                message += f" Contiene {scanned_pages} página(s) escaneada(s) que requieren OCR."

            return {
                "valid": valid,
                "total_pages": total_pages,
                "scanned_pages": scanned_pages,
                "digital_pages": digital_pages,
                "message": message,
                "metadata": doc_info.get("metadata", {})
            }

        except Exception as e:
            raise DocumentError(f"Error al validar documento PDF: {str(e)}")
