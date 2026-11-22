# ==============================================================================
# SIGEPSI BACKEND DOCKERFILE (Django REST + Multi-Tenant PostgreSQL)
# ==============================================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema requeridas para psycopg2 y utilidades
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    dos2unix \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt /app/
# CU21: torch solo-CPU (evita ~2 GB de librerías CUDA) antes del resto de dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# CU21: cache del modelo Hugging Face dentro de la imagen.
# docker build --build-arg PRELOAD_IA=1 ...  descarga el modelo en el build (arranque sin internet).
ENV HF_HOME=/app/.hf_cache
ARG PRELOAD_IA=0
RUN if [ "$PRELOAD_IA" = "1" ]; then python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli')"; fi

# Copiar el código del proyecto
COPY . /app/

# Asegurar terminaciones de línea Unix (LF) y permisos en entrypoint
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
