import google.generativeai as genai
from typing import Dict, Any
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

class GeminiProvider(LLMProvider):
    """Google's Gemini implementation of LLM provider."""

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Gemini client with configuration.
        
        Args:
            config: Dictionary with Gemini-specific settings
        """
        genai.configure(api_key=config["api_key"])
        self.model = genai.GenerativeModel(
            model_name=config.get("model_id", "gemini-pro")
        )
        self.max_retries = config.get("max_retries", 5)
        
    def generate_completion(self, 
                          prompt: str,
                          system_prompt: str = None,
                          temperature: float = 0.1) -> str:
        """Generate completion using Gemini's chat model.
        
        Args:
            prompt: The text to process
            system_prompt: Optional system context
            temperature: Controls response creativity
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails
        """
        try:
            chat = self.model.start_chat(
                context=system_prompt if system_prompt else ""
            )
            response = chat.send_message(prompt, temperature=temperature)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
