"""
Adaptador de almacenamiento que implementa el puerto StoragePort.

Este adaptador proporciona implementaciones concretas para las operaciones
de almacenamiento definidas en el puerto StoragePort del dominio, utilizando
el sistema de archivos local para persistir los datos.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from domain.ports.storage_port import StoragePort
from shared.util.config import AppConfig

# Instancia de configuración
app_config = AppConfig()

logger = logging.getLogger(__name__)

# Directorio para resultados procesados
RESULT_DIR = Path("./result")
RESULT_DIR.mkdir(exist_ok=True)


class StorageAdapter(StoragePort):
    """
    Adaptador de almacenamiento que implementa el puerto StoragePort.

    Esta clase proporciona una implementación concreta de las operaciones
    de almacenamiento utilizando el sistema de archivos local.
    """

    def ensure_directory(self, directory: Path) -> None:
        """
        Asegura que un directorio exista, creándolo si es necesario.

        Args:
            directory: Ruta del directorio a asegurar
        """
        directory.mkdir(parents=True, exist_ok=True)

    def read_file(self, filepath: Path) -> Optional[str]:
        """
        Lee el contenido de un archivo si existe.

        Args:
            filepath: Ruta del archivo a leer

        Returns:
            El contenido del archivo o None si no existe
        """
        try:
            if filepath.exists():
                return filepath.read_text(encoding="utf-8")
            return None
        except Exception as e:
            logger.error(f"Error leyendo archivo {filepath}: {e}")
            return None

    def save_markdown(self, filename: str, content: str) -> Path:
        """
        Guarda contenido en formato Markdown en un archivo.

        Args:
            filename: Nombre del archivo sin extensión
            content: Contenido Markdown a guardar

        Returns:
            Path: Ruta del archivo guardado
        """
        self.ensure_directory(RESULT_DIR)
        filepath = RESULT_DIR / f"{filename}.md"
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Markdown guardado en {filepath}")
        return filepath

    def save_json(self, filename: str, data: Dict[str, Any]) -> Path:
        """
        Guarda datos en formato JSON en un archivo.

        Args:
            filename: Nombre del archivo sin extensión
            data: Datos a guardar en formato JSON

        Returns:
            Path: Ruta del archivo guardado
        """
        import json
        filepath = RESULT_DIR / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON guardado en {filepath}")
        return filepath

    def load_json(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Carga datos en formato JSON desde un archivo.

        Args:
            filepath: Ruta al archivo JSON

        Returns:
            Dict o None: Datos cargados o None si hay error
        """
        import json
        try:
            if not filepath.exists():
                logger.warning(f"El archivo {filepath} no existe")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar JSON desde {filepath}: {str(e)}")
            return None

    def save_binary(self, filepath: Path, data: bytes) -> bool:
        """
        Guarda datos binarios en un archivo.

        Args:
            filepath: Ruta completa incluyendo nombre de archivo
            data: Datos binarios a guardar

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_bytes(data)
            logger.debug(f"Datos binarios guardados en {filepath}")
            return True
        except Exception as e:
            logger.error(
                f"Error al guardar datos binarios en {filepath}: {str(e)}")
            return False

    def list_files(self, directory: Path, pattern: str = "*") -> List[Path]:
        """
        Lista archivos en un directorio que coinciden con un patrón.

        Args:
            directory: Directorio a listar
            pattern: Patrón glob para filtrar archivos

        Returns:
            List[Path]: Lista de rutas a archivos
        """
        try:
            if not directory.exists():
                logger.warning(f"El directorio {directory} no existe")
                return []

            return list(directory.glob(pattern))
        except Exception as e:
            logger.error(f"Error al listar archivos en {directory}: {str(e)}")
            return []
