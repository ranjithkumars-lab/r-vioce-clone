import tempfile
import traceback
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
        device_idx = getattr(context, "device_index", 0) if context else 0

        if device == "cuda" and torch.cuda.is_available():
            try:
                torch.cuda.set_device(device_idx)
                device_name = torch.cuda.get_device_name(device_idx)
                logger.info(f"F5Adapter: GPU selected -> CUDA Device {device_idx} ({device_name})")
            except Exception as dev_err:
                logger.warning(f"F5Adapter: Could not set CUDA device {device_idx}: {dev_err}")

        logger.info("Initializing F5-TTS...")
        logger.info("Downloading/Loading F5-TTS checkpoint (SWT-Bench/F5-TTS base model)...")

        try:
            self.model = load_model(model_cls="F5TTS")
            self.vocoder = load_vocoder()
            logger.info("F5-TTS model and vocoder loaded successfully.")
        except Exception as e:
            logger.error(f"F5Adapter: Model loading failed with error: {e}\n{traceback.format_exc()}")
            raise e

    def unload(self):
        self.model = None
        self.vocoder = None

    def synthesize(self, ref_audio: str, ref_text: str, gen_text: str) -> str:
        from f5_tts.infer.utils_infer import infer_process

        audio, sr, spectrogram = infer_process(
            ref_audio=ref_audio,
            ref_text=ref_text,
            gen_text=gen_text,
            model_obj=self.model,
            vocoder=self.vocoder
        )

        import soundfile as sf
        temp_out = tempfile.mktemp(suffix=".wav")
        sf.write(temp_out, audio, sr)
        return temp_out


class F5TTSAudioEngine(BaseAudioEngine):
    """F5-TTS Audio Synthesis Engine Plugin."""

    def __init__(self):
        self.adapter = F5Adapter()
        self._is_loaded = False
        self._last_error: Optional[str] = None

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
            self._last_error = None
            self.adapter.load(context)
            self._is_loaded = True
            return True
        except Exception as e:
            self._last_error = f"{e}\n{traceback.format_exc()}"
            logger.error(f"Failed to load F5-TTS model: {e}")
            self._is_loaded = False
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
            logger.warning("F5-TTS model was not pre-loaded, attempting automatic loading now...")
            loaded = self.load_model(Path("."), context=context)
            if not loaded:
                raise RuntimeError(f"F5-TTS model is not loaded and auto-loading failed: {self._last_error}")

        ref_text = options.get("reference_text") if options else ""
        if not ref_text:
            raise ValueError("F5-TTS requires a reference transcript (reference_text) in options.")

        logger.info(f"F5TTSAudioEngine: Synthesizing {len(text)} chars with ref text length {len(ref_text)} chars...")

        try:
            temp_wav = self.adapter.synthesize(
                ref_audio=str(reference_audio_path),
                ref_text=ref_text,
                gen_text=text
            )

            import shutil
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(temp_wav, str(output_path))
            return output_path
        except Exception as e:
            logger.error(f"F5TTSAudioEngine: Synthesis failed: {e}\n{traceback.format_exc()}")
            raise RuntimeError(f"F5-TTS synthesis failed: {e}")
