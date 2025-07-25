#!/bin/bash
# Script para iniciar Docker Compose con el sistema OCR

# Asegurar que los directorios necesarios existan
mkdir -p pdfs result logs cache output

# Construir y levantar contenedores
docker-compose up --build -d

# Esperar a que los contenedores estén listos
echo "Esperando a que los contenedores estén listos..."
sleep 5

# Mostrar estado de los contenedores
echo "Estado de los contenedores:"
docker ps | grep ocr-pymupdf

# Iniciar modo interactivo
echo "Iniciando modo interactivo..."
docker-compose exec ocr-pymupdf python -m src.main
