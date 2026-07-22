from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.voice import VoiceRecord


class VoiceRepository:
    """Repository handling database access for Voice profiles."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, voice_record: VoiceRecord) -> VoiceRecord:
        self.db.add(voice_record)
        self.db.commit()
        self.db.refresh(voice_record)
        return voice_record

    def get_by_id(self, voice_id: str) -> Optional[VoiceRecord]:
        return self.db.query(VoiceRecord).filter(VoiceRecord.id == voice_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[VoiceRecord]:
        return self.db.query(VoiceRecord).filter(VoiceRecord.status == "ACTIVE").offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(VoiceRecord).filter(VoiceRecord.status == "ACTIVE").count()

    def delete(self, voice_id: str) -> bool:
        record = self.get_by_id(voice_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False
