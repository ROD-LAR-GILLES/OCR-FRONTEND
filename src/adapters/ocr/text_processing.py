# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr/text_processing.py
#  Python 3.11 • Post-procesamiento de texto OCR
# ──────────────────────────────────────────────────────────────

"""
Funciones para limpieza y post-procesamiento de texto OCR.
"""

import csv
import re
import unicodedata
from pathlib import Path

from .config import CORRECTIONS_PATH


def cleanup_text(text: str) -> str:
    """
    Normaliza y limpia el texto OCR:
    • Normaliza Unicode a NFKC.
    • Elimina caracteres no imprimibles.
    • Convierte múltiples espacios en uno.
    • Retira líneas con muy baja proporción de caracteres alfabéticos (<30 %).

    Args:
        text (str): Texto bruto OCR.

    Returns:
        str: Texto limpio.
    """
    text = unicodedata.normalize("NFKC", text)
    # Normalización Unicode y limpieza de ruido OCR
    # Sustituir cualquier carácter que NO sea letra, número, puntuación básica o espacio
    text = re.sub(r"[^\w\sÁÉÍÓÚÜÑñáéíóúü¿¡.,;:%\-()/]", " ", text)
    # Colapsar espacios repetidos
    text = re.sub(r"\s{2,}", " ", text)

    # Filtrar líneas con mucho ruido
    cleaned_lines = []
    for line in text.splitlines():
        letters = sum(c.isalpha() for c in line)
        ratio = letters / max(len(line), 1)
        if ratio >= 0.3:
            cleaned_lines.append(line.strip())
    return "\n".join(cleaned_lines)


def detect_structured_headings(text: str) -> str:
    """
    Aplica formato Markdown a encabezados legales típicos como 'VISTOS', 'CONSIDERANDO', 'RESUELVO', 'DECRETO', etc.

    Args:
        text (str): Texto OCR limpio.

    Returns:
        str: Texto con encabezados jerarquizados en Markdown.
    """
    headings = ["VISTOS", "CONSIDERANDO", "RESUELVO", "DECRETO",
                "FUNDAMENTO", "TENIENDO PRESENTE", "POR TANTO"]
    for heading in headings:
        # Reemplaza solo si aparece como línea sola o seguida de dos puntos
        text = re.sub(rf"(?m)^\s*{heading}[:\s]*", f"\n### {heading}\n", text)
    return text


def segment_text_blocks(text: str) -> str:
    """
    Aplica segmentación por bloques heurística:
    • Divide por saltos de línea dobles.
    • Inserta encabezados Markdown si el bloque comienza con ciertas palabras clave o está en mayúsculas.

    Args:
        text (str): Texto plano preprocesado.

    Returns:
        str: Texto con divisiones y encabezados Markdown.
    """
    blocks = text.split("\n\n")
    out_blocks = []

    for block in blocks:
        stripped = block.strip()
        if not stripped:
            continue

        # Heurística 1: Si el bloque está en mayúsculas y es corto, asumimos encabezado
        if stripped.isupper() and len(stripped) < 80:
            out_blocks.append(f"### {stripped}")
        # Heurística 2: Palabras clave típicas de secciones legales
        elif any(stripped.startswith(word) for word in ["Artículo", "Capítulo", "Sección", "Título"]):
            out_blocks.append(f"### {stripped}")
        else:
            out_blocks.append(stripped)

    return "\n\n".join(out_blocks)


def detect_lists(text: str) -> str:
    """
    Detecta listas numeradas o con viñetas y las convierte a formato Markdown.
    - 1. Item → 1. Item
    - • Item → - Item

    Args:
        text (str): Texto plano.

    Returns:
        str: Texto con formato de lista en Markdown.
    """
    lines = text.splitlines()
    output = []
    for line in lines:
        line = line.strip()
        if re.match(r"^\(?\d+[\.\)-]", line):
            line = re.sub(r"^\(?(\d+)[\.\)-]\s*", r"\1. ", line)
        elif re.match(r"^[-•–]", line):
            line = re.sub(r"^[-•–]\s*", "- ", line)
        output.append(line)
    return "\n".join(output)


def apply_manual_corrections(text: str) -> str:
    """
    Sustituye errores comunes según data/corrections.csv (ocr, correct).
    """
    if not CORRECTIONS_PATH.exists():
        return text

    with CORRECTIONS_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            bad, good = row["ocr"], row["correct"]
            # Reemplazo sólo si coincide como palabra completa (evita falsos positivos)
            text = re.sub(rf"\b{re.escape(bad)}\b", good,
                          text, flags=re.IGNORECASE)
    return text
