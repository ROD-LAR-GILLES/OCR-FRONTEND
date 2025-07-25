"""DTOs for document-related data transfer between layers."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class DocumentInputDTO:
    """DTO for incoming document data from the presentation layer."""
    
    file_path: str
    process_tables: bool = False
    detect_language: bool = False
    spell_check: bool = False
    refine_with_llm: bool = False

@dataclass
class DocumentOutputDTO:
    """DTO for outgoing document data to the presentation layer."""
    
    id: str
    file_path: str
    total_pages: int
    processed_successfully: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    creation_date: Optional[datetime] = None
    author: Optional[str] = None

@dataclass
class DocumentMetadataDTO:
    """DTO for document metadata."""
    
    title: Optional[str]
    author: Optional[str]
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    producer: Optional[str]
    page_count: int
