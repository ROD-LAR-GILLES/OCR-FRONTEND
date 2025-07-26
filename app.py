#!/usr/bin/env python3
"""
Punto de entrada unificado para la aplicación OCR-FRONTEND.
Respeta la arquitectura hexagonal mediante composition root.
"""
import sys
from pathlib import Path
import argparse

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def create_cli_application():
    """
    Composition root para la aplicación CLI.
    Inyecta todas las dependencias necesarias.
    """
    from interfaces.cli_menu import main_loop
    return main_loop


def create_api_application():
    """
    Composition root para la aplicación API REST.
    Inyecta todas las dependencias necesarias.
    """
    from interfaces.api_rest import start_api
    return start_api


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
