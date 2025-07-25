# ─── src/adapters/llm_refiner.py ───
import re
from typing import List, Dict, Any
import time
from domain.ports.llm_provider import LLMProvider
from config.api_settings import load_api_settings
from infrastructure.logging_setup import logger

OCR_PATTERNS = {
    r"[0Oo]": "O",
    r"[1Il]": "l",
    r"[5Ss]": "S",
    r"[8Bb]": "B",
    r"[2Zz]": "Z",
}

def _correct_ocr_errors(text: str) -> str:
    for pattern, replacement in OCR_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text

def _detect_document_structure(text: str) -> Dict[str, List[str]]:
    structure = {"headers": [], "sections": [], "lists": [], "tables": []}
    structure["headers"]  = re.findall(r"^[A-ZÁÉÍÓÚÑ\s]{10,}$", text, re.MULTILINE)
    structure["sections"] = re.findall(r"^\d+\.\s+[A-ZÁÉÍÓÚÑ][^.]+", text, re.MULTILINE)
    structure["lists"]    = re.findall(r"^[\-\*•]\s+.+$",           text, re.MULTILINE)
    return structure


class LLMRefiner:
    """Refines OCR text using configurable LLM providers."""

    def __init__(self, provider: LLMProvider = None) -> None:
        try:
            self.api_config = load_api_settings()
            
            if provider is None:
                from adapters.providers.openai_provider import OpenAIProvider
                provider = OpenAIProvider()
            
            self.provider = provider
            self.provider.initialize(self.api_config["openai"])
        except Exception as e:
            logger.error(f"Error initializing LLM provider: {e}")
            self.provider = None
            
    def _safe_generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Safe wrapper for LLM completion generation.
        
        Args:
            prompt: Text to process
            system_prompt: Optional system instructions
            
        Returns:
            Generated completion or original text on error
        """
        try:
            return self.provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return prompt

    # ───────────────────── Fine-tuned model ─────────────────────
    def refine_markdown(self, raw_text: str) -> str:
        """Refine OCR text using configured LLM provider."""
        if not self.provider:
            logger.warning("LLM provider not available → returning raw text")
            return raw_text

        system_prompt = ("You are a Markdown formatter for Spanish legal OCR text. "
                        "Convert the user content into well-structured Markdown.")
        
        return self._safe_generate(raw_text, system_prompt) or raw_text

    # ───────────────────── Prompt-based pipeline ─────────────────────
    def prompt_refine(self, raw: str) -> str:
        """Prompt-based refinement pipeline."""
        if not self.provider:
            logger.warning("LLM provider not available → returning raw text")
            return raw

        try:
            cleaned = _correct_ocr_errors(raw)
            structure = _detect_document_structure(cleaned)

            # Initial document analysis
            analysis_prompt = ("You are a legal document analysis expert. "
                           "Analyze the text and return its structure, references, and OCR errors.")
            analysis = self._safe_generate(cleaned, analysis_prompt)

            # Final refinement with context
            system_prompt = (
                "You are an advanced legal document and OCR processing expert.\n"
                f"- Headers detected: {len(structure['headers'])}\n"
                f"- Numbered sections: {len(structure['sections'])}\n"
                f"- List items: {len(structure['lists'])}\n\n"
                f"Previous analysis:\n{analysis}"
            )
            
            return self._safe_generate(cleaned, system_prompt) or raw

        except Exception as e:
            logger.exception(f"Error in refinement pipeline: {e}")
            return raw