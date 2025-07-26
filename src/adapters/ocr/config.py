# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/config.py
#  Python 3.11 • Configuración de OCR
# ──────────────────────────────────────────────────────────────

"""
Configuración y constantes para el sistema OCR.
"""

import logging
from pathlib import Path

# ───────────────────────── Configuración global ─────────────────────────
DPI = 300
TESSERACT_CONFIG = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG = "spa"
CORRECTIONS_PATH = Path("data/corrections.csv")

# Configurar logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def build_tesseract_config(psm: int) -> str:
    """
    Construye la configuración de Tesseract OCR personalizada.

    Args:
        psm (int): Page Segmentation Mode para Tesseract.

    Returns:
        str: Cadena de configuración completa.
    """
    parts = [
        f"--psm {psm}",
        "--oem 3",
        f"-c user_defined_dpi={DPI}"
    ]

    # Archivos personalizados de usuario (si existen)
    words_path = Path("data/legal_words.txt")
    patterns_path = Path("data/legal_patterns.txt")

    if words_path.exists():
        parts.append(f"--user-words {words_path}")
    if patterns_path.exists():
        parts.append(f"--user-patterns {patterns_path}")

    return " ".join(parts)
