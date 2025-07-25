"""
Puerto para el procesamiento OCR de documentos.
Define la interfaz que deben implementar los adaptadores OCR.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

class OCRPort(ABC):
    """Interfaz abstracta para procesamiento OCR."""
    
    @abstractmethod
    def extract_text(self, image: bytes) -> str:
        """
        Extrae texto de una imagen usando OCR.
        
        Args:
            image: Datos binarios de la imagen
            
        Returns:
            str: Texto extraído
        """
        pass
    
    @abstractmethod
    def detect_tables(self, image: bytes) -> List[dict]:
        """
        Detecta tablas en una imagen.
        
        Args:
            image: Datos binarios de la imagen
            
        Returns:
            List[dict]: Lista de tablas detectadas con sus coordenadas
        """
        pass
    
    @abstractmethod
    def needs_ocr(self, page_content: str) -> bool:
        """
        Determina si una página necesita OCR.
        
        Args:
            page_content: Contenido de texto de la página
            
        Returns:
            bool: True si se requiere OCR
        """
        pass
