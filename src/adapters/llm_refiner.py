# ─── src/adapters/llm_refiner.py ───
"""
Módulo para el refinamiento de texto usando LLM.
"""

import re
import time
from typing import Any, Dict, List

import config.state as state
from adapters.providers.llm_factory import LLMProviderFactory
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

# Patrones comunes de corrección OCR
OCR_PATTERNS = {
    r"[0Oo]": "O",
    r"[1Il]": "l",
    r"[5Ss]": "S",
    r"[8Bb]": "B",
    r"[2Zz]": "Z",
}


def _correct_ocr_errors(text: str) -> str:
    """Corrige errores comunes de OCR usando patrones de sustitución."""
    for pattern, replacement in OCR_PATTERNS.items():
        text = re.sub(pattern, replacement, text)
    return text


def _detect_document_structure(text: str) -> Dict[str, List[str]]:
    """Detecta elementos estructurales en el documento para análisis."""
    structure = {"headers": [], "sections": [], "lists": [], "tables": []}
    structure["headers"] = re.findall(
        r"^[A-ZÁÉÍÓÚÑ\s]{10,}$", text, re.MULTILINE)
    structure["sections"] = re.findall(
        r"^\d+\.\s+[A-ZÁÉÍÓÚÑ][^.]+", text, re.MULTILINE)
    structure["lists"] = re.findall(
        r"^[\-\*•]\s+.+$",           text, re.MULTILINE)
    return structure


class LLMRefiner:
    """Refina texto OCR usando proveedores LLM configurables."""

    def __init__(self, provider_type: str = None) -> None:
        """
        Inicializa el refinador con un proveedor LLM.

        Args:
            provider_type: Tipo de proveedor a usar ('openai', 'gemini', o None para automático)
        """
        # Determinar el tipo de proveedor automáticamente basado en la configuración
        if provider_type is None:
            provider_type = state.LLM_PROVIDER if hasattr(
                state, 'LLM_PROVIDER') else None

        # Crear el proveedor usando la fábrica
        self.provider = LLMProviderFactory.create_provider(provider_type)

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
        """
        Refinamiento basado en prompts: aplica correcciones y mejoras al texto OCR.

        Proceso:
        1. Corrige errores OCR comunes
        2. Detecta estructura del documento
        3. Usa el LLM para refinar el texto

        Args:
            raw: Texto OCR original

        Returns:
            Texto refinado o el original si falla el proceso
        """
        if not self.provider:
            logger.warning(
                "Proveedor LLM no disponible → devolviendo texto original")
            return raw

        try:
            # 1. Corregir errores básicos de OCR
            cleaned = _correct_ocr_errors(raw)

            # 2. Detectar estructura del documento
            structure = _detect_document_structure(cleaned)

            # 3. Prompt unificado para refinamiento
            system_prompt = (
                "Eres un experto en documentos legales y procesamiento de OCR. "
                "Tu tarea es mejorar el texto OCR corrigiendo errores y mejorando el formato. "
                f"- Encabezados detectados: {len(structure['headers'])}\n"
                f"- Secciones numeradas: {len(structure['sections'])}\n"
                f"- Elementos de lista: {len(structure['lists'])}\n\n"
                "Mantén todas las referencias legales, números y términos técnicos exactos. "
                "Preserva el formato Markdown existente."
            )

            # 4. Generar refinamiento
            return self._safe_generate(cleaned, system_prompt) or raw

        except Exception as e:
            logger.error(f"Error en refinamiento: {e}")
            return raw

        except Exception as e:
            logger.exception(f"Error in refinement pipeline: {e}")
            return raw
