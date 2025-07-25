"""
Configuración simplificada usando variables de entorno.
"""
import os
from pathlib import Path

class Settings:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
    OPENAI_PROMPT_MODEL = os.getenv("OPENAI_PROMPT_MODEL", "gpt-4")
    OPENAI_FT_MODEL = os.getenv("OPENAI_FT_MODEL", "gpt-3.5-turbo")
    
    # OCR
    OCR_DPI = int(os.getenv("OCR_DPI", "300"))
    OCR_LANG = os.getenv("OCR_LANG", "spa")
    OCR_LOG_LEVEL = os.getenv("OCR_LOG_LEVEL", "INFO")
    
    # Rutas
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
    CORRECTIONS_PATH = DATA_DIR / "corrections.csv"
    WORDS_PATH = DATA_DIR / "legal_words.txt"
    PATTERNS_PATH = DATA_DIR / "legal_patterns.txt"
    
    # Procesamiento de imagen
    CLAHE_CLIP_LIMIT = float(os.getenv("CLAHE_CLIP_LIMIT", "3.0"))
    CLAHE_GRID_SIZE = tuple(map(int, os.getenv("CLAHE_GRID_SIZE", "8,8").split(",")))
    ADAPTIVE_THRESH_BLOCK_SIZE = int(os.getenv("ADAPTIVE_THRESH_BLOCK_SIZE", "31"))
    ADAPTIVE_THRESH_C = int(os.getenv("ADAPTIVE_THRESH_C", "15"))
    
    # Detección de tablas
    MIN_TABLE_WIDTH = int(os.getenv("MIN_TABLE_WIDTH", "50"))
    MIN_TABLE_HEIGHT = int(os.getenv("MIN_TABLE_HEIGHT", "30"))

# Instancia global de configuración
settings = Settings()
