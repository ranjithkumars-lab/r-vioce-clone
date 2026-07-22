from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.history import HistoryRecord


class HistoryRepository:
    """Repository handling database access for Audio History records."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, history_record: HistoryRecord) -> HistoryRecord:
        self.db.add(history_record)
        self.db.commit()
        self.db.refresh(history_record)
        return history_record

    def get_by_id(self, history_id: str) -> Optional[HistoryRecord]:
        return self.db.query(HistoryRecord).filter(HistoryRecord.id == history_id).first()

    def get_all(self, skip: int = 0, limit: int = 50) -> List[HistoryRecord]:
        return self.db.query(HistoryRecord).order_by(HistoryRecord.created_at.desc()).offset(skip).limit(limit).all()
