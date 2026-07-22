import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.engines.base_engine import BaseAudioEngine
from app.core.execution_context import ExecutionContext

class F5Adapter:
    """Adapter wrapper for F5-TTS official library."""
    def __init__(self):
        self.model = None
        self.vocoder = None

    def load(self, context: Optional[ExecutionContext]):
        # Lazy import to avoid crashing if F5-TTS is not installed
        from f5_tts.infer.utils_infer import load_model, load_vocoder
        import torch

        device = "cuda" if context and context.device_str.startswith("cuda") else "cpu"
        
        # Load F5-TTS model (uses defaults if no ckpt_path provided)
        # F5-TTS auto-downloads from HF if weights are missing
        logger.info(f"F5Adapter: Loading F5-TTS model to {device}...")
        self.model = load_model(model_cls="F5TTS")
        self.vocoder = load_vocoder()
        logger.info("F5Adapter: Model and Vocoder loaded.")

    def unload(self):
        self.model = None
        self.vocoder = None
        
    def synthesize(self, ref_audio: str, ref_text: str, gen_text: str) -> str:
        from f5_tts.infer.utils_infer import infer_process
        
        # infer_process returns the audio data (e.g., sample_rate, audio_tensor)
        # However, F5-TTS API might return just audio array and sr, or write to file.
        # We will use the common infer_process signature.
        audio, sr, spectrogram = infer_process(
            ref_audio=ref_audio,
            ref_text=ref_text,
            gen_text=gen_text,
            model_obj=self.model,
            vocoder=self.vocoder
        )
        
        # Save to temp file
        import soundfile as sf
        temp_out = tempfile.mktemp(suffix=".wav")
        sf.write(temp_out, audio, sr)
        return temp_out


class F5TTSAudioEngine(BaseAudioEngine):
    """F5-TTS Audio Synthesis Engine Plugin."""

    def __init__(self):
        self.adapter = F5Adapter()
        self._is_loaded = False

    @property
    def engine_name(self) -> str:
        return "f5tts"

    @property
    def description(self) -> str:
        return "F5-TTS Non-Autoregressive Zero-Shot Voice Cloning"

    def is_available(self) -> bool:
        try:
            import f5_tts
            import torch
            return True
        except ImportError:
            return False

    def load_model(self, model_dir: Path, context: Optional[ExecutionContext] = None) -> bool:
        try:
            self.adapter.load(context)
            self._is_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load F5-TTS model: {e}")
            return False

    def unload_model(self, context: Optional[ExecutionContext] = None) -> bool:
        self.adapter.unload()
        self._is_loaded = False
        return True

    def synthesize(
        self,
        text: str,
        reference_audio_path: Path,
        output_path: Path,
        speed: float = 1.0,
        options: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> Path:
        """Synthesize audio script using F5-TTS adapter."""
        if not self._is_loaded:
            raise RuntimeError("F5-TTS model is not loaded")

        ref_text = options.get("reference_text") if options else ""
        if not ref_text:
            raise ValueError("F5-TTS requires a reference transcript (reference_text) in options.")

        logger.info(f"F5TTSAudioEngine: Synthesizing {len(text)} chars with ref {len(ref_text)} chars.")
        
        temp_wav = self.adapter.synthesize(
            ref_audio=str(reference_audio_path),
            ref_text=ref_text,
            gen_text=text
        )
        
        import shutil
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(temp_wav, str(output_path))
        
        return output_path
