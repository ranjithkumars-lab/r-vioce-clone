from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from app.database.base import Base


class VoiceRecord(Base):
    __tablename__ = "voices"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    language = Column(String(10), default="en", nullable=False)
    gender = Column(String(20), default="unspecified")
    engine = Column(String(50), default="f5tts", nullable=False)
    duration = Column(Float, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    channels = Column(Integer, default=1, nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
