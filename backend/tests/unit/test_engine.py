import pytest
from app.engines.plugins.f5tts import F5TTSAudioEngine
from app.engines.plugins.mock import MockAudioEngine
from app.managers.model_manager import ModelManager


def test_mock_engine(tmp_path):
    engine = MockAudioEngine()
    assert engine.engine_name == "mock"
    assert engine.is_available() is True

    ref_wav = tmp_path / "ref.wav"
    ref_wav.write_bytes(b"dummy")
    out_wav = tmp_path / "output.wav"

    res = engine.synthesize(
        text="Hello world speech synthesis test script",
        reference_audio_path=ref_wav,
        output_path=out_wav,
    )

    assert res.exists()
    assert res.stat().st_size > 0


def test_model_manager_auto_discovery():
    mgr = ModelManager()
    engines = mgr.list_available_engines()
    engine_names = [e["name"] for e in engines]

    assert "mock" in engine_names
    assert "f5tts" in engine_names
