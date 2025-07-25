# src/config/state.py
from dotenv import load_dotenv

"""
Estado global compartido para el modo LLM.

Valores posibles:
    • "off"    → desactiva LLM
    • "prompt" → usa prompt directo
"""
# Se ejecuta una sola vez al importar `config.state`
load_dotenv()

LLM_MODE = "prompt"