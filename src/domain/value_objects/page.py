"""Value object representing a page in a document."""
from dataclasses import dataclass
from typing import List, Optional
from .text_block import TextBlock
from .table import Table

@dataclass(frozen=True)
class Page:
    """Value object that represents a page with its content."""
    
    number: int
    text_blocks: List[TextBlock]
    tables: List[Table]
    rotation: int = 0
    has_scanned_content: bool = False
    confidence_score: Optional[float] = None

    @property
    def is_empty(self) -> bool:
        """Check if the page has no content."""
        return len(self.text_blocks) == 0 and len(self.tables) == 0

    @property
    def total_text_blocks(self) -> int:
        """Get the total number of text blocks in the page."""
        return len(self.text_blocks)

    @property
    def total_tables(self) -> int:
        """Get the total number of tables in the page."""
        return len(self.tables)
