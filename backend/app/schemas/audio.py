from typing import Optional
from pydantic import BaseModel, Field


class GenerateAudioRequest(BaseModel):
    voice_id: str = Field(..., description="ID of the reference voice profile")
    text: str = Field(..., min_length=1, max_length=5000, description="Script to synthesize")
    engine: Optional[str] = Field(default="f5tts", description="Target audio synthesis engine")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Playback speed modifier")
