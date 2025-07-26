"""
Caso de uso mejorado para validar documentos PDF.

Este módulo implementa la lógica mejorada para validar si un documento PDF
puede ser procesado correctamente por el sistema OCR.
"""
from pathlib import Path
from typing import Dict, Any

from domain.ports.document_port import DocumentPort
from shared.utils.error_handling import (
    DocumentError, ValidationError, ErrorContext, ErrorHandler
)


class ValidatePDFUseCase:
    """Caso de uso mejorado para validar documentos PDF."""

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
