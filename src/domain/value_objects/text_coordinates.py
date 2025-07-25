"""Text coordinates value object representing position and dimensions of text or table."""
from dataclasses import dataclass

@dataclass(frozen=True)
class TextCoordinates:
    """Value object that represents the position and dimensions of text or table elements."""
    
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        """Get the width of the text area."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Get the height of the text area."""
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        """Get the area of the text region."""
        return self.width * self.height
