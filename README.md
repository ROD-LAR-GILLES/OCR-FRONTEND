# OCR-FRONTEND

Sistema OCR avanzado con arquitectura hexagonal para procesamiento de documentos PDF a Markdown.

## Arquitectura

El proyecto implementa una **arquitectura hexagonal (ports & adapters)** limpia con las siguientes capas:

- **Dominio**: Lógica de negocio pura
- **Aplicación**: Casos de uso y servicios
- **Adaptadores**: Integraciones externas
- **Infraestructura**: Implementaciones técnicas
- **Interfaces**: CLI

### Estructura del Proyecto

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
├── interfaces/           # Capa de interfaces (CLI)
│   └── cli/              # Interfaz de línea de comandos
│       ├── menu.py       # Menú principal
│       ├── pdf_management.py  # Gestión consolidada de PDFs
│       ├── processing.py # Procesamiento de documentos
│       └── utils.py      # Utilidades consolidadas
│
└── shared/               # Componentes compartidos
    ├── constants/        # Constantes centralizadas
    │   ├── config.py     # Configuración unificada
    │   └── directories.py # Directorios centralizados
    └── utils/            # Utilidades compartidas
        └── error_handling.py # Sistema de errores centralizado
```

### Principios Arquitectónicos

#### 1. Arquitectura Hexagonal (Ports & Adapters)

- **Dominio**: Lógica de negocio pura, sin dependencias externas
- **Aplicación**: Casos de uso y servicios de aplicación
- **Infraestructura**: Implementaciones técnicas
- **Interfaces**: CLI

#### 2. Inyección de Dependencias

- `DependencyContainer` centraliza la creación de objetos
- Composición root en `app.py`
- Interfaces abstraen implementaciones

#### 3. Configuración Centralizada

- `shared.constants.config` unifica toda la configuración
- Sistema de configuración inmutable con dataclasses
- Validación de configuración integrada

## Características

### Procesamiento Inteligente

- **OCR Selectivo**: Aplica OCR solo donde es necesario
- **Extracción de Tablas**: Detecta y preserva estructura tabular
- **Refinamiento LLM**: Mejora el texto con IA (OpenAI/Gemini)
- **Detección de Idioma**: Soporte multilenguaje automático

### Interfaces Múltiples

- **CLI Interactivo**: Menú intuitivo para uso local
- **Procesamiento Batch**: Múltiples documentos

### Características Técnicas

- **Caché Inteligente**: Evita reprocesamiento con hashing seguro BLAKE2b
- **Logging Avanzado**: Trazabilidad completa y detallada
- **Configuración Centralizada**: Gestión unificada y validada
- **Manejo de Errores Robusto**: Sistema centralizado con tipos y severidad
- **Seguridad Mejorada**: Configuración segura (127.0.0.1) y permisos adecuados

### Patrones de Diseño Utilizados

#### Composition Root

```python
# app.py
container = DependencyContainer()
use_case = container.get_pdf_to_markdown_use_case()
```

#### Repository Pattern (Ports)

```python
# domain/ports/document_port.py
class DocumentPort(ABC):
    @abstractmethod
    def extract_content(self, pdf_path: Path) -> str:
        pass
```

#### Service Layer

```python
# application/services/configuration_service.py
class ConfigurationService:
    def update_llm_provider(self, provider: str, settings: Dict[str, Any]):
        # Lógica de configuración
```

### Beneficios de la Arquitectura

#### Problemas Resueltos

1. **Duplicación de Código**: Eliminada mediante centralización
2. **Configuración Fragmentada**: Unificada en un solo lugar
3. **Manejo de Errores Inconsistente**: Estandarizado
4. **Dependencias Circulares**: Resueltas con inyección de dependencias
5. **Archivos Excesivamente Pequeños**: Consolidados

#### Mejoras Implementadas

1. **Testabilidad**: Inyección de dependencias facilita testing
2. **Mantenibilidad**: Código organizado y responsabilidades claras
3. **Extensibilidad**: Nuevas características fáciles de agregar
4. **Robustez**: Manejo de errores mejorado
5. **Configurabilidad**: Sistema de configuración flexible

## Desarrollo

### Agregar Nueva Funcionalidad

1. Definir caso de uso en `application/use_cases/`
2. Crear puerto si necesita infraestructura
3. Implementar adaptador en `adapters/` o `infrastructure/`
4. Registrar en `DependencyContainer`
5. Exponer en interfaz apropiada (`cli/`)

### Configurar Nueva Opción

1. Agregar al dataclass apropiado en `shared/constants/config.py`
2. Actualizar `ConfigurationService` si es necesario
3. Agregar validación en `AppConfig.validate_configuration()`

## Uso

### Docker (Recomendado)

```bash
# Construir e iniciar el contenedor
docker-compose up --build -d

# Acceder al CLI interactivo
docker exec -it ocr-pymupdf python app.py
```

### Local

```bash
# CLI interactivo
python app.py
```

## Funcionalidades

### CLI Interactivo

1. **Convertir PDF a Markdown** - Con validación automática integrada
2. **Configuración** - Configurar proveedores LLM y parámetros
3. **Estadísticas de caché** - Ver información del caché de procesamiento
4. **Salir** - Terminar la aplicación

## Configuración

### Variables de Entorno (.env)

```bash
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=tu_api_key_aqui
GEMINI_API_KEY=tu_api_key_gemini

# Configuración OCR
TESSERACT_CMD=/usr/bin/tesseract
```

## Estado del Proyecto

### Completado

- [x] Configuración centralizada
- [x] Directorios centralizados
- [x] Inyección de dependencias
- [x] Consolidación de archivos CLI
- [x] Sistema de errores unificado
- [x] Eliminación de código duplicado
- [x] Arquitectura hexagonal básica
- [x] Limpieza de funciones duplicadas
- [x] Eliminación de imports no utilizados

### En Progreso

- [ ] Testing exhaustivo de integración
- [ ] Documentación de API
- [ ] Optimización de performance

### Pendiente (Opcional)

- [ ] Implementar caché distribuido
- [ ] Métricas de monitoreo
- [ ] Configuración por variables de entorno
- [ ] Docker optimizado

## Contribución

Esta refactorización transforma OCR-FRONTEND de un sistema con múltiples problemas arquitectónicos a una aplicación bien estructurada, mantenible y extensible que sigue las mejores prácticas de desarrollo de software.

La nueva arquitectura facilita el desarrollo futuro, mejora la testabilidad, y proporciona una base sólida para el crecimiento del sistema.
