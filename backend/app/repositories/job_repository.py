from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job import JobRecord


class JobRepository:
    """Repository handling database access for Generation Jobs."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, job_record: JobRecord) -> JobRecord:
        self.db.add(job_record)
        self.db.commit()
        self.db.refresh(job_record)
        return job_record

    def get_by_id(self, job_id: str) -> Optional[JobRecord]:
        return self.db.query(JobRecord).filter(JobRecord.id == job_id).first()

    def update_status(
        self,
        job_id: str,
        status: str,
        progress: int = 0,
        error_message: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Optional[JobRecord]:
        record = self.get_by_id(job_id)
        if record:
            record.status = status
            record.progress_percentage = progress
            if error_message:
                record.error_message = error_message
            if output_path:
                record.output_audio_path = output_path
            self.db.commit()
            self.db.refresh(record)
            return record
        return None
