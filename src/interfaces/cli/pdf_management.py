"""
PDF Management - Gestión consolidada de archivos PDF.

Este módulo consolida todas las operaciones relacionadas con PDFs,
incluyendo listado, selección, validación y metadatos.
"""
try:
    import fitz
except ImportError:
    fitz = None

from pathlib import Path
from typing import List, Optional, Dict, Any
from shared.constants.directories import PDF_DIR
from infrastructure.logging_setup import logger


class PDFManager:
    """Gestor consolidado para operaciones con archivos PDF."""

    def __init__(self):
        self.pdf_dir = PDF_DIR
        self.pdf_dir.mkdir(exist_ok=True)

    def list_pdfs(self) -> List[str]:
        """Lista los PDFs disponibles en el directorio pdfs."""
        try:
            return [p.name for p in sorted(self.pdf_dir.glob("*.pdf"))]
        except Exception as e:
            logger.error(f"Error listando PDFs: {e}")
            return []

    def select_pdf(self) -> Optional[str]:
        """Muestra un menú de selección de PDF."""
        pdfs = self.list_pdfs()

        if not pdfs:
            print("\n[INFO] No hay archivos PDF en el directorio 'pdfs'")
            return None

        print("\nArchivos PDF disponibles:")
        for i, pdf in enumerate(pdfs, 1):
            info = self.get_pdf_info(pdf)
            size_info = f"({info['size_mb']:.1f} MB)" if info['exists'] else "(Error)"
            print(f"{i}. {pdf} {size_info}")

        try:
            choice = int(input(f"\nSeleccione un archivo (1-{len(pdfs)}): "))
            if 1 <= choice <= len(pdfs):
                return pdfs[choice - 1]
            else:
                print("[ERROR] Número fuera de rango")
                return None
        except ValueError:
            print("[ERROR] Entrada inválida")
            return None

    def get_pdf_info(self, pdf_name: str) -> Dict[str, Any]:
        """Obtiene información detallada de un PDF específico."""
        pdf_path = self.pdf_dir / pdf_name

        try:
            stat = pdf_path.stat()

            # Información básica del archivo
            info = {
                "name": pdf_name,
                "path": pdf_path,
                "size_mb": stat.st_size / (1024 * 1024),
                "exists": True,
                "readable": pdf_path.is_file(),
                "error": None
            }

            # Información del documento PDF si está disponible
            if fitz:
                try:
                    with fitz.open(pdf_path) as doc:
                        info.update({
                            "page_count": len(doc),
                            "title": doc.metadata.get("title", ""),
                            "author": doc.metadata.get("author", ""),
                            "subject": doc.metadata.get("subject", ""),
                            "creator": doc.metadata.get("creator", ""),
                            "is_encrypted": doc.needs_pass,
                            # Verificar primeras 3 páginas
                            "has_text": any(page.get_text() for page in doc[:3])
                        })
                except Exception as e:
                    info["pdf_error"] = f"Error leyendo PDF: {e}"

            return info

        except Exception as e:
            return {
                "name": pdf_name,
                "path": pdf_path,
                "size_mb": 0,
                "exists": False,
                "readable": False,
                "error": str(e)
            }

    def validate_pdf_accessibility(self, pdf_name: str) -> Dict[str, bool]:
        """Valida que un PDF sea accesible y procesable."""
        pdf_path = self.pdf_dir / pdf_name
        validation = {
            "exists": False,
            "readable": False,
            "valid_pdf": False,
            "not_encrypted": False,
            "has_content": False
        }

        try:
            validation["exists"] = pdf_path.exists()
            validation["readable"] = pdf_path.is_file()

            if validation["readable"] and fitz:
                with fitz.open(pdf_path) as doc:
                    validation["valid_pdf"] = True
                    validation["not_encrypted"] = not doc.needs_pass
                    validation["has_content"] = len(doc) > 0

        except Exception as e:
            logger.warning(f"Error validando PDF {pdf_name}: {e}")

        return validation

    def get_directory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del directorio de PDFs."""
        pdfs = self.list_pdfs()
        total_size = 0
        valid_pdfs = 0

        for pdf in pdfs:
            info = self.get_pdf_info(pdf)
            if info['exists']:
                total_size += info['size_mb']
                if info.get('page_count', 0) > 0:
                    valid_pdfs += 1

        return {
            "total_files": len(pdfs),
            "valid_pdfs": valid_pdfs,
            "total_size_mb": total_size,
            "directory_path": str(self.pdf_dir)
        }


# Instancia global para compatibilidad hacia atrás
pdf_manager = PDFManager()

# Funciones de compatibilidad hacia atrás


def list_pdfs() -> List[str]:
    """Lista los PDFs disponibles (función de compatibilidad)."""
    return pdf_manager.list_pdfs()


def select_pdf() -> Optional[str]:
    """Selecciona un PDF del menú (función de compatibilidad)."""
    return pdf_manager.select_pdf()


def get_pdf_info(pdf_name: str) -> Dict[str, Any]:
    """Obtiene información de un PDF (función de compatibilidad)."""
    return pdf_manager.get_pdf_info(pdf_name)


__all__ = [
    'PDFManager', 'pdf_manager',
    'list_pdfs', 'select_pdf', 'get_pdf_info'
]
