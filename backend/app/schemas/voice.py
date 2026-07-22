from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VoiceProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Ranjith"})
    language: str = Field(default="en", max_length=10, json_schema_extra={"example": "en"})
    gender: str = Field(default="unspecified", json_schema_extra={"example": "male"})
    engine: str = Field(default="f5tts", json_schema_extra={"example": "f5tts"})


class VoiceProfileResponse(VoiceProfileBase):
    id: str
    duration: float
    sample_rate: int
    channels: int
    file_path: str
    reference_text: Optional[str] = None
    transcript_source: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoiceListResponse(BaseModel):
    total: int
    voices: List[VoiceProfileResponse]


class VoiceUploadResponse(BaseModel):
    message: str
    voice: VoiceProfileResponse
