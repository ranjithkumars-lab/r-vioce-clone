import pytest
from app.services.audio_postprocessor import AudioPostprocessor
from app.services.audio_preprocessor import AudioPreprocessor


def test_audio_preprocessor(tmp_path):
    prep = AudioPreprocessor()
    ref_audio = tmp_path / "ref.wav"
    ref_audio.write_bytes(b"dummy wav content")

    clean_text, ref_path, meta = prep.preprocess("  Hello world   test   ", ref_audio)
    assert clean_text == "Hello world test"
    assert meta["word_count"] == 3
    assert meta["char_count"] == 16
