# Multi-stage Dockerfile — Production-ready
# ============================================================================
# Stage 1: Builder — Instala dependências
# ============================================================================

FROM python:3.10-slim as builder

WORKDIR /tmp

# Copia requirements
COPY requirements.txt .

# Instala dependências em um venv isolado
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime — Imagem final otimizada
# ============================================================================

FROM python:3.10-slim

# Metadados
LABEL maintainer="Harmoniz.AI Team"
LABEL description="Sommelier Digital API para Wine.com.br"
LABEL version="1.0.0"

# Define variável de ambiente para Python (evita buffering de output)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Define working directory
WORKDIR /app

# Copia apenas o venv do builder (reduz tamanho da imagem final)
COPY --from=builder /opt/venv /opt/venv

# Copia código da aplicação
COPY src/ ./src/
COPY data/ ./data/
COPY .env.example ./.env.example

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Port
EXPOSE 8000

# Comando para rodar a API
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
