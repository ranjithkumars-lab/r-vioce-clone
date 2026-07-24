import uuid
from datetime import datetime
from typing import List, Optional
from app.core.exceptions import VoiceNotFoundException
from app.core.logging import logger
from app.managers.storage_manager import StorageManager
from app.models.voice import VoiceRecord
from app.repositories.voice_repository import VoiceRepository
from app.services.voice_validation import VoiceValidationService


class VoiceService:
    """Service layer orchestrating voice profiles, audio storage, and database persistence."""

    def __init__(
        self,
        voice_repository: VoiceRepository,
        storage_manager: StorageManager,
        validator: VoiceValidationService,
    ):
        self.repository = voice_repository
        self.storage_manager = storage_manager
        self.validator = validator

    def upload_voice(
        self,
        file_bytes: bytes,
        filename: str,
        name: str,
        language: str = "en",
        gender: str = "unspecified",
        engine: str = "f5tts",
        transcript: Optional[str] = None,
    ) -> VoiceRecord:
        """Validate, store audio file, write voice.json profile, and persist VoiceRecord database entry."""
        # 1. Validate audio (and convert if necessary)
        audio_info, processed_bytes = self.validator.validate_wav_file(file_bytes, filename)

        voice_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # 2. Save audio file via StorageManager
        # Ensure the stored filename always ends in .wav since we normalized it
        storage_filename = f"{filename.rsplit('.', 1)[0]}.wav" if '.' in filename else f"{filename}.wav"
        audio_path = self.storage_manager.save_voice_file(voice_id, processed_bytes, storage_filename)

        # 3. Create rich voice.json metadata profile
        metadata = {
            "id": voice_id,
            "name": name,
            "language": language,
            "gender": gender,
            "engine": engine,
            "duration": audio_info["duration"],
            "sample_rate": audio_info["sample_rate"],
            "channels": audio_info["channels"],
            "file_path": str(audio_path),
            "status": "ACTIVE",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "tags": [],
            "description": f"Uploaded reference voice profile '{name}'",
            "version": 1,
        }
        self.storage_manager.save_voice_metadata(voice_id, metadata)

        # 4. Determine Transcript & Status
        reference_text = transcript.strip() if transcript else None
        transcript_source = "manual" if reference_text else "whisper"
        status = "READY" if reference_text else "PROCESSING"

        # 5. Save to Database
        voice_record = VoiceRecord(
            id=voice_id,
            name=name,
            language=language,
            gender=gender,
            engine=engine,
            duration=audio_info["duration"],
            sample_rate=audio_info["sample_rate"],
            channels=audio_info["channels"],
            file_path=str(audio_path),
            reference_text=reference_text,
            transcript_source=transcript_source,
            status=status,
            created_at=now,
            updated_at=now,
        )
        saved_record = self.repository.create(voice_record)
        
        # 6. Enqueue Async Transcription if needed
        if status == "PROCESSING":
            from app.workers.queue_service import queue_service
            queue_service.enqueue({
                "job_id": str(uuid.uuid4()),
                "job_type": "transcription",
                "voice_id": voice_id,
                "file_path": str(audio_path)
            })

        logger.info(f"Successfully registered new voice profile ID '{voice_id}' ({name})")
        return saved_record

    def get_voice(self, voice_id: str) -> VoiceRecord:
        record = self.repository.get_by_id(voice_id)
        if not record:
            raise VoiceNotFoundException(voice_id)
        return record

    def list_voices(self, skip: int = 0, limit: int = 100) -> List[VoiceRecord]:
        return self.repository.get_all(skip=skip, limit=limit)

    def count_voices(self) -> int:
        return self.repository.count()

    def delete_voice(self, voice_id: str) -> bool:
        record = self.get_voice(voice_id)
        # Delete files & metadata folder
        self.storage_manager.delete_voice_folder(voice_id)
        # Delete DB record
        return self.repository.delete(record.id)
