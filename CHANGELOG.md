# Changelog

All notable changes to **Voice Studio** will be documented in this file.

## [0.3.0] - 2026-07-22
### Added
- Asynchronous job queue (`QueueService`) and background worker daemon (`BackgroundWorkerDaemon`).
- Granular job states (`QUEUED` ➔ `VALIDATING` ➔ `LOADING_MODEL` ➔ `PREPROCESSING` ➔ `GENERATING` ➔ `POSTPROCESSING` ➔ `SAVING` ➔ `COMPLETED`).
- Async job endpoints `POST /api/v1/jobs/enqueue` and `GET /api/v1/jobs/{job_id}`.
- WebSockets event streaming endpoint `/ws/jobs` powered by `EventBus`.
- Request ID and response timing middleware (`RequestIDMiddleware`).
- Metrics manager tracking request counts and latency metrics.

## [0.2.0] - 2026-07-22
### Added
- Abstract plugin engine interface (`BaseAudioEngine`).
- Dynamic plugin discovery in `ModelManager`.
- Audio preprocessor and postprocessor services.
- `MockAudioEngine` and `F5TTSAudioEngine` plugins.
- Speech synthesis endpoint `POST /api/v1/audio/generate` and history endpoint `GET /api/v1/audio/history`.

## [0.1.0] - 2026-07-22
### Added
- Core backend architecture with Pydantic settings, logging, and application error codes.
- `StorageManager` handling centralized file storage and `voice.json` metadata profiles.
- Single SQLite database `voice_studio.db` with repository pattern.
- Audio validation service checking WAV headers, duration, and sample rates.
- Reference voice upload, listing, detail, and deletion API v1 endpoints.
- Health probes (`/health`, `/ready`, `/live`).
