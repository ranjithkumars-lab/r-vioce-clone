import uuid
from datetime import datetime
from typing import Optional
from app.core.enums import JobStatus
from app.core.exceptions import VoiceStudioException
from app.models.job import JobRecord
from app.repositories.job_repository import JobRepository
from app.workers.queue_service import queue_service


class JobService:
    """Service handling asynchronous generation jobs and queuing."""

    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def create_and_enqueue_job(
        self,
        voice_id: str,
        text: str,
        engine: str = "f5tts",
        speed: float = 1.0,
    ) -> JobRecord:
        """Create JobRecord in database, set status QUEUED, and submit to QueueService."""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job_record = JobRecord(
            id=job_id,
            voice_id=voice_id,
            text_prompt=text,
            status=JobStatus.QUEUED.value,
            progress_percentage=0,
            created_at=now,
            updated_at=now,
        )
        saved_record = self.job_repository.create(job_record)

        # Enqueue job payload
        queue_service.enqueue({
            "job_id": job_id,
            "voice_id": voice_id,
            "text": text,
            "engine": engine,
            "speed": speed,
        })

        return saved_record

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self.job_repository.get_by_id(job_id)
