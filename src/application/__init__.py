"""
Capa de aplicación.

Esta capa contiene la lógica de aplicación y orquestación de casos de uso,
manteniendo separada la lógica de negocio pura (dominio) de los detalles
de implementación (infraestructura).
"""

# Importar composition root y contenedor de dependencias
from .composition_root import CompositionRoot, DependencyContainer, composition_root, container

# Importar servicios
from .configuration_service import ConfigurationService, configuration_service

# Importar casos de uso
from .pdf_use_cases import PDFToMarkdownUseCase, ValidatePDFUseCase, UseCase, UseCaseFactory

# Exportar componentes públicos
__all__ = [
    # Composition Root y contenedor
    'CompositionRoot',
    'DependencyContainer',
    'composition_root',
    'container',

    # Servicios
    'ConfigurationService',
    'configuration_service',

    # Casos de uso
    'PDFToMarkdownUseCase',
    'ValidatePDFUseCase',
    'UseCase',
    'UseCaseFactory'
]
