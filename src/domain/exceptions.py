"""Excepciones del dominio para casos de uso."""

class DocumentError(Exception):
    """Error al procesar un documento."""
    pass

class StorageError(Exception):
    """Error al almacenar datos."""
    pass

class LLMError(Exception):
    """Error en el procesamiento con LLM."""
    pass
