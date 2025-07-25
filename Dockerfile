# ------------------ build stage ------------------
FROM python:3.11-slim AS builder

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
FROM python:3.11-slim

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
ENV PYTHONPATH=/app/src

WORKDIR /app

# Crear estructura de directorios necesaria y configurar volúmenes
RUN mkdir -p /app/data/corrections \
            /app/pdfs \
            /app/resultado

COPY --from=builder /install /usr/local

COPY src/ src/
COPY data/ data/
COPY pdfs/ pdfs/
COPY resultado/ resultado/

# Asegurar permisos de escritura y ownership
RUN chown -R 1000:1000 /app/data && \
    chmod -R 777 /app/data

CMD ["python", "-m", "src.main"]