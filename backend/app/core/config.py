import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Voice Studio"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    LOG_DIR: Path = BASE_DIR / "logs"

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/storage/voice_studio.db"

    # GPU & Model settings
    CUDA_VISIBLE_DEVICES: str = "0"
    DEFAULT_GPU_INDEX: int = 0
    DEFAULT_ENGINE: str = "f5tts"

    # Multi-GPU Scheduling
    GPU_RESERVATION_BUFFER_MB: int = 2048
    SCHEDULER_POLICY: str = "least_vram_used"
    WORKER_CONCURRENCY: int = 4

    # Audio Constraints
    MAX_UPLOAD_SIZE_MB: int = 50
    MIN_VOICE_DURATION_SEC: float = 2.0
    MAX_VOICE_DURATION_SEC: float = 600.0
    DEFAULT_SAMPLE_RATE: int = 24000

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
