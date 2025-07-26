"""
Capa de aplicación.

Esta capa contiene la lógica de aplicación y orquestación de casos de uso,
manteniendo separada la lógica de negocio pura (dominio) de los detalles
de implementación (infraestructura).
"""

from .composition_root import CompositionRoot, DependencyContainer, composition_root
from .services import ConfigurationService, configuration_service
from .use_cases import PDFToMarkdownUseCase, ValidatePDFUseCase

__all__ = [
    # Composition Root
    'CompositionRoot',
    'DependencyContainer',
    'composition_root',

    # Servicios
    'ConfigurationService',
    'configuration_service',

    # Casos de uso
    'PDFToMarkdownUseCase',
    'ValidatePDFUseCase'
]
