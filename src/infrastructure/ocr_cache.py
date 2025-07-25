"""
Sistema de caché para resultados OCR.
"""
import hashlib
from functools import lru_cache
from PIL import Image
import numpy as np

class OCRCache:
    @lru_cache(maxsize=100)
    def get_image_hash(self, image: Image.Image) -> str:
        """Genera un hash único para una imagen."""
        img_array = np.array(image)
        return hashlib.md5(img_array.tobytes()).hexdigest()
    
    @lru_cache(maxsize=50)
    def get_cached_ocr_result(self, image_hash: str) -> str:
        """Obtiene resultado OCR cacheado por hash de imagen."""
        pass  # Implementar lógica de almacenamiento
    
    def clear_cache(self):
        """Limpia la caché de resultados."""
        self.get_image_hash.cache_clear()
        self.get_cached_ocr_result.cache_clear()
