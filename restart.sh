#!/bin/bash

# Script para reiniciar los contenedores después de realizar cambios

echo "Limpieza de sistema..."
docker system prune --all --volumes --force

echo "Deteniendo contenedores..."
docker compose down

echo "Reconstruyendo imágenes..."
docker compose build

echo "Iniciando contenedores..."
docker compose up --detach

echo "Esperando a que los contenedores estén listos..."
sleep 5

echo "Estado de los contenedores:"
docker ps -a | grep ocr-pymupdf

echo "Iniciando modo interactivo..."
docker compose exec ocr-pymupdf python -m src.main

