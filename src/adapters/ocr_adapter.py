# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr_adapter.py
#  Python 3.11 • Punto de entrada modular para OCR
# ──────────────────────────────────────────────────────────────

"""
Punto de entrada para el sistema OCR modular.
Mantiene compatibilidad hacia atrás importando de los módulos especializados.

El código ha sido reorganizado en:
- ocr/config.py: Configuración y constantes
- ocr/engine.py: Motor principal de OCR
- ocr/image_processing.py: Preprocesamiento de imágenes
- ocr/tables.py: Detección y extracción de tablas
- ocr/text_processing.py: Post-procesamiento de texto
- ocr/utils.py: Utilidades varias
"""

# Importar todas las funciones de los módulos especializados
from .ocr import *
