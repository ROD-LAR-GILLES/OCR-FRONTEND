import sys
from pathlib import Path

from loguru import logger

from config import config
from interfaces import main_loop


def main() -> None:
    """
    Punto de entrada de la aplicación OCR-PYMUPDF.

    Configura el sistema de logging y la aplicación.
    Proporciona modo interactivo (CLI) y no interactivo (línea de comandos).
    """
    # Configuración inicial
    _setup_logging()
    _ensure_directories()

    # ─── Modo no interactivo ───
    if len(sys.argv) > 1:
        _run_non_interactive_mode()
        return  # Salir sin mostrar menú

    try:
        # Mostrar información de inicialización
        _show_startup_info()

        # Iniciar modo interactivo
        main_loop()
    except KeyboardInterrupt:
        print("\n\n[INFO] Programa interrumpido por el usuario")
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Ocurrió un problema. Revisa ocr.json para más detalles")


def _setup_logging() -> None:
    """Configura el sistema de logging."""
    logger.remove()  # Eliminar handler por defecto

    # Log en formato JSON para análisis
    logger.add(
        "logs/ocr.json",
        serialize=True,
        rotation="10 MB",
        retention="1 month",
        level="INFO"
    )

    # Log en formato legible para depuración
    logger.add(
        "logs/debug.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="5 MB",
        retention="1 week",
        level="DEBUG"
    )

    # Log de errores críticos
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 MB",
        retention="1 month",
        level="ERROR"
    )


def _ensure_directories() -> None:
    """Asegura que existan los directorios necesarios."""
    # Crear directorios base
    Path("pdfs").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # Asegurar estructura de datos
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    (data_path / "cache").mkdir(exist_ok=True)  # Cache dentro de data/


def _run_non_interactive_mode() -> None:
    """Ejecuta el modo no interactivo para procesar un PDF desde la línea de comandos."""
    from domain.use_cases.pdf_to_markdown import PDFToMarkdownUseCase
    from infrastructure.storage_adapter import StorageAdapter

    pdf_arg = Path(sys.argv[1])
    if not pdf_arg.exists():
        print(f"[ERROR] El archivo {pdf_arg} no existe")
        return

    try:
        print(f"[INFO] Procesando {pdf_arg}")
        # Usar el caso de uso en lugar de llamar directamente al adaptador
        storage_adapter = StorageAdapter()

        # TODO: Implementar DocumentPort y LLMPort adecuados
        pdf_to_markdown_use_case = PDFToMarkdownUseCase(
            document_port=None,
            storage_port=storage_adapter,
            llm_port=None
        )

        # Por ahora, usamos el adaptador directamente
        from adapters.pymupdf_adapter import extract_markdown
        markdown_content = extract_markdown(pdf_arg)
        output_path = storage_adapter.save_markdown(
            pdf_arg.stem, markdown_content)

        print(f"[OK] Markdown generado: {output_path}")
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Falló la conversión a Markdown.")


def _show_startup_info() -> None:
    """Muestra información de inicialización."""
    import platform
    from datetime import datetime

    print("\n=== OCR-FRONTEND ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Modo LLM: {config.llm_mode}")
    print(f"Proveedor LLM: {config.llm_provider or 'Ninguno'}")
    print("===================\n")


if __name__ == "__main__":
    main()
