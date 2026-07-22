import pytest
from app.managers.storage_manager import StorageManager


def test_storage_manager_directories(tmp_path):
    storage_mgr = StorageManager(base_storage_dir=tmp_path)
    assert (tmp_path / "voices").exists()
    assert (tmp_path / "generated").exists()
    assert (tmp_path / "temp").exists()
    assert (tmp_path / "models").exists()


def test_save_and_retrieve_metadata(tmp_path):
    storage_mgr = StorageManager(base_storage_dir=tmp_path)
    voice_id = "test-voice-123"
    meta = {"name": "Test Voice", "language": "en"}

    storage_mgr.save_voice_metadata(voice_id, meta)
    loaded_meta = storage_mgr.get_voice_metadata(voice_id)

    assert loaded_meta is not None
    assert loaded_meta["name"] == "Test Voice"
