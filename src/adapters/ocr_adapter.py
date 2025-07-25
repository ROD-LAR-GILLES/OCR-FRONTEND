# ──────────────────────────────────────────────────────────────
#  File: src/adapters/ocr_adapter.py
#  Python 3.11 • sólo fitz, PIL, pytesseract
# ──────────────────────────────────────────────────────────────

"""Propósito: OCR básico por página usando PyMuPDF + pytesseract

• Renderiza páginas como imagen con fitz (300 DPI)
• Extrae texto con Tesseract OCR
• Utilizado como respaldo para PDFs escaneados

Configuración por defecto:
  - DPI: 300
  - --psm 6 : texto uniforme (ideal para líneas)
  - --oem 1 : motor LSTM (neural net)
  - lang='spa' : idioma español, combinable (ej: 'spa+eng')

Idiomas soportados:
  • eng, spa, fra, deu, ita, por, jpn, chi_sim, chi_tra...
  • Listar con: tesseract --list-langs
  • Instalar con: sudo apt install tesseract-ocr-spa (etc.)

Ejemplo de uso:
  image_to_string(img, lang="spa", config="--psm 6 --oem 1")
"""

import logging
import os
import re
import unicodedata
from io import BytesIO
from pathlib import Path
import csv
# Third-party
import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import image_to_string
# Local
import config.state as state
from config.language_detection import detector
from adapters.llm_refiner import LLMRefiner

# Inicializar el refinador LLM
llm_refiner = LLMRefiner()


#
# ───────────────────────── Configuración global ─────────────────────────
DPI                         = 300
TESSERACT_CONFIG            = f"--psm 6 --oem 1 -c user_defined_dpi={DPI}"
OCR_LANG                    = "spa"
CORRECTIONS_PATH            = Path("data/corrections.csv")
logging.basicConfig(format   ="%(levelname)s: %(message)s", level=logging.INFO)

# ──────────────────────────── Helper: Tesseract config builder ────────────────────────────
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

# ───────────────────────── OCR Principal ─────────────────────────


def perform_ocr_on_page(page: fitz.Page) -> str:
    """
    Realiza OCR sobre una página PDF.

    Args:
        page: Página PDF de PyMuPDF

    Returns:
        str: Texto extraído y procesado

    Proceso:
    1. Renderiza página
    2. Corrige rotación 
    3. Aplica preprocesamiento
    4. Ejecuta OCR con configuración dinámica
    5. Post-procesa resultado
    """
    # 1) Render
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))

    # 2) Deskew / rotate
    img_pil = correct_rotation(img_pil)

    # 3) Contraste local + binarizado
    gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    binar = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 15
    )
    # 4) Denoise ligero
    binar = cv2.morphologyEx(
        binar, cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)),
        iterations=1
    )
    img_pil = Image.fromarray(binar)

    # 5) PSM dinámico
    psm = estimate_psm_for_page(img_pil)
    config = build_tesseract_config(psm)

    # 6) Idioma fijado a español
    lang_param = "spa"

    # 7) OCR principal
    raw = pytesseract.image_to_string(img_pil, lang=lang_param, config=config)

    # 8) Limpieza y post-procesado existentes
    raw = re.sub(r"-\n(\w+)", r"\1", raw)
    cleaned = detect_lists(_cleanup_text(raw))
    cleaned = apply_manual_corrections(cleaned)
    segmented = segment_text_blocks(cleaned)

    # 9) Detección de tablas OCR (tu lógica actual)
    table_regions = detect_table_regions(img_pil)
    if table_regions:
        tables_md = []
        for region in table_regions:
            table_img = img_pil.crop(region)
            md_tbl = ocr_table_to_markdown(table_img)
            if md_tbl.strip():
                tables_md.append(md_tbl)
        if tables_md:
            segmented += "\n\n## Tablas detectadas\n" + "\n\n".join(tables_md)

    # 10) Refinamiento LLM opcional
    try:
        use_llm = os.getenv("OPENAI_API_KEY") and state.LLM_MODE in {"prompt", "auto", "ft"}
        if use_llm:
            logging.info(f"[LLM] Page-level refinement via OpenAI · mode={state.LLM_MODE}")
            segmented = llm_refiner.prompt_refine(segmented)
        else:
            logging.debug(
                f"[LLM] Skipped page-level · mode={state.LLM_MODE} · key={'set' if os.getenv('OPENAI_API_KEY') else 'unset'}"
            )
    except Exception as exc:
        logging.warning(f"[LLM] Page-level refinement error → {exc}")
    return detect_structured_headings(segmented)

