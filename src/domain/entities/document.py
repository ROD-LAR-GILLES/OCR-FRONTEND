"""Document entity representing a PDF document in the system."""
from dataclasses import dataclass
from typing import List, Optional
from ..value_objects.page import Page
from ..value_objects.document_metadata import DocumentMetadata

@dataclass
class Document:
    """Document entity that represents a PDF document with its pages and metadata."""
    
    id: str
    path: str
    pages: List[Page]
    metadata: DocumentMetadata
    processed: bool = False
    error: Optional[str] = None

    def add_page(self, page: Page) -> None:
        """Add a new page to the document."""
        self.pages.append(page)

    def mark_as_processed(self) -> None:
        """Mark the document as processed."""
        self.processed = True

    def set_error(self, error_message: str) -> None:
        """Set an error message for the document."""
        self.error = error_message
        self.processed = False

    @property
    def total_pages(self) -> int:
        """Get the total number of pages in the document."""
        return len(self.pages)

    @property
    def has_error(self) -> bool:
        """Check if the document has any errors."""
        return self.error is not None
