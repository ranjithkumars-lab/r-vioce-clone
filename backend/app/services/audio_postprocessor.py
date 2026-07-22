import wave
from pathlib import Path
from typing import Any, Dict
from app.core.exceptions import StorageException
from app.core.logging import logger


class AudioPostprocessor:
    """Postprocessor measuring synthesized WAV clips, validating headers, and formatting output metadata."""

    def postprocess(self, output_path: Path) -> Dict[str, Any]:
        """Validate output WAV file existence, measure duration, sample rate, and channels."""
        if not output_path.exists():
            raise StorageException(f"Synthesized output audio file '{output_path}' was not generated.")

        try:
            with wave.open(str(output_path), "rb") as wav_in:
                n_channels = wav_in.getnchannels()
                sample_rate = wav_in.getframerate()
                n_frames = wav_in.getnframes()
                duration = n_frames / float(sample_rate) if sample_rate > 0 else 0.0
        except Exception as e:
            logger.error(f"Postprocessing failed on '{output_path}': {e}")
            raise StorageException(f"Failed to postprocess synthesized audio file: {e}")

        info = {
            "output_path": str(output_path),
            "duration": round(duration, 2),
            "sample_rate": sample_rate,
            "channels": n_channels,
            "size_bytes": output_path.stat().st_size,
        }
        logger.info(f"Postprocessed synthesized WAV clip: {info['duration']}s, {sample_rate}Hz")
        return info
