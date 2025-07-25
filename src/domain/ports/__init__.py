"""
Puertos que definen las interfaces para la arquitectura hexagonal.
Cada puerto define un contrato que los adaptadores deben implementar.
"""

from .document_port import DocumentPort
from .llm_port import LLMPort
from .llm_provider import LLMProvider
from .ocr_port import OCRPort
from .storage_port import StoragePort

__all__ = [
    'DocumentPort',
    'LLMPort',
    'LLMProvider',
    'OCRPort',
    'StoragePort',
]
