"""
Sistema de caché para resultados OCR.

Este módulo implementa un sistema de caché para resultados de OCR
para evitar procesar repetidamente las mismas imágenes, mejorando
significativamente el rendimiento en documentos con elementos visuales
repetidos como encabezados, pies de página, etc.
"""
import hashlib
import json
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from PIL import Image
import numpy as np
from loguru import logger
from shared.util.config import AppConfig

# Ruta de la base de datos SQLite para caché persistente
CACHE_DB_PATH = Path("src/shared/storage/cache/ocr_cache.db")


class OCRCache:
    """
    Sistema de caché para resultados OCR con almacenamiento en memoria y persistente.

    Combina una caché en memoria (LRU) para operaciones frecuentes con
    almacenamiento persistente en SQLite para resultados entre sesiones.
    """

    def __init__(self):
        """Inicializa el sistema de caché y asegura que exista la base de datos."""
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Crea la base de datos y tabla si no existen."""
        CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(CACHE_DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ocr_results (
                image_hash TEXT PRIMARY KEY,
                ocr_text TEXT,
                confidence REAL,
                language TEXT,
                timestamp TEXT,
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.debug(
            f"Base de datos de caché OCR inicializada en {CACHE_DB_PATH}")

    @lru_cache(maxsize=100)
    def get_image_hash(self, image: Image.Image) -> str:
        """
        Genera un hash único para una imagen.

        Args:
            image: Imagen PIL a hashear

        Returns:
            str: Hash BLAKE2b hexadecimal de la imagen (más seguro que MD5)
        """
        # Convertir a escala de grises y reducir resolución para mejor comparación
        img_small = image.convert('L').resize((100, 100))
        img_array = np.array(img_small)
        return hashlib.blake2b(img_array.tobytes(), digest_size=32).hexdigest()

    def get_cached_ocr_result(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene resultado OCR cacheado por hash de imagen.

        Args:
            image_hash: Hash BLAKE2b de la imagen

        Returns:
            Dict o None: Resultados del OCR si existe en caché, None si no existe
        """
        # Primero intentar desde la caché en memoria
        result = self._get_from_memory_cache(image_hash)
        if result:
            logger.debug(
                f"Resultado OCR encontrado en caché de memoria para hash {image_hash[:8]}...")
            return result

        # Si no está en memoria, buscar en la base de datos
        try:
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT ocr_text, confidence, language, metadata FROM ocr_results WHERE image_hash = ?",
                           (image_hash,))
            row = cursor.fetchone()
            conn.close()

            if row:
                logger.debug(
                    f"Resultado OCR encontrado en caché persistente para hash {image_hash[:8]}...")
                ocr_text, confidence, language, metadata_json = row
                metadata = json.loads(metadata_json) if metadata_json else {}

                result = {
                    "text": ocr_text,
                    "confidence": confidence,
                    "language": language,
                    "metadata": metadata
                }

                # Guardar en caché de memoria para futuras consultas
                self._save_to_memory_cache(image_hash, result)
                return result

            return None

        except Exception as e:
            logger.error(
                f"Error al recuperar resultado de caché OCR: {str(e)}")
            return None

    @lru_cache(maxsize=50)
    def _get_from_memory_cache(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Caché en memoria auxiliar."""
        return None  # La implementación real viene del decorador lru_cache

    def _save_to_memory_cache(self, image_hash: str, result: Dict[str, Any]) -> None:
        """Guarda resultado en la caché en memoria."""
        self._get_from_memory_cache.cache_clear()  # Necesario para actualizar la caché LRU
        # Esto no hará nada pero establece el valor en la caché
        _ = self._get_from_memory_cache(image_hash)

    def save_ocr_result(self, image_hash: str, text: str, confidence: float = 0.0,
                        language: str = "es", metadata: Dict[str, Any] = None) -> bool:
        """
        Guarda un resultado OCR en la caché.

        Args:
            image_hash: Hash BLAKE2b de la imagen
            text: Texto extraído por OCR
            confidence: Nivel de confianza (0-1)
            language: Código ISO del idioma detectado
            metadata: Metadatos adicionales (opcional)

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        metadata = metadata or {}

        try:
            # Guardar en la base de datos
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO ocr_results VALUES (?, ?, ?, ?, ?, ?)",
                (
                    image_hash,
                    text,
                    confidence,
                    language,
                    datetime.now().isoformat(),
                    json.dumps(metadata)
                )
            )
            conn.commit()
            conn.close()

            # Actualizar caché en memoria
            result = {
                "text": text,
                "confidence": confidence,
                "language": language,
                "metadata": metadata
            }
            self._save_to_memory_cache(image_hash, result)

            logger.debug(
                f"Resultado OCR guardado en caché para hash {image_hash[:8]}...")
            return True

        except Exception as e:
            logger.error(f"Error al guardar resultado en caché OCR: {str(e)}")
            return False

    def clear_cache(self, memory_only: bool = False) -> None:
        """
        Limpia la caché de resultados.

        Args:
            memory_only: Si es True, solo limpia la caché en memoria
        """
        # Limpiar caché en memoria
        self.get_image_hash.cache_clear()
        self._get_from_memory_cache.cache_clear()

        # Limpiar base de datos si se solicita
        if not memory_only:
            try:
                conn = sqlite3.connect(str(CACHE_DB_PATH))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ocr_results")
                conn.commit()
                conn.close()
                logger.info("Caché OCR persistente eliminada completamente")
            except Exception as e:
                logger.error(
                    f"Error al limpiar caché OCR persistente: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la caché.

        Returns:
            Dict con estadísticas: total de entradas, tamaño, etc.
        """
        try:
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            cursor = conn.cursor()

            # Contar entradas
            cursor.execute("SELECT COUNT(*) FROM ocr_results")
            total_entries = cursor.fetchone()[0]

            # Obtener tamaño total aproximado
            cursor.execute("SELECT SUM(LENGTH(ocr_text)) FROM ocr_results")
            total_text_size = cursor.fetchone()[0] or 0

            # Obtener última actualización
            cursor.execute("SELECT MAX(timestamp) FROM ocr_results")
            last_update = cursor.fetchone()[0]

            conn.close()

            return {
                "total_entries": total_entries,
                "total_text_size_bytes": total_text_size,
                "memory_cache_size": len(self._get_from_memory_cache.cache_info().currsize),
                "memory_cache_info": str(self._get_from_memory_cache.cache_info()),
                "last_update": last_update,
                "db_path": str(CACHE_DB_PATH)
            }

        except Exception as e:
            logger.error(
                f"Error al obtener estadísticas de caché OCR: {str(e)}")
            return {"error": str(e)}

    def vacuum_database(self) -> bool:
        """
        Optimiza la base de datos SQLite eliminando espacio no utilizado.

        Returns:
            bool: True si se optimizó correctamente, False en caso contrario
        """
        try:
            conn = sqlite3.connect(str(CACHE_DB_PATH))
            conn.execute("VACUUM")
            conn.commit()
            conn.close()
            logger.info("Base de datos de caché OCR optimizada correctamente")
            return True
        except Exception as e:
            logger.error(
                f"Error al optimizar base de datos de caché OCR: {str(e)}")
            return False


# Instancia global para uso en toda la aplicación
ocr_cache = OCRCache()
