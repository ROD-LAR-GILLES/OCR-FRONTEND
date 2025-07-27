"""
Excepciones específicas del dominio.

NOTA: Este módulo está obsoleto y se mantiene por compatibilidad. 
Usar shared.utils.error_handling para manejar errores.

Este módulo define excepciones personalizadas que representan errores
específicos del dominio, permitiendo un manejo más preciso de los
diferentes tipos de errores que pueden ocurrir durante la ejecución.
"""

from shared.utils.error_handling import (
    DocumentError, StorageError, LLMError,
    OCRError, ValidationError, ConfigurationError,
    NetworkError, FileError
)

# Las clases importadas de shared.utils.error_handling proporcionan
# implementaciones mejoradas con contexto y severidad
