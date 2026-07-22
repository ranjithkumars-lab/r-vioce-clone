import io
import wave
from typing import Any, Dict
from app.core.config_registry import ConfigRegistry
from app.core.exceptions import FileTooLargeException, InvalidAudioFileException
from app.core.logging import logger


class VoiceValidationService:
    """Service handling audio file validation rules."""

    def __init__(self):
        self.settings = ConfigRegistry.get_settings()

    def validate_wav_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Validate uploaded audio bytes for RIFF WAV format, size, duration, channels, and sample rate."""
        # 1. File size check
        max_bytes = self.settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        file_size = len(file_bytes)
        if file_size > max_bytes:
            raise FileTooLargeException(
                f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum limit of {self.settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        if file_size < 100:
            raise InvalidAudioFileException("Uploaded file is empty or corrupted.")

        # 2. RIFF WAV header & parameter parsing
        try:
            with wave.open(io.BytesIO(file_bytes), "rb") as wave_file:
                n_channels = wave_file.getnchannels()
                sample_rate = wave_file.getframerate()
                n_frames = wave_file.getnframes()
                sample_width = wave_file.getsampwidth()
                duration = n_frames / float(sample_rate) if sample_rate > 0 else 0.0
        except Exception as e:
            logger.warning(f"Validation failed for '{filename}': Not a valid RIFF WAV audio file. Error: {e}")
            raise InvalidAudioFileException(
                f"File '{filename}' is not a valid RIFF WAV audio file or has an unsupported compression header."
            )

        # 3. Duration check
        if duration < self.settings.MIN_VOICE_DURATION_SEC:
            raise InvalidAudioFileException(
                f"Audio duration ({duration:.2f}s) is shorter than minimum required duration of {self.settings.MIN_VOICE_DURATION_SEC}s."
            )
        if duration > self.settings.MAX_VOICE_DURATION_SEC:
            raise InvalidAudioFileException(
                f"Audio duration ({duration:.2f}s) exceeds maximum allowed duration of {self.settings.MAX_VOICE_DURATION_SEC}s."
            )

        logger.info(f"Successfully validated WAV file '{filename}': {duration:.2f}s, {sample_rate}Hz, {n_channels} ch")
        return {
            "duration": round(duration, 2),
            "sample_rate": sample_rate,
            "channels": n_channels,
            "sample_width": sample_width,
            "size_bytes": file_size,
        }
