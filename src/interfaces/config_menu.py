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

            print("\n=== Configuración de LLM ===")
            print(f"Proveedor actual: {current_provider or 'Ninguno'}")
            print(f"Modo actual: {current_mode or 'Desactivado'}")
            print("\nOpciones:")
            print("1. Cambiar proveedor LLM")
            print("2. Cambiar modo LLM")
            print("3. Configurar API keys")
            print("0. Volver al menú principal")

            choice = input("\nSeleccione una opción (0-3): ").strip()

            if choice == "0":
                break
            elif choice == "1":
                cls._change_provider()
            elif choice == "2":
                cls._change_mode()
            elif choice == "3":
                cls._configure_api_keys()
            else:
                print("Opción inválida. Inténtelo de nuevo.")

    @classmethod
    def _change_provider(cls) -> None:
        """Cambia el proveedor LLM."""
        print("\n=== Cambiar Proveedor LLM ===")
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
        print("\n=== Cambiar Modo LLM ===")
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

    @classmethod
    def _configure_api_keys(cls) -> None:
        """Configura las claves API para los proveedores LLM."""
        print("\n=== Configurar API Keys ===")
        print("1. OpenAI API Key")
        print("2. Google Gemini API Key")
        print("0. Volver")

        choice = input("\nSeleccione una opción: ").strip()

        try:
            if choice == "1":
                key = input("OpenAI API Key: ").strip()
                if key:
                    config.openai_api_key = key
                    print("API Key de OpenAI actualizada.")
            elif choice == "2":
                key = input("Google Gemini API Key: ").strip()
                if key:
                    config.gemini_api_key = key
                    print("API Key de Google Gemini actualizada.")
            elif choice != "0":
                print("Opción inválida.")
        except Exception as e:
            logger.error(f"Error configurando API key: {e}")
            print(f"\nError al configurar API key. Consulte los logs para más detalles.")
