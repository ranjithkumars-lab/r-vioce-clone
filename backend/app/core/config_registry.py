from typing import Optional
from app.core.config import Settings, settings


class ConfigRegistry:
    """Centralized Configuration Registry provider for Voice Studio."""

    _instance: Optional[Settings] = None

    @classmethod
    def get_settings(cls) -> Settings:
        if cls._instance is None:
            cls._instance = settings
        return cls._instance

    @classmethod
    def set_settings(cls, custom_settings: Settings) -> None:
        cls._instance = custom_settings
