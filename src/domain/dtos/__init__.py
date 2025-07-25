"""Base module for DTOs."""
from .coordinates_dto import CoordinatesDTO
from .content_dtos import (
    TextBlockDTO,
    TableDTO,
    PageContentDTO,
)
from .document_dtos import (
    DocumentInputDTO,
    DocumentOutputDTO,
    DocumentMetadataDTO,
)
from .ocr_dtos import (
    OCRConfigDTO,
    OCRResultDTO,
)
from .llm_dtos import (
    LLMConfigDTO,
    LLMRefineRequestDTO,
    LLMRefineResultDTO,
)

__all__ = [
    'CoordinatesDTO',
    'TextBlockDTO',
    'TableDTO',
    'PageContentDTO',
    'DocumentInputDTO',
    'DocumentOutputDTO',
    'DocumentMetadataDTO',
    'OCRConfigDTO',
    'OCRResultDTO',
    'LLMConfigDTO',
    'LLMRefineRequestDTO',
    'LLMRefineResultDTO',
]
