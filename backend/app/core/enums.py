from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    LOADING_MODEL = "LOADING_MODEL"
    PREPROCESSING = "PREPROCESSING"
    GENERATING = "GENERATING"
    POSTPROCESSING = "POSTPROCESSING"
    SAVING = "SAVING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VoiceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    ERROR = "ERROR"


class AudioEngine(str, Enum):
    F5TTS = "f5tts"
    MOCK = "mock"
    XTTS = "xtts"
    OPENVOICE = "openvoice"
    FISHSPEECH = "fishspeech"


class ErrorCode(str, Enum):
    # System & Validation Errors (VS001 - VS099)
    VS001_INVALID_FILE_FORMAT = "VS001"
    VS002_FILE_TOO_LARGE = "VS002"
    VS003_DURATION_OUT_OF_BOUNDS = "VS003"
    VS004_VOICE_NOT_FOUND = "VS004"
    VS005_DUPLICATE_VOICE_NAME = "VS005"
    
    # Engine & Resource Errors (VS100 - VS199)
    VS100_MODEL_NOT_LOADED = "VS100"
    VS101_ENGINE_NOT_FOUND = "VS101"
    VS102_GPU_UNAVAILABLE = "VS102"
    VS103_VRAM_EXHAUSTED = "VS103"
    
    # Job & Execution Errors (VS200 - VS299)
    VS200_JOB_NOT_FOUND = "VS200"
    VS201_JOB_FAILED = "VS201"
    VS202_QUEUE_FULL = "VS202"
    
    # Storage & Persistence Errors (VS300 - VS399)
    VS300_STORAGE_WRITE_ERROR = "VS300"
    VS301_DATABASE_ERROR = "VS301"
