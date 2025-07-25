"""LLM refinement related DTOs."""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class LLMConfigDTO:
    """DTO for LLM configuration options."""
    
    model: str = 'gpt-3.5-turbo'
    temperature: float = 0.3
    max_tokens: int = 500
    context_window: int = 2000
    retry_attempts: int = 3
    timeout: int = 30

@dataclass
class LLMRefineRequestDTO:
    """DTO for LLM refinement request."""
    
    original_text: str
    context: Optional[str] = None
    instructions: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

@dataclass
class LLMRefineResultDTO:
    """DTO for LLM refinement results."""
    
    refined_text: str
    confidence_score: float
    changes_made: List[Dict[str, str]]
    processing_time: float
    tokens_used: int
    error: Optional[str] = None
