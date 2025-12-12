# Production-ready Dockerfile
# Designed to be deployed to cloud platforms (AWS ECS, Azure Container Apps, GCP Cloud Run, K8s)
# Dependencies (MongoDB, Redis) are external cloud services

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Default command options:
# 1. FastAPI only: CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 2. RQ Worker only: CMD ["uv", "run", "python", "worker.py"] 
# 3. Arq (same process): CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Default: FastAPI + RQ Workers in same container (inlined)
CMD ["bash", "-c", "\
echo '🚀 Starting FastAPI + RQ Workers in container...' && \
echo '📡 Starting FastAPI server...' && \
uv run uvicorn main:app --host 0.0.0.0 --port 8000 & \
sleep 3 && \
echo '👷 Starting RQ Workers...' && \
WORKER_NAME=docker-worker-1 uv run python worker.py & \
WORKER_NAME=docker-worker-2 uv run python worker.py & \
WORKER_NAME=docker-worker-3 uv run python worker.py & \
echo '✅ All processes started! FastAPI: http://0.0.0.0:8000' && \
wait -n && \
echo '❌ A process exited, shutting down container...' && \
kill $(jobs -p) 2>/dev/null \
"]