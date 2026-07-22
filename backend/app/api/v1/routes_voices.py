from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.dependencies import get_voice_service
from app.schemas.voice import VoiceListResponse, VoiceProfileResponse, VoiceUploadResponse
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/voices", tags=["Voices"])


@router.post("/upload", response_model=VoiceUploadResponse, status_code=status.HTTP_201_CREATED, summary="Upload Reference Voice")
async def upload_voice(
    file: UploadFile = File(..., description="Reference audio .wav file"),
    name: str = Form(..., description="Name of the voice profile"),
    language: str = Form("en", description="ISO language code"),
    gender: str = Form("unspecified", description="Gender descriptor"),
    engine: str = Form("f5tts", description="Target TTS engine"),
    transcript: Optional[str] = Form(None, description="Optional reference transcript. If blank, Whisper will auto-transcribe."),
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Upload reference WAV audio file, validate audio constraints, generate voice.json, and store profile."""
    file_bytes = await file.read()
    filename = file.filename or "reference.wav"

    voice_record = voice_service.upload_voice(
        file_bytes=file_bytes,
        filename=filename,
        name=name,
        language=language,
        gender=gender,
        engine=engine,
        transcript=transcript,
    )

    return VoiceUploadResponse(
        message=f"Voice profile '{name}' uploaded and registered successfully.",
        voice=VoiceProfileResponse.model_validate(voice_record),
    )


@router.get("", response_model=VoiceListResponse, summary="List Active Voice Profiles")
def list_voices(
    skip: int = 0,
    limit: int = 100,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """List all registered reference voice profiles."""
    voices = voice_service.list_voices(skip=skip, limit=limit)
    total = voice_service.count_voices()
    return VoiceListResponse(
        total=total,
        voices=[VoiceProfileResponse.model_validate(v) for v in voices],
    )


@router.get("/{voice_id}", response_model=VoiceProfileResponse, summary="Get Voice Profile Details")
def get_voice(
    voice_id: str,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Get metadata for a specific voice profile."""
    voice_record = voice_service.get_voice(voice_id)
    return VoiceProfileResponse.model_validate(voice_record)


@router.delete("/{voice_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Voice Profile")
def delete_voice(
    voice_id: str,
    voice_service: VoiceService = Depends(get_voice_service),
):
    """Delete reference voice files, voice.json metadata, and database entry."""
    voice_service.delete_voice(voice_id)
    return None
