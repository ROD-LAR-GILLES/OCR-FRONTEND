"""Document metadata value object representing metadata of a document."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class DocumentMetadata:
    """Value object that represents metadata of a document."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    producer: Optional[str] = None
    page_count: int = 0

    @property
    def has_title(self) -> bool:
        """Check if the document has a title."""
        return self.title is not None and len(self.title.strip()) > 0

    @property
    def has_author(self) -> bool:
        """Check if the document has an author."""
        return self.author is not None and len(self.author.strip()) > 0
