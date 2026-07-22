# Voice Studio API v1

Welcome to the Voice Studio API documentation! This API is powered by FastAPI and provides full programmatic access to the Voice Studio asynchronous pipeline.

## Endpoints Overview

- `/api/v1/health` - Check API and GPU cluster health.
- `/api/v1/voices` - CRUD operations for reference voices.
- `/api/v1/jobs` - Manage asynchronous voice generation jobs.
- `/api/v1/ws` - WebSocket endpoint for real-time job events.

For interactive documentation, start the server and navigate to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication
(Authentication mechanisms to be implemented in a future release)

## Examples

### 1. Create a Voice
```bash
curl -X POST "http://localhost:8000/api/v1/voices/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "name=My Custom Voice" \
  -F "description=A test voice" \
  -F "file=@/path/to/reference.wav"
```

### 2. Generate Audio
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"voice_id": "...", "text": "Hello world!", "engine_name": "f5tts", "speed": 1.0}'
```
