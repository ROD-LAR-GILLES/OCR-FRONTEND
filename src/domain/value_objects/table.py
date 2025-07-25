"""Table value object representing a table in a page."""
from dataclasses import dataclass
from typing import List, Optional
from .text_coordinates import TextCoordinates

@dataclass(frozen=True)
class Table:
    """Value object that represents a table with its data and position."""
    
    data: List[List[str]]
    coordinates: TextCoordinates
    confidence_score: Optional[float] = None

    @property
    def row_count(self) -> int:
        """Get the number of rows in the table."""
        return len(self.data)

    @property
    def column_count(self) -> int:
        """Get the number of columns in the table."""
        return len(self.data[0]) if self.data else 0

    @property
    def is_empty(self) -> bool:
        """Check if the table has no data."""
        return len(self.data) == 0 or all(len(row) == 0 for row in self.data)
