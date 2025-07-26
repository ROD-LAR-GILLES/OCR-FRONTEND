"""Menú de configuración para ajustes de LLM."""
from typing import Dict, Any

from config import config
from infrastructure.logging_setup import logger


class ConfigMenu:
    """Gestiona la configuración de LLM a través de un menú interactivo."""

    PROVIDERS = {
        "1": ("Sin procesamiento LLM", "off"),
        "2": ("OpenAI GPT", "openai"),
        "3": ("Google Gemini", "gemini"),
        "4": ("Automático (mejor disponible)", "auto")
    }

    MODES = {
        "1": ("Desactivado", "off"),
        "2": ("Sólo resumen", "summary"),
        "3": ("Mejora completa", "full"),
        "4": ("Análisis legal", "legal")
    }

    @classmethod
    def show_provider_menu(cls) -> None:
        """Muestra y gestiona el menú de selección de proveedor LLM."""
        while True:
            current_provider = config.llm_provider
            current_mode = config.llm_mode

            print("\n=== Opción 2. Configuración de LLM ===")
            print(f"Proveedor actual: {current_provider or 'Ninguno'}")
            print(f"Modo actual: {current_mode or 'Desactivado'}")
            print("\nOpciones:")
            print("2.1. Cambiar proveedor LLM")
            print("2.2. Cambiar modo LLM")
            print("2.0. Volver al menú principal")

            choice = input("\nSeleccione una opción (2.0-2.2): ").strip()

            if choice == "2.0":
                break
            elif choice == "2.1":
                cls._change_provider()
            elif choice == "2.2":
                cls._change_mode()
            else:
                print("[ERROR] Opción inválida. Inténtelo de nuevo.")

    @classmethod
    def _change_provider(cls) -> None:
        """Cambia el proveedor LLM."""
        print("\n=== Opción 2.1. Cambiar Proveedor LLM ===")
        print("Proveedores disponibles:")

        for key, (name, _) in cls.PROVIDERS.items():
            print(f"{key}. {name}")

        choice = input("\nSeleccione un proveedor: ").strip()

        if choice in cls.PROVIDERS:
            _, provider = cls.PROVIDERS[choice]
            config.llm_provider = provider
            print(f"\nProveedor establecido a: {provider}")
        else:
            print("Opción inválida.")

    @classmethod
    def _change_mode(cls) -> None:
        """Cambia el modo de operación LLM."""
        print("\n=== Opción 2.2. Cambiar Modo LLM ===")
        print("Modos disponibles:")

        for key, (name, _) in cls.MODES.items():
            print(f"{key}. {name}")

        choice = input("\nSeleccione un modo: ").strip()

        if choice in cls.MODES:
            _, mode = cls.MODES[choice]
            config.llm_mode = mode
            print(f"\nModo establecido a: {mode}")
        else:
            print("Opción inválida.")
