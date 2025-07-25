"""Base module for mappers."""
from .entity_mappers import (
    DocumentMapper,
    PageMapper,
    TextBlockMapper,
    TableMapper,
    CoordinatesMapper,
)

__all__ = [
    'DocumentMapper',
    'PageMapper',
    'TextBlockMapper',
    'TableMapper',
    'CoordinatesMapper',
]
