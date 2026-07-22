from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.execution_context import ExecutionContext


class BaseEngine(ABC):
    """Abstract Base Class for all Voice Studio AI engine plugins (TTS, STT, etc)."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Unique key name of the engine plugin (e.g., 'f5tts', 'faster-whisper')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human readable engine description."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if engine requirements (e.g. weights, dependencies, CUDA) are satisfied."""
        pass

    @abstractmethod
    def load_model(self, model_dir: Path, context: Optional[ExecutionContext] = None) -> bool:
        """Load engine model weights into memory/GPU."""
        pass

    @abstractmethod
    def unload_model(self, context: Optional[ExecutionContext] = None) -> bool:
        """Unload engine model weights and release memory/VRAM."""
        pass


class BaseAudioEngine(BaseEngine):
    """Abstract Base Class for TTS audio synthesis engine plugins."""
    @abstractmethod
    def synthesize(
        self,
        text: str,
        reference_audio_path: Path,
        output_path: Path,
        speed: float = 1.0,
        options: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> Path:
        """Synthesize audio from text script using reference voice audio file."""
        pass


class BaseSTTEngine(BaseEngine):
    """Abstract Base Class for Speech-to-Text (STT) engine plugins."""
    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        options: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> str:
        """Transcribe audio file to text."""
        pass
