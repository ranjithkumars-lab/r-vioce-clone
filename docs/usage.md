# Voice Studio User & Operator Guide

This guide covers step-by-step usage of Voice Studio via the Web UI, REST API, Benchmarking Suite, and Production Deployment.

---

## Table of Contents
1. [Web UI Usage](#1-web-ui-usage)
2. [REST API Usage](#2-rest-api-usage)
3. [Running Benchmarks](#3-running-benchmarks)
4. [Production Deployment](#4-production-deployment)
5. [Troubleshooting & FAQs](#5-troubleshooting--faqs)

---

## 1. Web UI Usage

Access the dashboard at `http://localhost:5173` (or your domain, e.g., `https://rvoice.amrita.ac.in`).

### Cloning a Voice Profile
1. Navigate to the **Voices** tab on the left sidebar.
2. Click **Clone New Voice**.
3. Fill in:
   - **Voice Name**: Identifier (e.g. `John Doe`).
   - **Language**: English (`en`), Tamil (`ta`), etc.
   - **Engine**: Target engine (`F5-TTS` or `Mock Engine`).
   - **Reference Audio**: Drag & drop or browse a `.wav`, `.mp3`, `.m4a`, or `.flac` audio snippet (10–30 seconds recommended).
4. Click **Clone Voice**.

### Generating Speech (TTS)
1. Navigate to the **Generate** tab.
2. Select your registered **Voice Profile**.
3. Choose the target **Engine** and **Speed**.
4. Enter the text script to synthesize.
5. Click **Generate Audio**. The job progress will stream live via WebSockets.

---

## 2. REST API Usage

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### List Voices
```bash
curl http://localhost:8000/api/v1/voices
```

### Upload Reference Voice
```bash
curl -X POST "http://localhost:8000/api/v1/voices/upload" \
  -F "name=Demo Voice" \
  -F "language=en" \
  -F "gender=male" \
  -F "engine=f5tts" \
  -F "file=@/path/to/reference_audio.wav"
```

### Submit Asynchronous Audio Synthesis Job
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "<VOICE_ID>",
    "text": "Welcome to Voice Studio asynchronous voice cloning.",
    "engine": "f5tts",
    "speed": 1.0
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/<JOB_ID>
```

---

## 3. Running Benchmarks

Voice Studio includes a multi-threaded benchmark suite to evaluate queue throughput and GPU scheduler performance.

### Run Queue Throughput Benchmark
```bash
# Inside backend container or local environment:
PYTHONPATH=backend python3 -m scripts.benchmark.runner \
  --profile queue \
  --url http://127.0.0.1:8000 \
  --concurrency 20 \
  --jobs 100
```

### Options
- `--concurrency`: Number of parallel worker clients (default: 20 for SQLite, 100+ for Redis).
- `--jobs`: Total number of synthesis requests to enqueue and process.
- `--profile`: `queue` (tests queue ingestion and processing speed) or `end_to_end` (includes audio synthesis).

---

## 4. Production Deployment

### Docker Compose Stack
```bash
docker compose up -d --build
```

### Service Map
- **Frontend Dashboard**: `http://localhost:80`
- **FastAPI Backend**: `http://localhost:8000`
- **Grafana Monitoring**: `http://localhost:3000` (Default credentials: `admin` / `admin_secure`)
- **Prometheus Metrics**: `http://localhost:9090`

---

## 5. Troubleshooting & FAQs

### Q: Upload returns `400 Bad Request` or `422 Unprocessable Entity`
- Ensure you do **NOT** hardcode `Content-Type: multipart/form-data` without a boundary in custom client calls.
- Ensure `ffmpeg` is installed if uploading `.m4a` or `.mp3` files.

### Q: Benchmark script fails with `httpx.ReadTimeout`
- When using SQLite as the database backend, high concurrency (>50) causes database lock contention. Lower concurrency to `--concurrency 20` or switch `QUEUE_BACKEND=redis` in `.env`.
