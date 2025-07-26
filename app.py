#!/usr/bin/env python3
"""
Punto de entrada unificado para la aplicación OCR-FRONTEND.
Respeta la arquitectura hexagonal mediante composition root mejorado.
"""
import sys
import time
from pathlib import Path
import argparse
import json

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar después de configurar el path
from infrastructure.logging_setup import logger
from shared.constants.directories import Directories
from application.composition_root import DependencyContainer


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
    from interfaces.cli import main_loop
    return main_loop


def create_api_application():
    """
    Composition root para la aplicación API REST.
    Inyecta todas las dependencias necesarias usando el contenedor.
    """
    # Asegurar que los directorios existen
    Directories.ensure_all_exist()
    
    # Crear contenedor de dependencias
    container = DependencyContainer()
    
    # Importar función de inicio API
    from interfaces.api_rest import start_api
    return start_api


def cleanup_temp_files():
    """
    Limpia archivos temporales y directorios vacíos usando directorios centralizados.

    - Elimina archivos de progreso sin actividad reciente
    - Elimina archivos de validación huérfanos
    - Elimina directorios vacíos
    - Limpia archivos de caché antiguos
    """
    try:
        from shared.constants.directories import UPLOAD_DIR, CACHE_DIR
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
    """Punto de entrada principal con selección de modo."""
    parser = argparse.ArgumentParser(
        description="OCR-FRONTEND: Sistema de procesamiento OCR con arquitectura hexagonal"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Modo de ejecución: cli (interfaz de línea de comandos) o api (servidor REST)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para el servidor API (solo en modo api)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto para el servidor API (solo en modo api)"
    )

    args = parser.parse_args()

    try:
        # Limpiar archivos temporales al inicio
        print(" Limpiando archivos temporales...")
        cleanup_temp_files()

        if args.mode == "cli":
            print(" Iniciando aplicación CLI...")
            cli_app = create_cli_application()
            cli_app()
        elif args.mode == "api":
            print(f" Iniciando servidor API en {args.host}:{args.port}...")
            api_app = create_api_application()
            api_app(host=args.host, port=args.port)

    except KeyboardInterrupt:
        print("\n\n Aplicación terminada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f" Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
