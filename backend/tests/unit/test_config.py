from app.core.config import Settings
from app.core.config_registry import ConfigRegistry


def test_settings_defaults():
    settings = ConfigRegistry.get_settings()
    assert settings.APP_NAME == "Voice Studio"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.DEFAULT_SAMPLE_RATE == 24000
