"""
Sistema de manejo de errores centralizado.

Este módulo implementa un manejo unificado de errores y excepciones
para eliminar la inconsistencia entre diferentes módulos.
"""
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class ErrorType(Enum):
    """Tipos de errores del sistema."""
    DOCUMENT_ERROR = "document_error"
    STORAGE_ERROR = "storage_error"
    LLM_ERROR = "llm_error"
    OCR_ERROR = "ocr_error"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"


class ErrorSeverity(Enum):
    """Niveles de severidad de errores."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Contexto adicional para errores."""
    operation: Optional[str] = None
    file_path: Optional[str] = None
    user_action: Optional[str] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class BaseApplicationError(Exception):
    """Excepción base para todos los errores de la aplicación."""

    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.context = context or ErrorContext()
        self.original_exception = original_exception

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el error a un diccionario para serialización."""
        return {
            'message': self.message,
            'error_type': self.error_type.value,
            'severity': self.severity.value,
            'context': {
                'operation': self.context.operation,
                'file_path': self.context.file_path,
                'user_action': self.context.user_action,
                'timestamp': self.context.timestamp,
                'additional_data': self.context.additional_data
            },
            'original_exception': str(self.original_exception) if self.original_exception else None
        }


# Excepciones específicas del dominio
class DocumentError(BaseApplicationError):
    """Error al procesar un documento."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.DOCUMENT_ERROR,
                         ErrorSeverity.HIGH, context, original_exception)


class StorageError(BaseApplicationError):
    """Error al almacenar datos."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.STORAGE_ERROR,
                         ErrorSeverity.MEDIUM, context, original_exception)


class LLMError(BaseApplicationError):
    """Error en el procesamiento con LLM."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.LLM_ERROR,
                         ErrorSeverity.MEDIUM, context, original_exception)


class OCRError(BaseApplicationError):
    """Error en el procesamiento OCR."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.OCR_ERROR,
                         ErrorSeverity.HIGH, context, original_exception)


class ValidationError(BaseApplicationError):
    """Error de validación."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.VALIDATION_ERROR,
                         ErrorSeverity.LOW, context, original_exception)


class ConfigurationError(BaseApplicationError):
    """Error de configuración."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.CONFIGURATION_ERROR,
                         ErrorSeverity.CRITICAL, context, original_exception)


class NetworkError(BaseApplicationError):
    """Error de red."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.NETWORK_ERROR,
                         ErrorSeverity.MEDIUM, context, original_exception)


class FileError(BaseApplicationError):
    """Error de archivo."""

    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorType.FILE_ERROR,
                         ErrorSeverity.HIGH, context, original_exception)


class ErrorHandler:
    """Manejador centralizado de errores."""

    @staticmethod
    def handle_exception(
        exception: Exception,
        operation: str,
        default_message: str = "Ha ocurrido un error inesperado"
    ) -> BaseApplicationError:
        """
        Convierte excepciones genéricas en errores de aplicación específicos.

        Args:
            exception: La excepción original
            operation: La operación que se estaba realizando
            default_message: Mensaje por defecto si no se puede determinar el tipo

        Returns:
            BaseApplicationError: Error de aplicación específico
        """
        context = ErrorContext(operation=operation)

        if isinstance(exception, BaseApplicationError):
            return exception

        # Mapeo de excepciones comunes a errores específicos
        if isinstance(exception, FileNotFoundError):
            return FileError(f"Archivo no encontrado: {exception}", context, exception)
        elif isinstance(exception, PermissionError):
            return FileError(f"Sin permisos para acceder al archivo: {exception}", context, exception)
        elif isinstance(exception, ValueError):
            return ValidationError(f"Valor inválido: {exception}", context, exception)
        elif isinstance(exception, ConnectionError):
            return NetworkError(f"Error de conexión: {exception}", context, exception)
        else:
            return BaseApplicationError(
                f"{default_message}: {exception}",
                ErrorType.DOCUMENT_ERROR,
                ErrorSeverity.MEDIUM,
                context,
                exception
            )

    @staticmethod
    def format_error_message(error: BaseApplicationError) -> str:
        """
        Formatea un mensaje de error de manera consistente.

        Args:
            error: El error a formatear

        Returns:
            str: Mensaje formateado
        """
        severity_symbols = {
            ErrorSeverity.LOW: "INFO",
            ErrorSeverity.MEDIUM: "WARN",
            ErrorSeverity.HIGH: "ERROR",
            ErrorSeverity.CRITICAL: "CRITICAL"
        }

        symbol = severity_symbols.get(error.severity, "UNKNOWN")
        operation_info = f" ({error.context.operation})" if error.context.operation else ""

        return f"{symbol} {error.message}{operation_info}"
