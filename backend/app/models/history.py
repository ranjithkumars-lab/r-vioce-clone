from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from app.database.base import Base


class HistoryRecord(Base):
    __tablename__ = "history"

    id = Column(String(36), primary_key=True, index=True)
    voice_id = Column(String(36), ForeignKey("voices.id"), nullable=False, index=True)
    text_prompt = Column(Text, nullable=False)
    audio_file_path = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)
    sample_rate = Column(Integer, default=24000, nullable=False)
    engine_used = Column(String(50), default="f5tts", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
