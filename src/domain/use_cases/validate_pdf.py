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

            # Verificaciones de validación
            validations = {
                "exists": pdf_path.exists(),
                "is_file": pdf_path.is_file(),
                "has_size": pdf_path.stat().st_size > 0 if pdf_path.exists() else False,
                "has_pages": total_pages > 0,
                "not_encrypted": not doc_info.get("encrypted", False),
                "valid_format": doc_info.get("format", "").lower() == "pdf"
            }

            # Construir mensaje detallado
            messages = []
            valid = True

            if not validations["exists"]:
                valid = False
                messages.append("El archivo no existe")
            elif not validations["is_file"]:
                valid = False
                messages.append("La ruta no corresponde a un archivo")
            elif not validations["has_size"]:
                valid = False
                messages.append("El archivo está vacío")
            elif not validations["has_pages"]:
                valid = False
                messages.append("El PDF no contiene páginas")
            elif not validations["not_encrypted"]:
                valid = False
                messages.append("El PDF está encriptado")
            elif not validations["valid_format"]:
                valid = False
                messages.append("El archivo no es un PDF válido")

            if valid:
                messages.append("Documento válido para procesamiento")
                if scanned_pages > 0:
                    messages.append(
                        f"Contiene {scanned_pages} página(s) escaneada(s) que requieren OCR")
                if digital_pages > 0:
                    messages.append(
                        f"Contiene {digital_pages} página(s) con texto digital")

            # Agregar información detallada sobre el documento
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024) if pdf_path.exists() else 0

            return {
                "valid": valid,
                "total_pages": total_pages,
                "scanned_pages": scanned_pages,
                "digital_pages": digital_pages,
                "message": ". ".join(messages),
                "metadata": doc_info.get("metadata", {}),
                "validations": validations,
                "file_size_mb": round(file_size_mb, 2),
                "validation_details": {
                    "min_text_length_per_page": doc_info.get("min_text_length_per_page", 0),
                    "has_images": doc_info.get("has_images", False),
                    "has_text_layers": doc_info.get("has_text_layers", False),
                    "created_date": doc_info.get("created_date", None),
                    "modified_date": doc_info.get("modified_date", None),
                    "producer": doc_info.get("producer", None)
                }
            }

        except Exception as e:
            raise DocumentError(f"Error al validar documento PDF: {str(e)}")
