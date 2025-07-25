from typing import Dict, Any
import time
from openai import OpenAI, APIError, RateLimitError
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider."""

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize OpenAI client with configuration.
        
        Args:
            config: Dictionary with OpenAI-specific settings
        """
        self.client = OpenAI(
            api_key=config["api_key"],
            organization=config.get("org_id")
        )
        self.model = config.get("model_id", "gpt-3.5-turbo")
        self.max_retries = config.get("max_retries", 5)

    def generate_completion(self, 
                          prompt: str,
                          system_prompt: str = None,
                          temperature: float = 0.1) -> str:
        """Generate completion using OpenAI's chat completion API.
        
        Args:
            prompt: The text to process
            system_prompt: Optional system instructions
            temperature: Controls response randomness
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails after max retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            except RateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt
                logger.warning(f"Rate limit reached, retrying in {wait}s")
                time.sleep(wait)
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                raise
