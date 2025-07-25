"""DTOs for content-related data transfer between layers."""
from dataclasses import dataclass
from typing import List, Optional
from .coordinates_dto import CoordinatesDTO

@dataclass
class TextBlockDTO:
    """DTO for text block data."""
    
    content: str
    coordinates: CoordinatesDTO
    confidence_score: Optional[float] = None
    language: Optional[str] = None
    spelling_corrections: List[str] = None
    refined_content: Optional[str] = None

@dataclass
class TableDTO:
    """DTO for table data."""
    
    data: List[List[str]]
    coordinates: CoordinatesDTO
    confidence_score: Optional[float] = None
    headers: Optional[List[str]] = None
    table_type: Optional[str] = None

@dataclass
class PageContentDTO:
    """DTO for page content data."""
    
    page_number: int
    text_blocks: List[TextBlockDTO]
    tables: List[TableDTO]
    rotation: int = 0
    is_scanned: bool = False
    confidence_score: Optional[float] = None
