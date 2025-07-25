"""
Servicios de procesamiento con Modelos de Lenguaje (LLM).

Este módulo proporciona adaptadores para trabajar con modelos de lenguaje
para tareas como refinamiento de texto, corrección de errores OCR,
y otras operaciones avanzadas de procesamiento de texto.
"""

import re
import time
from typing import Any, Dict, List, Optional

# Importaciones internas
from shared.util.config import AppConfig
from adapters.providers.llm_factory import LLMProviderFactory
from domain.ports.llm_provider import LLMProvider
from infrastructure.logging_setup import logger

# Instancia de configuración
app_config = AppConfig()

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


class LLMRefiner:
    """
    Clase para refinar texto usando modelos de lenguaje (LLM).

    Esta clase utiliza proveedores LLM (como OpenAI, Gemini, etc.)
    para mejorar la calidad del texto extraído por OCR, corrigiendo
    errores y mejorando la coherencia.
    """

    def __init__(self):
        """Inicializa el refinador con la configuración actual."""
        self.config = app_config.llm
        # Obtenemos max_retries del proveedor seleccionado, con valor predeterminado de 3
        self.max_retries = 3
        # Establecemos un valor predeterminado para retry_delay
        self.retry_delay = 1
        # Prompt del sistema para refinar texto
        self.system_prompt = "Eres un asistente especializado en mejorar la calidad de texto extraído por OCR. Corrige errores tipográficos, mejora la coherencia y el formato, pero mantén todo el contenido original. No agregues información nueva."
        self.provider = self._get_provider()

    def _get_provider(self) -> Optional[LLMProvider]:
        """
        Obtiene la instancia del proveedor LLM configurado.

        Returns:
            Instancia del proveedor LLM o None si hay un error
        """
        try:
            llm_factory = LLMProviderFactory()
            # Accedemos a la propiedad correctamente
            provider_type = self.config.provider
            if not provider_type:
                logger.info("No se ha configurado un proveedor LLM")
                return None

            provider = llm_factory.create_provider(provider_type)

            if not provider:
                logger.error(
                    f"No se pudo crear el proveedor LLM: {provider_type}")
                return None

            logger.info(f"Proveedor LLM inicializado: {provider_type}")
            return provider

        except Exception as e:
            logger.error(f"Error inicializando proveedor LLM: {e}")
            return None

    def is_enabled(self) -> bool:
        """
        Verifica si el refinamiento LLM está habilitado y disponible.

        Returns:
            bool: True si el refinamiento LLM está disponible
        """
        return self.provider is not None and self.config.mode != 'off'

    def refine(self, text: str, max_chunk_size: int = 4000) -> str:
        """
        Refina el texto usando el proveedor LLM configurado.

        Args:
            text: Texto a refinar
            max_chunk_size: Tamaño máximo de cada fragmento para procesar

        Returns:
            Texto refinado o el texto original si hay un error
        """
        if not self.provider or not text:
            return text

        # Aplicar correcciones básicas primero
        text = _correct_ocr_errors(text)

        # Para textos largos, procesar por fragmentos
        if len(text) > max_chunk_size:
            return self._process_large_text(text, max_chunk_size)

        # Procesar texto completo si es suficientemente pequeño
        return self._refine_chunk(text)

    def _process_large_text(self, text: str, chunk_size: int) -> str:
        """
        Procesa textos largos dividiéndolos en fragmentos manejables.

        Args:
            text: Texto largo a procesar
            chunk_size: Tamaño máximo de cada fragmento

        Returns:
            Texto completo procesado
        """
        # Dividir el texto en párrafos
        paragraphs = re.split(r'\n\s*\n', text)

        # Agrupar párrafos en fragmentos de tamaño manejable
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_size:
                # Si el fragmento actual excede el tamaño, procesarlo
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    refined_chunk = self._refine_chunk(chunk_text)
                    chunks.append(refined_chunk)

                    # Reiniciar fragmento
                    current_chunk = [para]
                    current_size = para_size
                else:
                    # Si un párrafo es demasiado grande, procesarlo individualmente
                    refined_para = self._refine_chunk(para)
                    chunks.append(refined_para)
            else:
                # Añadir párrafo al fragmento actual
                current_chunk.append(para)
                current_size += para_size

        # Procesar el último fragmento si existe
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            refined_chunk = self._refine_chunk(chunk_text)
            chunks.append(refined_chunk)

        # Unir todos los fragmentos procesados
        return "\n\n".join(chunks)

    def _refine_chunk(self, text: str) -> str:
        """
        Refina un fragmento de texto usando el proveedor LLM.

        Args:
            text: Fragmento de texto a refinar

        Returns:
            Texto refinado o el original si hay un error
        """
        if not text.strip():
            return text

        retries = 0

        while retries <= self.max_retries:
            try:
                # Enviar al LLM para refinamiento
                response = self.provider.generate_completion(
                    system_prompt=self.system_prompt,
                    user_prompt=text,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )

                if response and response.strip():
                    return response.strip()

                logger.warning("El proveedor LLM devolvió una respuesta vacía")
                return text

            except Exception as e:
                retries += 1
                logger.warning(
                    f"Error refinando texto (intento {retries}/{self.max_retries}): {e}")

                if retries <= self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Refinamiento fallido después de {self.max_retries} intentos")
                    return text

        return text
