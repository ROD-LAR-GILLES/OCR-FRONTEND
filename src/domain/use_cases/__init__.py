"""
Casos de uso del dominio.

Este paquete contiene todos los casos de uso de la aplicación, cada uno en su propio archivo.
Sigue los principios de Clean Architecture, donde cada caso de uso representa una operación de negocio.
"""

from .pdf_to_markdown import PDFToMarkdownUseCase

__all__ = ['PDFToMarkdownUseCase']
