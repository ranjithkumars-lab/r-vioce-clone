from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_job_service
from app.schemas.audio import GenerateAudioRequest
from app.schemas.job import JobResponse, JobStatusResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Async Job Engine"])


@router.post("/enqueue", response_model=JobStatusResponse, status_code=status.HTTP_202_ACCEPTED, summary="Enqueue Asynchronous Synthesis Job")
def enqueue_job(
    payload: GenerateAudioRequest,
    job_service: JobService = Depends(get_job_service),
):
    """Submit asynchronous speech generation task to background queue and worker pool."""
    job_record = job_service.create_and_enqueue_job(
        voice_id=payload.voice_id,
        text=payload.text,
        engine=payload.engine or "f5tts",
        speed=payload.speed or 1.0,
    )
    return JobStatusResponse(
        job_id=job_record.id,
        status=job_record.status,
        progress_percentage=job_record.progress_percentage,
    )


@router.get("/{job_id}", response_model=JobStatusResponse, summary="Query Job Status & Progress")
def get_job_status(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """Query progress percentage and status of a background synthesis job."""
    job_record = job_service.get_job(job_id)
    if not job_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' was not found.",
        )
    return JobStatusResponse(
        job_id=job_record.id,
        status=job_record.status,
        progress_percentage=job_record.progress_percentage,
        output_url=job_record.output_audio_path,
        error=job_record.error_message,
    )
