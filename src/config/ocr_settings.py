"""
Configuración centralizada para el sistema OCR y LLM.

Clases:
    OCRSettings: Configuración general del sistema OCR y LLM
"""

# Configuración de modelos OpenAI
import os

class OpenAIModels:
    """Modelos de OpenAI disponibles"""
import os
from pathlib import Path

class OCRSettings:
    # Configuración básica
    DPI = int(os.getenv('OCR_DPI', 300))
    OCR_LANG = os.getenv('OCR_LANG', 'spa')
    
    # Rutas
    CORRECTIONS_PATH = Path("data/corrections.csv")
    WORDS_PATH = Path("data/legal_words.txt")
    PATTERNS_PATH = Path("data/legal_patterns.txt")
    
    # Parámetros de procesamiento de imagen
    CLAHE_CLIP_LIMIT = 3.0
    CLAHE_GRID_SIZE = (8, 8)
    ADAPTIVE_THRESH_BLOCK_SIZE = 31
    ADAPTIVE_THRESH_C = 15
    
    # Parámetros de detección de tablas
    MIN_TABLE_WIDTH = 50
    MIN_TABLE_HEIGHT = 30
    
    # Configuración de logging
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_LEVEL = os.getenv('OCR_LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_tesseract_config(cls, psm: int) -> str:
        return f"--psm {psm} --oem 1 -c user_defined_dpi={cls.DPI}"
