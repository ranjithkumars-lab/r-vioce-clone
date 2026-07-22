import pytest
from app.core.exceptions import InvalidAudioFileException
from app.services.voice_validation import VoiceValidationService


def test_validate_valid_wav(generate_sample_wav):
    validator = VoiceValidationService()
    wav_bytes = generate_sample_wav(duration_sec=3.0, sample_rate=24000)

    result = validator.validate_wav_file(wav_bytes, "test.wav")
    assert result["duration"] == 3.0
    assert result["sample_rate"] == 24000
    assert result["channels"] == 1


def test_validate_short_wav(generate_sample_wav):
    validator = VoiceValidationService()
    # 0.5s duration is below 2.0s minimum
    wav_bytes = generate_sample_wav(duration_sec=0.5, sample_rate=24000)

    with pytest.raises(InvalidAudioFileException):
        validator.validate_wav_file(wav_bytes, "short.wav")


def test_validate_corrupted_file():
    validator = VoiceValidationService()
    bad_bytes = b"not a wav header content"

    with pytest.raises(InvalidAudioFileException):
        validator.validate_wav_file(bad_bytes, "bad.wav")
