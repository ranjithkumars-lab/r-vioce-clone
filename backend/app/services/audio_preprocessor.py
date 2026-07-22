import re
from pathlib import Path
from typing import Any, Dict, Tuple
from app.core.exceptions import InvalidAudioFileException
from app.core.logging import logger


class AudioPreprocessor:
    """Preprocessor handling script text normalization and reference audio verification."""

    def preprocess(self, text: str, reference_audio_path: Path) -> Tuple[str, Path, Dict[str, Any]]:
        """Clean and validate input text script and verify reference audio availability."""
        # 1. Text script normalization
        cleaned_text = re.sub(r"\s+", " ", text).strip()
        if not cleaned_text:
            raise InvalidAudioFileException("Input script text cannot be empty.")

        # 2. Verify reference audio file
        if not reference_audio_path.exists():
            raise InvalidAudioFileException(f"Reference audio file '{reference_audio_path}' does not exist.")

        metadata = {
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
        }
        logger.info(f"Preprocessed text script: {metadata['word_count']} words, {metadata['char_count']} chars.")
        return cleaned_text, reference_audio_path, metadata