# ──────────────── Detección de regiones de tabla ────────────────
def detect_table_regions(img: Image.Image):
    """
    Detecta regiones candidatas a ser tablas en la imagen (PIL) y retorna una lista de cajas (left, upper, right, lower).
    """
    import numpy as np
    import cv2
    img_gray = np.array(img.convert("L"))
    _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Detección de líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
    table_mask = cv2.add(horizontal_lines, vertical_lines)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(cnt) for cnt in contours]
    # Opcional: filtrar por tamaño mínimo
    boxes = [box for box in boxes if box[2] > 50 and box[3] > 30]
    # Convertir a formato PIL: (left, upper, right, lower)
    regions = [(x, y, x + w, y + h) for (x, y, w, h) in boxes]
    return regions


# ──────────────── OCR de tabla a Markdown ────────────────
def ocr_table_to_markdown(img: Image.Image) -> str:
    """
    Aplica OCR sobre una imagen de tabla y la convierte a formato Markdown simple.
    """
    config = build_tesseract_config(6)
    raw_text = image_to_string(img, lang="spa", config=config)
    lines = raw_text.strip().splitlines()
    lines = [line for line in lines if line.strip()]

    if len(lines) < 2:
        return ""

    # Separar por espacios o tabulaciones para obtener celdas
    header_cells = lines[0].split()
    header = "| " + " | ".join(header_cells) + " |"
    separator = "| " + " | ".join(["---"] * len(header_cells)) + " |"
    rows = []
    for line in lines[1:]:
        row_cells = line.split()
        # Si la fila tiene menos celdas que el header, rellenar
        if len(row_cells) < len(header_cells):
            row_cells += [""] * (len(header_cells) - len(row_cells))
        elif len(row_cells) > len(header_cells):
            row_cells = row_cells[:len(header_cells)]
        rows.append("| " + " | ".join(row_cells) + " |")
    return "\n".join([header, separator] + rows)


