"""
Puerto para el procesamiento de documentos PDF.
Define la interfaz que deben implementar los adaptadores de documentos.
"""
from abc import ABC, abstractmethod
from pathlib import Path

class DocumentPort(ABC):
    """Interfaz abstracta para procesamiento de documentos PDF."""
    
    @abstractmethod
    def extract_markdown(self, pdf_path: Path) -> str:
        """
        Extrae contenido de un PDF y lo convierte a Markdown.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            str: Contenido del PDF en formato Markdown
        """
        pass
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

class DocumentPort(ABC):
    """Interfaz abstracta para procesamiento de documentos PDF."""
    
    @abstractmethod
    def extract_markdown(self, pdf_path: Path) -> str:
        """
        Extrae contenido de un PDF y lo convierte a Markdown.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            str: Contenido en formato Markdown
        """
        pass
    
    @abstractmethod
    def extract_pages(self, pdf_path: Path) -> List[str]:
        """
        Extrae el contenido de todas las páginas de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            List[str]: Lista de contenido por página
        """
        pass
    
    @abstractmethod
    def extract_tables(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extrae todas las tablas encontradas en el PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            List[Tuple[int, str]]: Lista de (número_página, tabla_markdown)
        """
        pass
