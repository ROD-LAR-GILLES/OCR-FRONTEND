# OCR-FRONTEND

# OCR-FRONTEND

Sistema OCR avanzado con arquitectura hexagonal para procesamiento de documentos PDF a Markdown.

## 🏗️ Arquitectura

El proyecto implementa una **arquitectura hexagonal (ports & adapters)** limpia con las siguientes capas:

- **🎯 Dominio**: Lógica de negocio pura
- **⚙️ Aplicación**: Casos de uso y servicios
- **🔌 Adaptadores**: Integraciones externas
- **🏗️ Infraestructura**: Implementaciones técnicas
- **🖥️ Interfaces**: CLI y API REST

> 📖 Ver [ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalles completos

## ✨ Características

### 🔄 Procesamiento Inteligente

- **OCR Selectivo**: Aplica OCR solo donde es necesario
- **Extracción de Tablas**: Detecta y preserva estructura tabular
- **Refinamiento LLM**: Mejora el texto con IA (OpenAI/Gemini)
- **Detección de Idioma**: Soporte multilenguaje automático

### 🎯 Interfaces Múltiples

- **CLI Interactivo**: Menú intuitivo para uso local
- **API REST**: Endpoints para integración
- **Procesamiento Batch**: Múltiples documentos

### ⚡ Características Técnicas

- **Caché Inteligente**: Evita reprocesamiento
- **Logging Avanzado**: Trazabilidad completa
- **Configuración Centralizada**: Gestión unificada
- **Manejo de Errores Robusto**: Recuperación automática

## 🏗️ Arquitectura

Este proyecto implementa **Arquitectura Hexagonal (Ports & Adapters)** con:

- **Dominio**: Lógica de negocio pura sin dependencias externas
- **Puertos**: Interfaces que definen contratos
- **Adaptadores**: Implementaciones concretas de los puertos
- **Composition Root**: Inyección de dependencias en el punto de entrada

## 🚀 Uso

### Docker (Recomendado)

```bash
# Construir e iniciar el contenedor
docker-compose up --build -d

# Acceder al CLI interactivo
docker exec -it ocr-pymupdf python app.py --mode cli

# Iniciar servidor API
docker exec -it ocr-pymupdf python app.py --mode api --host 0.0.0.0 --port 8000
```

### Local

```bash
# CLI interactivo
python app.py --mode cli

# Servidor API
python app.py --mode api --host localhost --port 8000

# Con parámetros personalizados
python app.py --mode api --host 0.0.0.0 --port 9000
```

## 📋 Funcionalidades

### CLI Interactivo

1. **Convertir PDF a Markdown** - Con validación automática integrada
2. **Configuración** - Configurar proveedores LLM y parámetros
3. **Estadísticas de caché** - Ver información del caché de procesamiento
4. **Salir** - Terminar la aplicación

### API REST

- **POST /api/convert** - Convertir PDF a Markdown
- **GET /api/progress/{doc_id}** - Consultar progreso de conversión
- **GET /api/health** - Estado del sistema
- **GET /api/logs/{doc_id}** - Logs de procesamiento

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=tu_api_key_aqui
GEMINI_API_KEY=tu_api_key_gemini

# Configuración OCR
TESSERACT_CMD=/usr/bin/tesseract
```
