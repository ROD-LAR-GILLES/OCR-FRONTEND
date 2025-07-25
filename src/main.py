import sys
from pathlib import Path

from loguru import logger

from shared.util.config import config
from shared.constants.directories import Directories
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
        "src/shared/storage/logs/ocr.json",
        serialize=True,
        rotation="10 MB",
        retention="1 month",
        level="INFO"
    )

    # Log en formato legible para depuración
    logger.add(
        "src/shared/storage/logs/debug.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="5 MB",
        retention="1 week",
        level="DEBUG"
    )

    # Log de errores críticos
    logger.add(
        "src/shared/storage/logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 MB",
        retention="1 month",
        level="ERROR"
    )


def _ensure_directories() -> None:
    """Asegura que existan los directorios necesarios."""
    # Usar el método centralizado para crear todos los directorios
    Directories.ensure_all_exist()


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
        from adapters.document_processing import extract_markdown
        markdown_content = extract_markdown(pdf_arg)
        output_path = storage_adapter.save_markdown(
            pdf_arg.stem, markdown_content)

        print(f"[OK] Markdown generado: {output_path}")
    except Exception as exc:
        logger.exception(exc)
        print("[ERROR] Falló la conversión a Markdown.")


def _show_startup_info() -> None:
    """Muestra información de inicialización."""
    # Función vacía para mantener compatibilidad con el código existente
    pass


if __name__ == "__main__":
    main()
