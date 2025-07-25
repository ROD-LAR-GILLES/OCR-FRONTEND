"""
Procesamiento de texto para OCR.

Este módulo contiene funciones para mejorar y corregir el texto extraído por OCR.
"""

import logging
import re
import os
import csv
from typing import Dict, List, Tuple

# Configurar logger
logger = logging.getLogger(__name__)

# Patrones y correcciones
CORRECTIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))), 'data', 'corrections.csv')
LEGAL_PATTERNS_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))), 'data', 'legal_patterns.txt')
LEGAL_WORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))), 'data', 'legal_words.txt')


def load_corrections() -> Dict[str, str]:
    """
    Carga las correcciones comunes de OCR desde el archivo CSV.

    Returns:
        Dict[str, str]: Diccionario de correcciones {error: corrección}
    """
    corrections = {}
    try:
        if os.path.exists(CORRECTIONS_PATH):
            with open(CORRECTIONS_PATH, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2:
                        corrections[row[0]] = row[1]
            logger.info(f"Cargadas {len(corrections)} correcciones de OCR")
        else:
            logger.warning(
                f"Archivo de correcciones no encontrado: {CORRECTIONS_PATH}")
    except Exception as e:
        logger.error(f"Error cargando correcciones: {e}")

    return corrections


def load_legal_patterns() -> List[Tuple[str, str]]:
    """
    Carga patrones de texto legal desde el archivo.

    Returns:
        List[Tuple[str, str]]: Lista de tuplas (patrón, reemplazo)
    """
    patterns = []
    try:
        if os.path.exists(LEGAL_PATTERNS_PATH):
            with open(LEGAL_PATTERNS_PATH, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and '::' in line:
                        pattern, replacement = line.split('::', 1)
                        patterns.append((pattern.strip(), replacement.strip()))
            logger.info(f"Cargados {len(patterns)} patrones legales")
        else:
            logger.warning(
                f"Archivo de patrones legales no encontrado: {LEGAL_PATTERNS_PATH}")
    except Exception as e:
        logger.error(f"Error cargando patrones legales: {e}")

    return patterns


def load_legal_words() -> List[str]:
    """
    Carga palabras legales desde el archivo.

    Returns:
        List[str]: Lista de palabras legales
    """
    words = []
    try:
        if os.path.exists(LEGAL_WORDS_PATH):
            with open(LEGAL_WORDS_PATH, 'r', encoding='utf-8') as file:
                for line in file:
                    word = line.strip()
                    if word:
                        words.append(word)
            logger.info(f"Cargadas {len(words)} palabras legales")
        else:
            logger.warning(
                f"Archivo de palabras legales no encontrado: {LEGAL_WORDS_PATH}")
    except Exception as e:
        logger.error(f"Error cargando palabras legales: {e}")

    return words


# Cargar recursos al importar el módulo
corrections_dict = load_corrections()
legal_patterns = load_legal_patterns()
legal_words = load_legal_words()


def apply_corrections(text: str) -> str:
    """
    Aplica correcciones comunes de OCR al texto.

    Args:
        text (str): Texto original con errores de OCR

    Returns:
        str: Texto corregido
    """
    if not text:
        return text

    corrected = text

    # Aplicar correcciones específicas de palabras
    for error, correction in corrections_dict.items():
        # Usar expresión regular para reemplazar solo palabras completas
        corrected = re.sub(r'\b' + re.escape(error) +
                           r'\b', correction, corrected)

    # Corregir errores comunes de OCR

    # Espacios duplicados
    corrected = re.sub(r' +', ' ', corrected)

    # Caracteres mal reconocidos
    char_corrections = {
        'l\\.': 'I.',  # l. -> I.
        'l,': 'I,',    # l, -> I,
        'ﬁ': 'fi',     # ligaduras
        'ﬂ': 'fl',
        'ﬀ': 'ff',
        '—': '-',      # guiones
        '–': '-',
        '‐': '-',
        ''': "'",      # comillas
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',    # puntos suspensivos
        '•': '*',      # viñetas
        '·': '•',
        '\\\\': '\\',  # barras
        '\\|': '|'
    }

    for error, fix in char_corrections.items():
        corrected = corrected.replace(error, fix)

    # Corregir problemas con números
    # Cambiar punto decimal por coma
    corrected = re.sub(r'(\d)\.(\d)', r'\1,\2', corrected)

    # Corregir errores de salto de línea
    # Cambiar saltos de línea únicos por espacios
    corrected = re.sub(r'(?<!\n)\n(?!\n)', ' ', corrected)
    # Normalizar múltiples saltos de línea
    corrected = re.sub(r'\n{3,}', '\n\n', corrected)

    return corrected


def fix_line_breaks(text: str) -> str:
    """
    Arregla los saltos de línea para mantener párrafos coherentes.

    Args:
        text (str): Texto original con saltos de línea incorrectos

    Returns:
        str: Texto con saltos de línea corregidos
    """
    if not text:
        return text

    # Preservar saltos de línea dobles (párrafos)
    text = re.sub(r'\n{2,}', '[PARAGRAPH]', text)

    # Juntar líneas rotas dentro del mismo párrafo
    lines = text.split('\n')
    result = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Verificar si la línea termina con un carácter que indica continuación
        ends_with_continuation = any(line.endswith(c)
                                     for c in [',', ':', ';', '-'])

        # Verificar si la línea actual no termina con punto
        no_sentence_end = not line.endswith(
            '.') and not line.endswith('!') and not line.endswith('?')

        # Verificar si la siguiente línea comienza con minúscula (continuación)
        next_starts_lowercase = i < len(
            lines) - 1 and lines[i+1].strip() and lines[i+1][0].islower()

        if ends_with_continuation or (no_sentence_end and next_starts_lowercase):
            # Es continuación, no añadir salto de línea
            result.append(line + ' ')
        else:
            # Es fin de párrafo o oración completa
            result.append(line + '\n')

    # Restaurar párrafos
    text = ''.join(result).replace('[PARAGRAPH]', '\n\n')

    # Eliminar espacios en blanco al principio y final
    text = text.strip()

    return text


def apply_legal_corrections(text: str) -> str:
    """
    Aplica correcciones específicas para texto legal.

    Args:
        text (str): Texto original

    Returns:
        str: Texto con correcciones legales aplicadas
    """
    if not text:
        return text

    corrected = text

    # Aplicar patrones de texto legal
    for pattern, replacement in legal_patterns:
        corrected = re.sub(pattern, replacement, corrected)

    # Corregir referencias a artículos
    corrected = re.sub(r'(?i)art(?:\.|\s)?(\s*)(\d+)',
                       r'Artículo\1\2', corrected)
    corrected = re.sub(r'(?i)artículo(\d+)', r'Artículo \1', corrected)

    # Corregir referencias a leyes
    corrected = re.sub(
        r'(?i)ley(?:\.|\s)?(\s*)(\d+[\/\.\-][0-9]+)', r'Ley\1\2', corrected)

    # Corregir números de párrafos
    corrected = re.sub(r'(\d+)\)\.', r'\1).', corrected)

    # Asegurar correcta capitalización de palabras legales
    for word in legal_words:
        # Solo corregir si la palabra está en minúsculas
        corrected = re.sub(r'(?<!\w)' + word.lower() +
                           r'(?!\w)', word, corrected, flags=re.IGNORECASE)

    return corrected


def clean_and_format_text(text: str, is_legal_doc: bool = False) -> str:
    """
    Limpia y formatea el texto completo aplicando todas las correcciones.

    Args:
        text (str): Texto original del OCR
        is_legal_doc (bool): Indica si es un documento legal

    Returns:
        str: Texto limpio y formateado
    """
    if not text:
        return ""

    # Aplicar correcciones básicas
    clean_text = apply_corrections(text)

    # Arreglar saltos de línea
    clean_text = fix_line_breaks(clean_text)

    # Aplicar correcciones legales si es necesario
    if is_legal_doc:
        clean_text = apply_legal_corrections(clean_text)

    # Eliminar espacios en blanco al principio y final
    clean_text = clean_text.strip()

    return clean_text


def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto usando patrones sencillos.
    Para una detección más precisa, se recomienda usar el adaptador de detección de idioma.

    Args:
        text (str): Texto a analizar

    Returns:
        str: Código de idioma ('spa', 'eng', etc.)
    """
    # Palabras de función frecuentes en español
    spanish_markers = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
                       'y', 'o', 'pero', 'porque', 'como', 'que', 'cuando',
                       'del', 'al', 'es', 'son', 'está', 'están', 'para', 'por']

    # Palabras de función frecuentes en inglés
    english_markers = ['the', 'a', 'an', 'and', 'or', 'but', 'because', 'as',
                       'that', 'when', 'is', 'are', 'be', 'to', 'for', 'with', 'by']

    # Contar ocurrencias
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_markers if re.search(
        r'\b' + word + r'\b', text_lower))
    english_count = sum(1 for word in english_markers if re.search(
        r'\b' + word + r'\b', text_lower))

    # Calcular proporciones
    spanish_ratio = spanish_count / len(spanish_markers)
    english_ratio = english_count / len(english_markers)

    # Determinar idioma basado en la mayor proporción
    if spanish_ratio > english_ratio:
        return 'spa'
    elif english_ratio > spanish_ratio:
        return 'eng'
    else:
        # Si no hay clara preferencia, revisar acentos y caracteres especiales
        if re.search(r'[áéíóúüñ¿¡]', text):
            return 'spa'
        else:
            return 'eng'


def split_into_sections(text: str) -> List[str]:
    """
    Divide el texto en secciones lógicas basadas en títulos y subtítulos.

    Args:
        text (str): Texto completo

    Returns:
        List[str]: Lista de secciones
    """
    # Patrones de título común
    title_patterns = [
        r'^#+\s+.+$',  # Títulos markdown
        r'^[A-Z][A-Z\s]+:',  # TÍTULO EN MAYÚSCULAS:
        r'^[IVX]+\.\s+.+$',  # Números romanos
        r'^\d+\.\s+[A-Z]',  # Números seguidos de texto
        r'^CAPÍTULO\s+[IVXLCDM]+',  # Capítulos
        r'^Artículo\s+\d+',  # Artículos
    ]

    # Compilar patrones
    compiled_patterns = [re.compile(pattern, re.MULTILINE)
                         for pattern in title_patterns]

    # Dividir por párrafos
    paragraphs = re.split(r'\n{2,}', text)

    sections = []
    current_section = []

    for paragraph in paragraphs:
        # Verificar si el párrafo coincide con algún patrón de título
        is_title = any(pattern.match(paragraph.strip())
                       for pattern in compiled_patterns)

        # Si es un título y ya tenemos contenido, comenzar nueva sección
        if is_title and current_section:
            sections.append('\n\n'.join(current_section))
            current_section = [paragraph]
        else:
            current_section.append(paragraph)

    # Añadir la última sección
    if current_section:
        sections.append('\n\n'.join(current_section))

    return sections
