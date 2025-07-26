"""
OCR-FRONTEND - Documentación de Arquitectura

Este documento describe la nueva arquitectura refactorizada del sistema OCR-FRONTEND,
que implementa una arquitectura hexagonal limpia y centralizada.

## Estructura del Proyecto

```
src/
├── application/           # Capa de aplicación
│   ├── composition_root.py   # Inyección de dependencias
│   ├── services/            # Servicios de aplicación
│   │   └── configuration_service.py
│   └── use_cases/           # Casos de uso del dominio
│       ├── pdf_to_markdown.py
│       └── validate_pdf.py
│
├── domain/                # Capa de dominio (núcleo del negocio)
│   ├── entities/          # Entidades del dominio
│   ├── ports/             # Interfaces (puertos)
│   ├── use_cases/         # Casos de uso principales
│   └── value_objects/     # Objetos de valor
│
├── infrastructure/       # Capa de infraestructura
│   ├── document_adapter.py
│   ├── storage_adapter.py
│   ├── logging_setup.py
│   └── ocr_cache.py
│
├── adapters/             # Adaptadores externos
│   ├── pymupdf_adapter.py
│   ├── llm_refiner.py
│   └── ocr/
│
├── interfaces/           # Capa de interfaces (UI/API)
│   ├── cli/              # Interfaz de línea de comandos
│   │   ├── menu.py       # Menú principal
│   │   ├── pdf_management.py  # Gestión consolidada de PDFs
│   │   ├── processing.py # Procesamiento de documentos
│   │   └── utils.py      # Utilidades consolidadas
│   └── api/              # API REST
│
└── shared/               # Componentes compartidos
    ├── constants/        # Constantes centralizadas
    │   ├── config.py     # Configuración unificada
    │   └── directories.py # Directorios centralizados
    └── utils/            # Utilidades compartidas
        └── error_handling.py # Sistema de errores centralizado
```

## Principios Arquitectónicos Implementados

### 1. Arquitectura Hexagonal (Ports & Adapters)

- **Dominio**: Lógica de negocio pura, sin dependencias externas
- **Aplicación**: Casos de uso y servicios de aplicación
- **Infraestructura**: Implementaciones técnicas
- **Interfaces**: UI, API, CLI

### 2. Inyección de Dependencias

- `DependencyContainer` centraliza la creación de objetos
- Composición root en `app.py`
- Interfaces abstraen implementaciones

### 3. Configuración Centralizada

- `shared.constants.config` unifica toda la configuración
- Sistema de configuración inmutable con dataclasses
- Validación de configuración integrada

### 4. Gestión de Errores Consistente

- Excepciones tipadas por dominio
- Contexto de error estructurado
- Manejo centralizado en `shared.utils.error_handling`

### 5. Directorios Centralizados

- `shared.constants.directories` elimina duplicación
- Método `ensure_all_exist()` para inicialización
- Compatibilidad hacia atrás con alias

## Beneficios de la Refactorización

### ✅ Problemas Resueltos

1. **Duplicación de Código**: Eliminada mediante centralización
2. **Configuración Fragmentada**: Unificada en un solo lugar
3. **Manejo de Errores Inconsistente**: Estandarizado
4. **Dependencias Circulares**: Resueltas con inyección de dependencias
5. **Archivos Excesivamente Pequeños**: Consolidados
6. **Responsabilidades Mixtas**: Separadas por capas

### 🚀 Mejoras Implementadas

1. **Testabilidad**: Inyección de dependencias facilita testing
2. **Mantenibilidad**: Código organizado y responsabilidades claras
3. **Extensibilidad**: Nuevas características fáciles de agregar
4. **Robustez**: Manejo de errores mejorado
5. **Configurabilidad**: Sistema de configuración flexible

## Patrones de Diseño Utilizados

### Composition Root

```python
# app.py
container = DependencyContainer()
use_case = container.get_pdf_to_markdown_use_case()
```

### Repository Pattern (Ports)

```python
# domain/ports/document_port.py
class DocumentPort(ABC):
    @abstractmethod
    def extract_content(self, pdf_path: Path) -> str:
        pass
```

### Service Layer

```python
# application/services/configuration_service.py
class ConfigurationService:
    def update_llm_provider(self, provider: str, settings: Dict[str, Any]):
        # Lógica de configuración
```

### Error Handling Strategy

```python
# shared/utils/error_handling.py
class DocumentError(BaseApplicationError):
    # Errores específicos del dominio
```

## Guías de Uso

### Agregar Nueva Funcionalidad

1. Definir caso de uso en `application/use_cases/`
2. Crear puerto si necesita infraestructura
3. Implementar adaptador en `adapters/` o `infrastructure/`
4. Registrar en `DependencyContainer`
5. Exponer en interfaz apropiada (`cli/` o `api/`)

### Configurar Nueva Opción

1. Agregar al dataclass apropiado en `shared/constants/config.py`
2. Actualizar `ConfigurationService` si es necesario
3. Agregar validación en `AppConfig.validate_configuration()`

### Manejar Nuevo Tipo de Error

1. Crear excepción en `shared/utils/error_handling.py`
2. Definir `ErrorType` apropiado
3. Usar en código con contexto adecuado

## Migración de Código Existente

### Antes (Problemático)

```python
# Configuración directa
from config import config
config.llm_provider = "openai"  # Mutación directa

# Paths duplicados
PDF_DIR = Path("pdfs")  # Repetido en múltiples archivos

# Errores inconsistentes
print("[ERROR] Algo salió mal")  # Sin contexto
```

### Después (Mejorado)

```python
# Configuración centralizada
from application.composition_root import DependencyContainer
container = DependencyContainer()
service = container.configuration_service
service.update_llm_provider("openai", config_dict)

# Directorios centralizados
from shared.constants.directories import PDF_DIR

# Errores estructurados
from shared.utils.error_handling import DocumentError, ErrorContext
context = ErrorContext(operation="pdf_processing", file_path=str(pdf_path))
raise DocumentError("Error procesando PDF", context)
```

## Estado Actual del Refactoring

### ✅ Completado

- [x] Configuración centralizada
- [x] Directorios centralizados
- [x] Inyección de dependencias
- [x] Consolidación de archivos CLI
- [x] Sistema de errores unificado
- [x] Eliminación de código duplicado
- [x] Arquitectura hexagonal básica

### 🔄 En Progreso

- [ ] Testing exhaustivo de integración
- [ ] Documentación de API
- [ ] Optimización de performance

### 📋 Pendiente (Opcional)

- [ ] Implementar caché distribuido
- [ ] Métricas de monitoreo
- [ ] Configuración por variables de entorno
- [ ] Docker optimizado

## Conclusión

Esta refactorización transforma OCR-FRONTEND de un sistema con múltiples problemas
arquitectónicos a una aplicación bien estructurada, mantenible y extensible que
sigue las mejores prácticas de desarrollo de software.

La nueva arquitectura facilita el desarrollo futuro, mejora la testabilidad,
y proporciona una base sólida para el crecimiento del sistema.
"""
