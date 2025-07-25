"""
Puerto para el almacenamiento de archivos.
Define la interfaz que deben implementar los adaptadores de almacenamiento.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class StoragePort(ABC):
    """Interfaz abstracta para almacenamiento de archivos."""
    
    @abstractmethod
    def save_markdown(self, filename: str, content: str) -> Path:
        """
        Guarda contenido como archivo Markdown.
        
        Args:
            filename: Nombre del archivo sin extensión
            content: Contenido Markdown a guardar
            
        Returns:
            Path: Ruta al archivo guardado
        """
        pass
    
    @abstractmethod
    def read_file(self, file_path: Path) -> str:
        """
        Lee el contenido de un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            str: Contenido del archivo
        """
        pass
    
    @abstractmethod
    def ensure_directory(self, directory: Path) -> None:
        """
        Asegura que un directorio existe.
        
        Args:
            directory: Ruta al directorio
        """
        pass
