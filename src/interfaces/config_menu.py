"""Menú de configuración para ajustes de LLM."""
from typing import Dict, Any

from shared.util.config import config
from infrastructure.logging_setup import logger
from application.configuration_service import ConfigurationService


class ConfigMenu:
    """Gestiona la configuración de LLM a través de un menú interactivo."""

    def __init__(self):
        self.config_service = ConfigurationService()

    PROVIDERS = {
        "1": ("Sin procesamiento LLM", "off"),
        "2": ("OpenAI GPT", "openai"),
        "3": ("Google Gemini", "gemini"),
        "4": ("Automático (mejor disponible)", "auto"),
        "5": ("Volver", None)
    }

    MODES = {
        "1": ("Desactivado", "off"),
        "2": ("Sólo resumen", "summary"),
        "3": ("Mejora completa", "full"),
        "4": ("Análisis legal", "legal"),
        "5": ("Volver", None)
    }

    @classmethod
    def show_provider_menu(cls) -> None:
        """Muestra y gestiona el menú de selección de proveedor LLM."""
        instance = cls()
        instance._show_provider_menu()

    def _show_provider_menu(self) -> None:
        """Implementación interna del menú de proveedor."""
        while True:
            llm_config = self.config_service.get_llm_configuration()
            current_provider = llm_config.get('provider', 'Ninguno')
            current_mode = llm_config.get('mode', 'Desactivado')

            print("\n=== Opción 2. Configuración de LLM ===")
            print(f"Proveedor actual: {current_provider}")
            print(f"Modo actual: {current_mode}")
            print("\nOpciones:")
            print("1. Cambiar proveedor LLM")
            print("2. Cambiar modo LLM")
            print("3. Volver al menú principal")

            choice = input("\nSeleccione una opción (1-3): ").strip()

            if choice == "3":
                break
            elif choice == "1":
                self._change_provider()
            elif choice == "2":
                self._change_mode()
            else:
                print("[ERROR] Opción inválida. Inténtelo de nuevo.")

    def _change_provider(self) -> None:
        """Cambia el proveedor LLM."""
        print("\n=== Opción 1. Cambiar Proveedor LLM ===")
        print("Proveedores disponibles:")

        for key, (name, _) in self.PROVIDERS.items():
            print(f"{key}. {name}")

        choice = input("\nSeleccione un proveedor (1-5): ").strip()

        if choice == "5":
            return
        elif choice in self.PROVIDERS:
            _, provider = self.PROVIDERS[choice]
            if provider:  # Ignorar None para la opción Volver
                try:
                    # Usar el servicio de configuración para actualizar el proveedor
                    provider_config = config.get_llm_provider_config(
                        provider) if provider != "off" else {}
                    self.config_service.update_llm_provider(
                        provider, provider_config)
                    print(f"\nProveedor establecido a: {provider}")
                except Exception as e:
                    print(f"[ERROR] No se pudo configurar el proveedor: {e}")
        else:
            print("[ERROR] Opción inválida.")

    def _change_mode(self) -> None:
        """Cambia el modo de operación LLM."""
        print("\n=== Opción 2. Cambiar Modo LLM ===")
        print("Modos disponibles:")

        for key, (name, _) in self.MODES.items():
            print(f"{key}. {name}")
        print("5. Volver")

        choice = input("\nSeleccione un modo (1-5): ").strip()

        if choice == "5":
            return
        elif choice in self.MODES:
            _, mode = self.MODES[choice]
            if mode:  # Ignorar None para la opción Volver
                try:
                    # Usar el servicio de configuración para actualizar el modo
                    current_config = self.config_service.get_llm_configuration()
                    provider = current_config.get('provider', 'off')
                    provider_config = config.get_llm_provider_config(
                        provider) if provider != "off" else {}
                    provider_config['mode'] = mode
                    self.config_service.update_llm_provider(
                        provider, provider_config)
                    print(f"\nModo establecido a: {mode}")
                except Exception as e:
                    print(f"[ERROR] No se pudo configurar el modo: {e}")
        else:
            print("[ERROR] Opción inválida.")
