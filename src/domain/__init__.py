"""
Dominio de la aplicación OCR.

Este módulo contiene las entidades, objetos de valor, puertos y casos de uso que
conforman el núcleo de la aplicación OCR. El dominio sigue los principios de
Arquitectura Hexagonal (Ports & Adapters) para mantener la independencia de
infraestructura y tecnologías específicas.

Organización:
- entities: Entidades del dominio (Document)
- value_objects: Objetos de valor inmutables (Page, TextBlock, etc.)
- ports: Interfaces para adaptar tecnologías externas
- use_cases: Implementación de la lógica de negocio
- dtos: Objetos de transferencia de datos
- mappers: Conversión entre entidades y DTOs
- exceptions: Excepciones específicas del dominio
"""

# Entidades
from .entities.document import Document

# Objetos de valor
from .value_objects.document_metadata import DocumentMetadata
from .value_objects.page import Page
from .value_objects.table import Table
from .value_objects.text_block import TextBlock
from .value_objects.text_coordinates import TextCoordinates

# DTOs
from .dtos import (
    CoordinatesDTO,
    TextBlockDTO, TableDTO, PageContentDTO,
    DocumentInputDTO, DocumentOutputDTO, DocumentMetadataDTO,
    OCRConfigDTO, OCRResultDTO,
    LLMConfigDTO, LLMRefineRequestDTO, LLMRefineResultDTO,
)

# Puertos
from .ports.document_port import DocumentPort
from .ports.ocr_port import OCRPort
from .ports.llm_port import LLMPort
from .ports.storage_port import StoragePort
from .ports.llm_provider import LLMProvider

# Casos de uso
from .use_cases.pdf_to_markdown import PDFToMarkdownUseCase
from .use_cases.validate_pdf import ValidatePDFUseCase

# Excepciones
from .exceptions import DocumentError, StorageError, LLMError

# Mappers
from .mappers.entity_mappers import DocumentMapper, PageMapper

__all__ = [
    # Entidades
    'Document',

    # Objetos de valor
    'DocumentMetadata', 'Page', 'Table', 'TextBlock', 'TextCoordinates',

    # DTOs
    'CoordinatesDTO', 'TextBlockDTO', 'TableDTO', 'PageContentDTO',
    'DocumentInputDTO', 'DocumentOutputDTO', 'DocumentMetadataDTO',
    'OCRConfigDTO', 'OCRResultDTO',
    'LLMConfigDTO', 'LLMRefineRequestDTO', 'LLMRefineResultDTO',

    # Puertos
    'DocumentPort', 'OCRPort', 'LLMPort', 'StoragePort', 'LLMProvider',

    # Casos de uso
    'PDFToMarkdownUseCase',
    'ValidatePDFUseCase',

    # Excepciones
    'DocumentError', 'StorageError', 'LLMError',    # Mappers
    'DocumentMapper', 'PageMapper',
]
