"""Configuration menu for LLM settings."""
from typing import Dict, Any
from config.llm_config import LLMConfig
from config.api_settings import load_api_settings
from infrastructure.logging_setup import logger

class ConfigMenu:
    """Handles LLM configuration through interactive menu."""
    
    PROVIDERS = {
        "1": ("No LLM Processing", None),
        "2": ("OpenAI GPT", "openai"),
        "3": ("Google Gemini", "gemini")
    }
    
    @classmethod
    def show_provider_menu(cls) -> None:
        """Display and handle LLM provider selection menu."""
        while True:
            current = LLMConfig.get_current_provider()
            print("\n=== LLM Provider Configuration ===")
            print(f"Current provider: {current or 'No LLM Processing'}")
            print("\nAvailable providers:")
            
            for key, (name, _) in cls.PROVIDERS.items():
                print(f"{key}. {name}")
            print("0. Return to main menu")
            
            choice = input("\nSelect provider (0-3): ").strip()
            
            if choice == "0":
                break
                
            if choice in cls.PROVIDERS:
                name, provider = cls.PROVIDERS[choice]
                print(f"\nSetting provider to: {name}")
                LLMConfig.set_provider(provider)
                
                if provider:
                    cls._configure_provider(provider)
            else:
                print("Invalid option. Please try again.")
    
    @classmethod
    def _configure_provider(cls, provider: str) -> None:
        """Configure specific provider settings.
        
        Args:
            provider: The provider to configure
        """
        try:
            settings = load_api_settings()[provider]
            current_config = LLMConfig.load_config()
            
            print(f"\n=== {provider.upper()} Configuration ===")
            
            # Show current settings
            print("\nCurrent settings:")
            for key, value in settings.items():
                # Mask API keys
                display_value = "****" if "api_key" in key else value
                print(f"{key}: {display_value}")
            
            # Only show advanced configuration if requested
            if input("\nConfigure advanced settings? (y/n): ").lower() == 'y':
                new_settings = {}
                for key, default in settings.items():
                    if "api_key" not in key:  # Don't modify API keys here
                        value = input(f"{key} [{default}]: ").strip()
                        new_settings[key] = value if value else default
                
                # Update config with new settings
                current_config["settings"] = new_settings
                LLMConfig.save_config(current_config)
                print("\nSettings updated successfully")
            
        except Exception as e:
            logger.error(f"Error configuring {provider}: {e}")
            print(f"\nError configuring {provider}. Check logs for details.")
