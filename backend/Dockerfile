# Stage 1: Shared Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# 1. Heavy PyTorch & AI base dependencies (850MB+) - Cached separately
COPY requirements-base.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-base.txt

# 2. Lightweight app dependencies - Cached separately
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Shared Base Runtime Layer
FROM python:3.11-slim AS base-runtime

RUN apt-get update && apt-get install -y ffmpeg libgomp1 && rm -rf /var/lib/apt/lists/* && \
    addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

# Stage 3: API Container Target
FROM base-runtime AS api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Worker Container Target
FROM base-runtime AS worker
CMD ["python", "worker_main.py"]
