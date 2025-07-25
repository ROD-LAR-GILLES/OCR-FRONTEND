"""
Excepciones específicas del dominio.

Este módulo define excepciones personalizadas que representan errores
específicos del dominio, permitiendo un manejo más preciso de los
diferentes tipos de errores que pueden ocurrir durante la ejecución.
"""


class DocumentError(Exception):
    """Error al procesar un documento."""
    pass


class StorageError(Exception):
    """Error al almacenar datos."""
    pass


class LLMError(Exception):
    """Error en el procesamiento con LLM."""
    pass
