from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    id: str
    voice_id: str
    text_prompt: str
    status: str
    progress_percentage: int
    error_message: Optional[str] = None
    output_audio_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_percentage: int
    output_url: Optional[str] = None
    error: Optional[str] = None
