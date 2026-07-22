import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.config_registry import ConfigRegistry
from app.core.exceptions import StorageException
from app.core.logging import logger


class StorageManager:
    """Centralized Storage Manager handling directory structure and file persistence."""

    def __init__(self, base_storage_dir: Optional[Path] = None):
        settings = ConfigRegistry.get_settings()
        self.base_dir = base_storage_dir or settings.STORAGE_DIR
        self.voices_dir = self.base_dir / "voices"
        self.generated_dir = self.base_dir / "generated"
        self.temp_dir = self.base_dir / "temp"
        self.cache_dir = self.base_dir / "cache"
        self.models_dir = self.base_dir / "models"
        self.exports_dir = self.base_dir / "exports"

        self.ensure_directories()

    def ensure_directories(self) -> None:
        """Create all required storage subdirectories."""
        try:
            for directory in [
                self.base_dir,
                self.voices_dir,
                self.generated_dir,
                self.temp_dir,
                self.cache_dir,
                self.models_dir,
                self.exports_dir,
            ]:
                directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directories verified under: {self.base_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize storage directories: {e}")
            raise StorageException(f"Storage directory initialization failed: {e}")

    def save_voice_file(self, voice_id: str, file_bytes: bytes, filename: str) -> Path:
        """Save reference audio file to storage/voices/{voice_id}/{filename}."""
        try:
            voice_folder = self.voices_dir / voice_id
            voice_folder.mkdir(parents=True, exist_ok=True)
            target_path = voice_folder / filename

            with open(target_path, "wb") as f:
                f.write(file_bytes)

            logger.info(f"Saved voice audio file for ID '{voice_id}' to: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to save voice file '{filename}': {e}")
            raise StorageException(f"Failed to save voice audio file: {e}")

    def save_voice_metadata(self, voice_id: str, metadata: Dict[str, Any]) -> Path:
        """Save rich metadata JSON profile to storage/voices/{voice_id}/voice.json."""
        try:
            voice_folder = self.voices_dir / voice_id
            voice_folder.mkdir(parents=True, exist_ok=True)
            target_path = voice_folder / "voice.json"

            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved voice metadata for ID '{voice_id}' to: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to save voice metadata for ID '{voice_id}': {e}")
            raise StorageException(f"Failed to save voice metadata: {e}")

    def get_voice_metadata(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Load voice metadata JSON profile from storage/voices/{voice_id}/voice.json."""
        metadata_path = self.voices_dir / voice_id / "voice.json"
        if not metadata_path.exists():
            return None
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read metadata for voice '{voice_id}': {e}")
            return None

    def delete_voice_folder(self, voice_id: str) -> bool:
        """Delete storage/voices/{voice_id} directory."""
        voice_folder = self.voices_dir / voice_id
        if voice_folder.exists() and voice_folder.is_dir():
            try:
                shutil.rmtree(voice_folder)
                logger.info(f"Deleted storage folder for voice ID '{voice_id}'")
                return True
            except Exception as e:
                logger.error(f"Error removing voice directory '{voice_id}': {e}")
                raise StorageException(f"Failed to delete voice folder: {e}")
        return False
