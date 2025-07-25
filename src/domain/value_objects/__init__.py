"""Base value objects module."""
from .document_metadata import DocumentMetadata
from .page import Page
from .table import Table
from .text_block import TextBlock
from .text_coordinates import TextCoordinates

__all__ = [
    'DocumentMetadata',
    'Page',
    'Table',
    'TextBlock',
    'TextCoordinates',
]
