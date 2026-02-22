# Base image
FROM python:3.14-slim-bookworm

# Runtime env: clean FS, real-time logs, predictable imports
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# App root inside container
WORKDIR /app

# curl only for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install deps first (cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app code
COPY ./app ./app

# Writable dirs for runtime artifacts
RUN mkdir -p /app/data /app/logs && chmod -R 777 /app/data /app/logs

# Healthcheck via /health endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# API port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
