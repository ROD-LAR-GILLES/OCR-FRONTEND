"""Text block value object representing a block of text in a page."""
from dataclasses import dataclass
from typing import Optional
from .text_coordinates import TextCoordinates

@dataclass(frozen=True)
class TextBlock:
    """Value object that represents a block of text with its position and content."""
    
    content: str
    coordinates: TextCoordinates
    confidence_score: Optional[float] = None
    language: Optional[str] = None

    @property
    def is_empty(self) -> bool:
        """Check if the text block is empty."""
        return len(self.content.strip()) == 0

    @property
    def word_count(self) -> int:
        """Get the number of words in the text block."""
        return len(self.content.split())
