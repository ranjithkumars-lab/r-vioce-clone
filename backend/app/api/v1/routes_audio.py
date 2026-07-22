from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from app.dependencies import get_history_repository, get_voice_generation_pipeline
from app.repositories.history_repository import HistoryRepository
from app.schemas.audio import GenerateAudioRequest
from app.services.voice_generation_pipeline import VoiceGenerationPipeline

router = APIRouter(prefix="/audio", tags=["Audio Generation"])


@router.post("/generate", status_code=status.HTTP_200_OK, summary="Synthesize Audio Clip")
def generate_audio(
    payload: GenerateAudioRequest,
    pipeline: VoiceGenerationPipeline = Depends(get_voice_generation_pipeline),
):
    """Synthesize speech from text script using reference voice profile and target engine plugin."""
    result = pipeline.generate(
        voice_id=payload.voice_id,
        text=payload.text,
        engine_name=payload.engine or "f5tts",
        speed=payload.speed or 1.0,
    )
    return {
        "message": "Audio synthesized successfully.",
        "data": result,
    }


@router.get("/history", summary="Get Generated Audio History")
def get_audio_history(
    skip: int = 0,
    limit: int = 50,
    history_repo: HistoryRepository = Depends(get_history_repository),
):
    """Fetch history list of previously synthesized audio clips."""
    records = history_repo.get_all(skip=skip, limit=limit)
    return {
        "total": len(records),
        "history": [
            {
                "id": r.id,
                "voice_id": r.voice_id,
                "text_prompt": r.text_prompt,
                "duration": r.duration,
                "sample_rate": r.sample_rate,
                "engine_used": r.engine_used,
                "created_at": r.created_at,
                "audio_file_path": r.audio_file_path,
            }
            for r in records
        ],
    }
