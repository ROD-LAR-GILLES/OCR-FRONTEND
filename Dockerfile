# ------------------ build stage ------------------
FROM python:3.13-slim AS builder

WORKDIR /app

# Instalar dependencias de sistema necesarias para la compilación
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ------------------ runtime stage ------------------
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
        tesseract-ocr-eng \
        tesseract-ocr-chi-tra \
        build-essential \
        python3-dev \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgl1 \
        fontconfig && \
    fc-cache -f -v && \
    rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PYTHONPATH=/app:/app/src:/app/config

WORKDIR /app

# Crear estructura de directorios necesaria y configurar volúmenes
RUN mkdir -p data/corrections \
            pdfs \
            result \
            logs

COPY --from=builder /install /usr/local

COPY app.py .
COPY src/ src/
COPY config/ config/
COPY data/ data/
COPY pdfs/ pdfs/
COPY result/ result/

# Crear usuario no-root
RUN groupadd -r ocruser && useradd -r -g ocruser -d /app ocruser

# Asegurar permisos de escritura y ownership
RUN chown -R ocruser:ocruser /app/data /app/pdfs /app/result /app/logs && \
    chmod -R 755 /app/data /app/pdfs /app/result /app/logs

# Cambiar al usuario no-root
USER ocruser

CMD ["python", "app.py", "--mode", "cli"]