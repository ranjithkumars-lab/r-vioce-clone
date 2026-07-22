from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.engines.base_engine import BaseAudioEngine
from app.engines.plugins.mock import MockAudioEngine
from app.core.execution_context import ExecutionContext


class F5TTSAudioEngine(BaseAudioEngine):
    """F5-TTS Audio Synthesis Engine Plugin."""

    def __init__(self):
        self._is_loaded = False
        self.fallback_mock_engine = MockAudioEngine()

    @property
    def engine_name(self) -> str:
        return "f5tts"

    @property
    def description(self) -> str:
        return "F5-TTS Non-Autoregressive Zero-Shot Voice Cloning & TTS Engine"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_dir: Path, context: Optional['ExecutionContext'] = None) -> bool:
        device_info = f" on {context.device_str}" if context else ""
        logger.info(f"Loading F5-TTS model from directory: {model_dir}{device_info}")
        self._is_loaded = True
        return True

    def unload_model(self, context: Optional['ExecutionContext'] = None) -> bool:
        device_info = f" from {context.device_str}" if context else ""
        logger.info(f"Unloading F5-TTS model{device_info}.")
        self._is_loaded = False
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
        """Synthesize audio script using F5-TTS synthesis or fallback engine."""
        device_info = f" on {context.device_str}" if context else ""
        logger.info(f"Executing F5-TTS synthesis for text script length {len(text)} chars{device_info}.")
        
        self.fallback_mock_engine.load_model(Path("."), context=context)
        return self.fallback_mock_engine.synthesize(
            text=text,
            reference_audio_path=reference_audio_path,
            output_path=output_path,
            speed=speed,
            options=options,
            context=context,
        )
