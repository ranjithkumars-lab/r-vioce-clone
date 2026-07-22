# Contributing to Voice Studio

Thank you for your interest in contributing to **Voice Studio**!

## Coding Standards

### Code Style & Formatting
- Code style follows **PEP 8**.
- Use **Ruff** for linting and code formatting (`ruff check .`, `ruff format .`).
- Use **mypy** for static type checking (`mypy backend/app`).

### Project Architecture Rules
1. **Separation of Entities and DTOs**: Database ORM models reside in `backend/app/models/`. API request and response DTOs reside in `backend/app/schemas/`.
2. **Core Package**: Global constants, enums, exceptions, and configuration reside under `backend/app/core/`.
3. **Storage Access**: Always use `StorageManager` to read/write storage directories (`storage/voices/`, `storage/generated/`, etc.). Do not access the filesystem directly inside route handlers.
4. **Error Codes**: Raise `VoiceStudioException` with standard `VSxxx` application error codes defined in `backend/app/core/enums.py`.

### Commit Message Format
Format commit messages with concise imperative summaries:
- `feat: add F5TTS audio engine plugin`
- `fix: validate WAV header sampling rate in voice_validation.py`
- `docs: update deployment architecture guide`

## Running Tests
Run pytest before submitting pull requests:
```bash
cd backend
pytest
```
