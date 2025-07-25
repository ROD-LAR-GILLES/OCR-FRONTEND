#!/usr/bin/env python3
"""
Punto de entrada unificado para la aplicación OCR-FRONTEND.
Respeta la arquitectura hexagonal mediante composition root mejorado.
"""
# AÑADIR src AL PATH ANTES DE CUALQUIER IMPORT DEL PROYECTO
from src.application.composition_root import DependencyContainer, composition_root
from shared.constants.directories import Directories
from infrastructure.logging_setup import logger
import time
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Ahora podemos importar desde src


def create_cli_application():
    """
    Composition root para la aplicación CLI.
    Inyecta todas las dependencias necesarias usando el contenedor.
    """
    # Asegurar que los directorios existen
    Directories.ensure_all_exist()

    # Crear contenedor de dependencias
    container = DependencyContainer()

    # Importar y retornar la función principal
    from src.interfaces.cli import main_loop
    return main_loop


def cleanup_temp_files():
    """
    Limpia archivos temporales y directorios vacíos usando directorios centralizados.

    - Elimina archivos de progreso sin actividad reciente
    - Elimina archivos de validación huérfanos
    - Elimina directorios vacíos
    - Limpia archivos de caché antiguos
    """
    try:
        from src.shared.constants.directories import UPLOAD_DIR, CACHE_DIR
        # Directorios a revisar
        dirs_to_check = [
            Path("uploads"),
            Path("data/cache"),
            Path("logs"),
            Path("output")
        ]

        for base_dir in dirs_to_check:
            if not base_dir.exists():
                continue

            # Tiempo actual
            current_time = time.time()

            # Revisar cada subdirectorio
            for item in base_dir.iterdir():
                try:
                    if item.is_dir():
                        # Verificar si el directorio está vacío
                        files = list(item.iterdir())
                        if not files:
                            item.rmdir()
                            logger.info(f"Eliminado directorio vacío: {item}")
                            continue

                        # Verificar archivos de progreso antiguos
                        progress_file = item / "progress.json"
                        if progress_file.exists():
                            stats = progress_file.stat()
                            # Si el archivo tiene más de 24 horas sin modificarse
                            if current_time - stats.st_mtime > 86400:
                                with open(progress_file) as f:
                                    progress_data = json.load(f)
                                    # Si el proceso no está en progreso o tiene error
                                    if progress_data.get("status") in ["error", "completed", None]:
                                        progress_file.unlink()
                                        logger.info(
                                            f"Eliminado archivo de progreso antiguo: {progress_file}")

                        # Verificar archivos de validación huérfanos
                        validation_file = item / "validation.json"
                        if validation_file.exists() and not (item / "document.pdf").exists():
                            validation_file.unlink()
                            logger.info(
                                f"Eliminado archivo de validación huérfano: {validation_file}")

                    elif item.is_file() and base_dir.name == "cache":
                        # Eliminar archivos de caché antiguos (más de 7 días)
                        if current_time - item.stat().st_mtime > 604800:
                            item.unlink()
                            logger.info(
                                f"Eliminado archivo de caché antiguo: {item}")

                except Exception as e:
                    logger.error(f"Error procesando {item}: {e}")

    except Exception as e:
        logger.error(f"Error en limpieza de archivos temporales: {e}")


def main():
    """Punto de entrada principal."""
    try:
        # Limpiar archivos temporales al inicio
        print(" Limpiando archivos temporales...")
        cleanup_temp_files()

        print(" Iniciando aplicación CLI...")
        cli_app = create_cli_application()
        cli_app()

    except KeyboardInterrupt:
        print("\n\n Aplicación terminada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f" Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
