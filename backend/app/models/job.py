from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database.base import Base


class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, index=True)
    voice_id = Column(String(36), nullable=False)
    text_prompt = Column(Text, nullable=False)
    status = Column(String(30), default="QUEUED", nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    output_audio_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
