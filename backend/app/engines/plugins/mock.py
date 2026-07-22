import io
import wave
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.engines.base_engine import BaseAudioEngine
from app.core.execution_context import ExecutionContext


class MockAudioEngine(BaseAudioEngine):
    """Fast synthetic audio engine plugin for development, testing, and offline benchmarking."""

    def __init__(self):
        self._is_loaded = False

    @property
    def engine_name(self) -> str:
        return "mock"

    @property
    def description(self) -> str:
        return "Mock Synthetic Audio Engine for testing & local development"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_dir: Path, context: Optional['ExecutionContext'] = None) -> bool:
        logger.info(f"MockAudioEngine: Loading model from {model_dir}")
        self._loaded = True
        return True

    def unload_model(self, context: Optional['ExecutionContext'] = None) -> bool:
        logger.info("MockAudioEngine: Unloading model")
        self._loaded = False
        return True

    def synthesize(
        self,
        text: str,
        reference_audio_path: Path,
        output_path: Path,
        speed: float = 1.0,
        options: Optional[Dict[str, Any]] = None,
        context: Optional['ExecutionContext'] = None,
    ) -> Path:
        """Synthesize a valid 24kHz mono PCM WAV clip proportionally matching text script length."""
        if not self._loaded:
            raise RuntimeError("Model not loaded")

        device_info = f" on {context.device_str}" if context else ""
        logger.info(f"MockAudioEngine: Synthesizing '{text}' (speed={speed}){device_info}")

        sample_rate = 24000
        words = text.split()
        # ~0.3 seconds per word, minimum 2.0s
        duration_sec = max(2.0, len(words) * 0.35 / speed)
        num_samples = int(duration_sec * sample_rate)

        # Generate silent/sine-like 16-bit PCM frames
        raw_frames = b"\x00\x00" * num_samples

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(sample_rate)
            wav_out.writeframes(raw_frames)

        return output_path
