"""DTO for coordinates data transfer between layers."""
from dataclasses import dataclass

@dataclass
class CoordinatesDTO:
    """DTO for coordinate data."""
    
    x1: float
    y1: float
    x2: float
    y2: float
    page_number: int
    
    @property
    def width(self) -> float:
        """Calculate width of the area."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """Calculate height of the area."""
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        """Calculate total area."""
        return self.width * self.height
