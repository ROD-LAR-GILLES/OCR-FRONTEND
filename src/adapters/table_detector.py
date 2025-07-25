"""
Mejoras en la detección y validación de tablas.
"""
from dataclasses import dataclass
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image
from config.ocr_settings import OCRSettings

@dataclass
class TableValidationResult:
    is_valid: bool
    confidence: float
    num_rows: int
    num_cols: int

class TableDetector:
    def __init__(self):
        self.min_confidence = 0.7
        
    def validate_table_structure(self, region: np.ndarray) -> TableValidationResult:
        """Valida la estructura de una tabla candidata."""
        # Detectar líneas
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return TableValidationResult(False, 0.0, 0, 0)
            
        # Separar líneas horizontales y verticales
        h_lines = []
        v_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 10:  # horizontal
                h_lines.append((min(x1, x2), max(x1, x2), y1))
            elif abs(x2 - x1) < 10:  # vertical
                v_lines.append((x1, min(y1, y2), max(y1, y2)))
                
        # Calcular filas y columnas
        num_rows = len(set(l[2] for l in h_lines))
        num_cols = len(set(l[0] for l in v_lines))
        
        # Calcular confianza
        min_expected = 2  # mínimo 2 filas y 2 columnas
        confidence = min(1.0, (num_rows/min_expected + num_cols/min_expected) / 2)
        
        return TableValidationResult(
            is_valid=confidence >= self.min_confidence,
            confidence=confidence,
            num_rows=num_rows,
            num_cols=num_cols
        )
