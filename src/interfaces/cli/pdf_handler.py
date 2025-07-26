"""
PDF Handler - Gestión y selección de archivos PDF.
"""

from pathlib import Path
from typing import List, Optional
from . import PDF_DIR


def list_pdfs() -> List[str]:
    """Lista los PDFs disponibles en el directorio pdfs."""
    return [p.name for p in sorted(PDF_DIR.glob("*.pdf"))]


def select_pdf() -> Optional[str]:
    """Muestra un menú de selección de PDF."""
    files = list_pdfs()
    if not files:
        print("\n[INFO] No se encontraron PDFs en el directorio ./pdfs")
        print("[TIP] Coloca archivos PDF en el directorio 'pdfs' para procesarlos")
        return None

    print(
        f"\nPDFs disponibles ({len(files)} archivo{'s' if len(files) != 1 else ''}):")
    print("-" * 60)

    for i, pdf in enumerate(files, 1):
        # Obtener información adicional del archivo
        pdf_path = PDF_DIR / pdf
        try:
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            size_str = f"({size_mb:.1f} MB)"
        except:
            size_str = "(tamaño desconocido)"

        print(f"  {i:2d}. {pdf} {size_str}")

    print("-" * 60)

    try:
        sel = input("Seleccione un número: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(files):
            selected_file = files[int(sel) - 1]
            print(f"[OK] Seleccionado: {selected_file}")
            return selected_file
        print("[ERROR] Selección inválida")
        return None
    except (ValueError, IndexError):
        print("[ERROR] Selección inválida")
        return None


def get_pdf_info(pdf_name: str) -> dict:
    """Obtiene información detallada de un PDF específico."""
    pdf_path = PDF_DIR / pdf_name

    try:
        stat = pdf_path.stat()
        return {
            "name": pdf_name,
            "path": pdf_path,
            "size_mb": stat.st_size / (1024 * 1024),
            "exists": True,
            "readable": pdf_path.is_file()
        }
    except Exception as e:
        return {
            "name": pdf_name,
            "path": pdf_path,
            "size_mb": 0,
            "exists": False,
            "readable": False,
            "error": str(e)
        }
