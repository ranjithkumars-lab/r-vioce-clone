import io
import wave
import subprocess
from typing import Any, Dict, Tuple
from app.core.config_registry import ConfigRegistry
from app.core.exceptions import FileTooLargeException, InvalidAudioFileException
from app.core.logging import logger


class VoiceValidationService:
    """Service handling audio file validation rules."""

    def __init__(self):
        self.settings = ConfigRegistry.get_settings()

    def _convert_to_wav(self, file_bytes: bytes) -> bytes:
        """Attempt to convert an audio file buffer to WAV using FFmpeg."""
        try:
            process = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1', '-v', 'error'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = process.communicate(input=file_bytes)
            if process.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {err.decode('utf-8')}")
            return out
        except Exception as e:
            logger.error(f"Error during audio conversion: {e}")
            raise InvalidAudioFileException("Failed to convert audio file to WAV.")

    def validate_wav_file(self, file_bytes: bytes, filename: str) -> Tuple[Dict[str, Any], bytes]:
        """Validate uploaded audio bytes, converting them to WAV if necessary. Returns metadata and the final WAV bytes."""
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
        processed_bytes = file_bytes
        try:
            with wave.open(io.BytesIO(processed_bytes), "rb") as wave_file:
                n_channels = wave_file.getnchannels()
                sample_rate = wave_file.getframerate()
                n_frames = wave_file.getnframes()
                sample_width = wave_file.getsampwidth()
                duration = n_frames / float(sample_rate) if sample_rate > 0 else 0.0
        except Exception as e:
            # If wave.open fails, it might be an MP3, M4A, etc. Try converting it.
            logger.info(f"File '{filename}' failed RIFF check. Attempting format conversion with FFmpeg...")
            try:
                processed_bytes = self._convert_to_wav(file_bytes)
                with wave.open(io.BytesIO(processed_bytes), "rb") as wave_file:
                    n_channels = wave_file.getnchannels()
                    sample_rate = wave_file.getframerate()
                    n_frames = wave_file.getnframes()
                    sample_width = wave_file.getsampwidth()
                    duration = n_frames / float(sample_rate) if sample_rate > 0 else 0.0
                logger.info(f"Successfully converted '{filename}' to WAV format.")
            except Exception as conv_err:
                logger.warning(f"Validation failed for '{filename}': {conv_err}")
                raise InvalidAudioFileException(
                    f"File '{filename}' is not a valid audio file or could not be processed."
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
            "size_bytes": len(processed_bytes),
        }, processed_bytes
