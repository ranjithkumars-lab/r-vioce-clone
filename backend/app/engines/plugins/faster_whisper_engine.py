from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.engines.base_engine import BaseSTTEngine
from app.core.execution_context import ExecutionContext


class FasterWhisperEngine(BaseSTTEngine):
    """Faster-Whisper Speech-to-Text Engine Plugin."""

    def __init__(self):
        self._model = None

    @property
    def engine_name(self) -> str:
        return "faster-whisper"

    @property
    def description(self) -> str:
        return "Faster-Whisper CTranslate2 Engine for fast STT"

    def is_available(self) -> bool:
        try:
            import faster_whisper
            return True
        except ImportError:
            return False

    def load_model(self, model_dir: Path, context: Optional[ExecutionContext] = None) -> bool:
        try:
            from faster_whisper import WhisperModel
            # We MUST force CPU for faster-whisper because CTranslate2 v4+ wheels
            # are compiled with CUDA 12, which crashes on NVIDIA driver 470.
            device = "cpu"
            device_index = 0
            
            # Using 'base' model for speed in preprocessing
            self._model = WhisperModel("base", device=device, device_index=device_index, compute_type="int8")
            logger.info("Faster-Whisper model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Faster-Whisper model: {e}")
            return False

    def unload_model(self, context: Optional[ExecutionContext] = None) -> bool:
        logger.info("Unloading Faster-Whisper model.")
        self._model = None
        return True

    def transcribe(
        self,
        audio_path: Path,
        options: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> str:
        if not self._model:
            raise RuntimeError("Faster-Whisper model is not loaded.")
        
        logger.info(f"Transcribing audio file: {audio_path}")
        segments, info = self._model.transcribe(str(audio_path), beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        logger.info(f"Transcription completed ({info.language}): {text[:50]}...")
        return text.strip()
