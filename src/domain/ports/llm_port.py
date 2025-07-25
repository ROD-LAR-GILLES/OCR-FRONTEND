"""
Puerto para el refinamiento de texto usando LLMs.
Define la interfaz que deben implementar los adaptadores de LLM.
"""
from abc import ABC, abstractmethod
from typing import Optional

class LLMPort(ABC):
    """Interfaz abstracta para refinamiento de texto con LLMs."""
    
    @abstractmethod
    def refine_text(self, text: str) -> str:
        """
        Refina y mejora un texto usando LLM.
        
        Args:
            text: Texto a refinar
            
        Returns:
            str: Texto refinado
        """
        pass
    
    @abstractmethod
    def detect_structure(self, text: str) -> dict:
        """
        Detecta la estructura del documento en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            dict: Estructura detectada (secciones, listas, etc)
        """
        pass
    
    @abstractmethod
    def format_markdown(self, text: str) -> str:
        """
        Formatea texto como Markdown usando LLM.
        
        Args:
            text: Texto a formatear
            
        Returns:
            str: Texto formateado en Markdown
        """
        pass
