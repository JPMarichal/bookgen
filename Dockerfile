FROM python:3.11-slim

# Metadatos
LABEL maintainer="BookGen System"
LABEL description="Sistema Automatizado de Generación de Libros con IA"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/bookgen/.local/bin:$PATH"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    pandoc \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash bookgen

# Cambiar al directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cambiar propietario del directorio
RUN chown -R bookgen:bookgen /app

# Cambiar a usuario no-root
USER bookgen

# Copiar el resto del código
COPY --chown=bookgen:bookgen . .

# Crear directorios necesarios
RUN mkdir -p data/logs config/prompts bios docx esquemas colecciones wordTemplate

# Verificar que todas las dependencias estén correctas
RUN python -c "import sys; print(f'Python {sys.version}')" && \
    python -c "import fastapi, requests, nltk, sklearn; print('Core dependencies OK')" && \
    pandoc --version

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]