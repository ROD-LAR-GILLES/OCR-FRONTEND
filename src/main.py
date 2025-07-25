from loguru import logger
from interfaces.cli_menu import mostrar_menu
import sys

def main() -> None:
    """
    Punto de entrada de la aplicación OCR-PYMUPDF.
    
    Configura el sistema de logging para:
    - Eliminar el handler por defecto de Loguru
    - Añadir handler para escribir en ocr.json en formato JSON
    - Rotar archivo cada 10 MB
    
    Invoca el menú interactivo CLI.
    """
    # Configuración logging 
    logger.remove()
    logger.add(
        "ocr.json",
        serialize=True,
        rotation="10 MB"
    )
    
    # ─── Modo no interactivo ───
    if len(sys.argv) > 1:
        from pathlib import Path
        from domain.use_cases import convert_pdf_to_md

        pdf_arg = Path(sys.argv[1])
        if not pdf_arg.exists():
            print(f"[ERROR] El archivo {pdf_arg} no existe")
            return

        try:
            md_path = convert_pdf_to_md(pdf_arg)
            print(f"[OK] Markdown generado: {md_path}")
        except Exception as exc:
            logger.exception(exc)
            print("[ERROR] Falló la conversión a Markdown.")
        return  # Salir sin mostrar menú
        
    try:
        mostrar_menu()
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr.json")


if __name__ == "__main__":
    main()
