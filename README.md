# OCR-PYMUPDF

Sistema de OCR y procesamiento de documentos PDF basado en arquitectura hexagonal.

##  Características Principales

- Extracción de texto de PDFs digitales y escaneados
- Detección y extracción de tablas
- Refinamiento de texto usando LLMs (OpenAI, Google Gemini)
- Caché de resultados OCR para optimización
- Sistema de corrección manual de palabras
- Soporte multilenguaje

##  Estructura del Proyecto

```
src/
├── domain/             # Núcleo de la aplicación
│   ├── entities/       # Entidades principales
│   ├── value_objects/  # Objetos de valor inmutables
│   ├── ports/         # Interfaces para servicios externos
│   ├── use_cases/     # Lógica de negocio
│   └── dtos/          # Objetos de transferencia de datos
│
├── adapters/           # Implementaciones de puertos
│   ├── ocr_adapter.py      # Adaptador OCR (Tesseract)
│   ├── pymupdf_adapter.py  # Adaptador PDF
│   ├── llm_refiner.py     # Refinamiento con LLMs
│   └── providers/         # Proveedores LLM (OpenAI, Gemini)
│
├── infrastructure/     # Servicios técnicos
│   ├── file_storage.py    # Almacenamiento de archivos
│   ├── logging_setup.py   # Sistema de logs
│   └── ocr_cache.py      # Caché de resultados
│
├── interfaces/         # Puntos de entrada
│   ├── cli_menu.py        # Interfaz de línea de comandos
│   └── config_menu.py     # Menú de configuración
│
└── config/            # Configuración del sistema
    └── settings.py        # Ajustes globales
```

##  Casos de Uso Principales

1. **Procesamiento de PDFs Digitales**
   - Extracción directa de texto
   - Preservación de formato y estructura

2. **Procesamiento de PDFs Escaneados**
   - OCR con Tesseract
   - Optimización mediante caché
   - Corrección manual de palabras

3. **Extracción de Tablas**
   - Detección automática
   - Conversión a formato estructurado

4. **Refinamiento de Texto**
   - Mejora mediante LLMs
   - Múltiples proveedores disponibles
   - Control de costos y tokens

##  Tecnologías Utilizadas

- **Python 3.11+**
- **PyMuPDF**: Procesamiento de PDFs
- **Tesseract**: Motor OCR
- **OpenAI/Gemini**: Refinamiento de texto
- **FAISS/Chroma**: Vectorización y búsqueda
- **SQLite**: Almacenamiento local

##  Requisitos

1. Python 3.11 o superior
2. Tesseract OCR instalado
3. Variables de entorno configuradas
4. Dependencias Python instaladas

##  Configuración

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/ROD-LAR-GILLES/OCR-PYMUPDF.git
   cd OCR-PYMUPDF
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus claves API
   ```

##  Uso

1. **Interfaz de Línea de Comandos**:
   ```bash
   python src/main.py
   ```

2. **Opciones Disponibles**:
   - Listar PDFs disponibles
   - Convertir PDF a Markdown
   - Configurar procesamiento LLM
   - Gestionar cache OCR

##  Arquitectura

El proyecto sigue una arquitectura hexagonal (ports & adapters) que:

1. **Aísla la Lógica de Negocio**
   - El dominio es independiente de implementaciones externas
   - Interfaces claras mediante puertos

2. **Facilita la Extensibilidad**
   - Nuevos adaptadores sin modificar el dominio
   - Fácil adición de nuevas interfaces

3. **Asegura la Mantenibilidad**
   - Separación clara de responsabilidades
   - Documentación exhaustiva

##  Documentación

Para más detalles sobre:
- Arquitectura y diseño
- Guías de desarrollo
- API Reference
- Ejemplos de uso

Consulta la [Wiki del proyecto](https://github.com/ROD-LAR-GILLES/OCR-PYMUPDF/wiki)

##  Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/NuevaCaracteristica`
3. Commit cambios: `git commit -am 'Añadir nueva característica'`
4. Push a la rama: `git push origin feature/NuevaCaracteristica`
5. Crear Pull Request

##  Licencia

Este proyecto está licenciado bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

