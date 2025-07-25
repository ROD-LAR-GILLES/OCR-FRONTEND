# src/config/state.py
from dotenv import load_dotenv
import os

"""
Estado global compartido para la configuración del LLM.

LLM_MODE:
    • "off"    → desactiva LLM
    • "prompt" → usa prompt directo
    • "ft"     → usa modelo fine-tuned
    • "auto"   → selecciona automáticamente

LLM_PROVIDER:
    • "openai"  → usa OpenAI API
    • "gemini"  → usa Google Gemini API
    • None      → selecciona automáticamente según claves disponibles
"""
# Se ejecuta una sola vez al importar `config.state`
load_dotenv()

# Configuración del modo LLM (desde .env o valor por defecto)
LLM_MODE = os.getenv("LLM_MODE", "prompt")

# Proveedor LLM a utilizar (desde .env o automático)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", None)