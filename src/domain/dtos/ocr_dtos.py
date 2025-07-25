"""DTOs for OCR processing configuration and results."""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class OCRConfigDTO:
    """DTO for OCR configuration options."""
    
    language: str = 'spa'
    psm: int = 3  # Page segmentation mode
    oem: int = 3  # OCR Engine mode
    dpi: int = 300
    preprocessing_options: Dict[str, bool] = None
    timeout: Optional[int] = None

@dataclass
class OCRResultDTO:
    """DTO for OCR processing results."""
    
    text: str
    confidence: float
    word_confidences: List[float]
    processing_time: float
    language_detected: Optional[str] = None
    error: Optional[str] = None
