# ===================================
# Etapa 1: Builder - Construcción de dependencias
# ===================================
FROM python:3.11-slim AS builder

# Variables de entorno para construcción
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_TRUSTED_HOST="pypi.org pypi.python.org files.pythonhosted.org"

# Instalar dependencias de construcción y certificados
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para dependencias
WORKDIR /install

# Copiar requirements y construir wheels
COPY requirements.txt .
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org && \
    pip install --prefix=/install --no-cache-dir --no-warn-script-location \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt && \
    # Remover archivos innecesarios para reducir tamaño
    find /install -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /install -type d -name "*.dist-info" -exec rm -rf {}/RECORD {} + 2>/dev/null || true && \
    find /install -name "*.pyc" -delete 2>/dev/null || true && \
    find /install -name "*.pyo" -delete 2>/dev/null || true && \
    find /install -name "*.c" -delete 2>/dev/null || true && \
    find /install -name "*.pxd" -delete 2>/dev/null || true && \
    rm -rf /install/share 2>/dev/null || true


# ===================================
# Etapa 2: Runtime - Imagen de producción optimizada
# ===================================
FROM python:3.11-slim

# Metadatos
LABEL maintainer="BookGen System"
LABEL description="Sistema Automatizado de Generación de Libros con IA"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/install/bin:$PATH"
ENV PYTHONPATH="/install/lib/python3.11/site-packages"

# Instalar solo dependencias de runtime necesarias (sin build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash bookgen

# Cambiar al directorio de trabajo
WORKDIR /app

# Copiar dependencias desde builder
COPY --from=builder /install /install

# Cambiar propietario del directorio
RUN chown -R bookgen:bookgen /app

# Cambiar a usuario no-root
USER bookgen

# Copiar solo archivos necesarios para la aplicación
COPY --chown=bookgen:bookgen src/ ./src/
COPY --chown=bookgen:bookgen requirements.txt ./

# Crear directorios necesarios
RUN mkdir -p data/logs config/prompts bios docx esquemas colecciones wordTemplate

# Verificar que todas las dependencias estén correctas
RUN python -c "import sys; print(f'Python {sys.version}')" && \
    python -c "import fastapi, requests, nltk, sklearn; print('Core dependencies OK')" && \
    pandoc --version

# Exponer puerto
EXPOSE 8000

# Health check optimizado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]