from typing import Any, Dict, Optional
from app.core.enums import ErrorCode


class VoiceStudioException(Exception):
    """Base exception for all Voice Studio domain errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class InvalidAudioFileException(VoiceStudioException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VS001_INVALID_FILE_FORMAT,
            status_code=400,
            details=details,
        )


class FileTooLargeException(VoiceStudioException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VS002_FILE_TOO_LARGE,
            status_code=413,
            details=details,
        )


class VoiceNotFoundException(VoiceStudioException):
    def __init__(self, voice_id: str):
        super().__init__(
            message=f"Voice profile with ID '{voice_id}' was not found.",
            error_code=ErrorCode.VS004_VOICE_NOT_FOUND,
            status_code=404,
            details={"voice_id": voice_id},
        )


class StorageException(VoiceStudioException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VS300_STORAGE_WRITE_ERROR,
            status_code=500,
            details=details,
        )


class EngineNotFoundException(VoiceStudioException):
    def __init__(self, engine_name: str):
        super().__init__(
            message=f"Audio engine '{engine_name}' is not registered.",
            error_code=ErrorCode.VS101_ENGINE_NOT_FOUND,
            status_code=400,
            details={"engine": engine_name},
        )