# ───────────────────── Post‑OCR cleanup ──────────────────────
def _cleanup_text(text: str) -> str:
    """
    Normaliza y limpia el texto OCR:
    • Normaliza Unicode a NFKC.
    • Elimina caracteres no imprimibles.
    • Convierte múltiples espacios en uno.
    • Retira líneas con muy baja proporción de caracteres alfabéticos (<30 %).

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

# ──────────────── Visualización de regiones OCR ────────────────

def visualize_ocr_regions(page: fitz.Page, output_path: str = "ocr_regions.png") -> None:
    """
    Dibuja las regiones de texto detectadas por Tesseract en la imagen de una página y guarda el resultado.

    Args:
        page (fitz.Page): Página PDF a procesar.
        output_path (str): Ruta donde guardar la imagen con las cajas dibujadas.
    """


    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))
    img = np.array(img_pil)

    # Convertir a RGB si es necesario
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    data = pytesseract.image_to_data(img, lang=OCR_LANG, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)

    n_boxes = len(data['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Guardar o mostrar la imagen
    Image.fromarray(img).save(output_path)
    logging.info(f"Regiones OCR visualizadas en: {output_path}")

# ─────────────────────── Preprocesamiento ───────────────────────

def correct_rotation(img_pil: Image.Image) -> Image.Image:
    """
    Corrige la rotación de una imagen usando detección automática vía Tesseract OSD.

    Args:
        img_pil (Image.Image): Imagen original.

    Returns:
        Image.Image: Imagen rotada si se detectó desviación de ángulo.
    """
    try:
        osd = pytesseract.image_to_osd(img_pil)
        angle = int([line for line in osd.split('\n') if 'Rotate' in line][0].split(':')[-1])
        if angle != 0:
            return img_pil.rotate(-angle, expand=True)
    except Exception:
        pass  # Si falla, seguimos con la imagen original
    return img_pil

# ───────────── Heurísticas y Detección de Tablas ────────────────


def estimate_psm_for_page(img_pil: Image.Image) -> int:
    """
    Estima automáticamente el valor de PSM (Page Segmentation Mode) para Tesseract
    según las características visuales de la imagen renderizada.

    Heurística:
        - Pocas líneas -> PSM 7 (una sola línea)
        - Muchas columnas visibles -> PSM 4 (flujo de columnas)
        - Distribución moderada -> PSM 6 (bloques uniformes)
        - Muy ruidoso o disperso -> PSM 11 (OCR general)

    Args:
        img_pil (Image.Image): Imagen renderizada de la página.

    Returns:
        int: Valor de PSM sugerido.
    """
    img = np.array(img_pil.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(255 - binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_boxes = len(contours)

    if num_boxes < 5:
        return 7
    elif num_boxes > 50:
        return 11
    elif 20 < num_boxes <= 50:
        return 4
    else:
        return 6


def has_visual_table(img_pil: Image.Image) -> bool:
    """
    Detecta si una imagen contiene una tabla visualmente, evaluando líneas horizontales/verticales.

    Args:
        img_pil (Image.Image): Imagen de la página.

    Returns:
        bool: True si se detecta estructura tabular, False si no.
    """
    img = np.array(img_pil.convert("L"))
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Detección de líneas
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=50, maxLineGap=10)
    if lines is None:
        return False

    horizontal = 0
    vertical = 0
    for x1, y1, x2, y2 in lines[:, 0]:
        if abs(y2 - y1) < 10:  # Horizontal
            horizontal += 1
        elif abs(x2 - x1) < 10:  # Vertical
            vertical += 1

    return horizontal >= 2 and vertical >= 2

# ─────────────────────── Utilidades OCR ─────────────────────────

def needs_ocr(page: fitz.Page) -> bool:
    """
    Determina si una página necesita OCR revisando si contiene texto seleccionable.

    Args:
        page (fitz.Page): Página a analizar.

    Returns:
        bool: True si no hay texto y se debe aplicar OCR.
    """
    return page.get_text("text").strip() == ""

# ────────────────── Extraer bloques visuales del layout ──────────────────
def extract_blocks(page: fitz.Page) -> list[tuple[float, float, float, float, str]]:
    """
    Extrae bloques de texto con coordenadas de la página.

    Returns:
        Lista de tuplas (x0, y0, x1, y1, texto)
    """
    blocks = page.get_text("blocks")
    return [(b[0], b[1], b[2], b[3], b[4].strip()) for b in blocks if b[4].strip()]

# ────────────── Detección y jerarquización de encabezados legales ──────────────
def detect_structured_headings(text: str) -> str:
    """
    Aplica formato Markdown a encabezados legales típicos como 'VISTOS', 'CONSIDERANDO', 'RESUELVO', 'DECRETO', etc.

    Args:
        text (str): Texto OCR limpio.

    Returns:
        str: Texto con encabezados jerarquizados en Markdown.
    """
    headings = ["VISTOS", "CONSIDERANDO", "RESUELVO", "DECRETO", "FUNDAMENTO", "TENIENDO PRESENTE", "POR TANTO"]
    for heading in headings:
        # Reemplaza solo si aparece como línea sola o seguida de dos puntos
        text = re.sub(rf"(?m)^\s*{heading}[:\s]*", f"\n### {heading}\n", text)
    return text

# ──────────────── Aplica segmentación por bloques heurística ────────────────

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
# ──────────────── Detección y formateo de listas ────────────────
# Nueva versión detect_lists al final del archivo:
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
# ──────────────── Detección y extracción de tablas visuales ────────────────


def extract_tables_from_page(page: fitz.Page) -> list[str]:
    """
    Detecta visualmente tablas en una página PDF y extrae su contenido en formato Markdown.

    Returns:
        list[str]: Lista de tablas extraídas como strings Markdown.
    """
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    img_pil = Image.open(BytesIO(pix.tobytes("png")))
    img_gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)

    # Binarización y detección de bordes
    _, binary = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Detección de líneas horizontales y verticales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    table_mask = cv2.add(detect_horizontal, detect_vertical)

    # Encontrar contornos (tablas candidatas)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tables_md = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < 100 or h < 50:
            continue  # ignora cuadros pequeños

        table_img = img_gray[y:y + h, x:x + w]
        table_pil = Image.fromarray(table_img)
        md_table = ocr_table_to_markdown(table_pil)

        if md_table.strip():
            tables_md.append(md_table.strip())

    return tables_md

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
            text = re.sub(rf"\b{re.escape(bad)}\b", good, text, flags=re.IGNORECASE)
    return text