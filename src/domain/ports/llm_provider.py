from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """Base interface for LLM providers."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the client with provided configuration.
        
        Args:
            config: Dictionary containing provider-specific configuration
        """
        pass
    
    @abstractmethod
    def generate_completion(self, 
                          prompt: str,
                          system_prompt: str = None,
                          temperature: float = 0.1) -> str:
        """Generate a completion using the configured model.
        
        Args:
            prompt: The text to process
            system_prompt: Optional system instructions
            temperature: Controls randomness in the output
            
        Returns:
            The generated text completion
        """
        pass
