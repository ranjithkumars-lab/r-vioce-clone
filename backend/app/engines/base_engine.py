from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.execution_context import ExecutionContext


class BaseAudioEngine(ABC):
    """Abstract Base Class for all Voice Studio audio synthesis engine plugins."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Unique key name of the engine plugin (e.g., 'f5tts', 'mock', 'xtts')."""
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
