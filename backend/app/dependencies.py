from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, get_db
from app.managers.gpu_manager import GPUManager
from app.managers.model_manager import ModelManager
from app.managers.storage_manager import StorageManager
from app.repositories.history_repository import HistoryRepository
from app.repositories.job_repository import JobRepository
from app.repositories.voice_repository import VoiceRepository
from app.services.audio_postprocessor import AudioPostprocessor
from app.services.audio_preprocessor import AudioPreprocessor
from app.services.job_service import JobService
from app.services.voice_generation_pipeline import VoiceGenerationPipeline
from app.services.voice_service import VoiceService
from app.services.voice_validation import VoiceValidationService
from app.workers.queue_service import queue_service
from app.workers.worker import BackgroundWorkerDaemon

# Singleton Managers & Services
_storage_manager = StorageManager()
_gpu_manager = GPUManager()
_model_manager = ModelManager()
_voice_validator = VoiceValidationService()
_preprocessor = AudioPreprocessor()
_postprocessor = AudioPostprocessor()


def get_storage_manager() -> StorageManager:
    return _storage_manager


def get_gpu_manager() -> GPUManager:
    return _gpu_manager


def get_model_manager() -> ModelManager:
    return _model_manager


def get_voice_validation_service() -> VoiceValidationService:
    return _voice_validator


def get_audio_preprocessor() -> AudioPreprocessor:
    return _preprocessor


def get_audio_postprocessor() -> AudioPostprocessor:
    return _postprocessor


def get_voice_repository(db: Session = Depends(get_db)) -> VoiceRepository:
    return VoiceRepository(db)


def get_history_repository(db: Session = Depends(get_db)) -> HistoryRepository:
    return HistoryRepository(db)


def get_job_repository(db: Session = Depends(get_db)) -> JobRepository:
    return JobRepository(db)


def get_voice_service(
    voice_repo: VoiceRepository = Depends(get_voice_repository),
    storage_mgr: StorageManager = Depends(get_storage_manager),
    validator: VoiceValidationService = Depends(get_voice_validation_service),
) -> VoiceService:
    return VoiceService(
        voice_repository=voice_repo,
        storage_manager=storage_mgr,
        validator=validator,
    )


def build_pipeline_for_session(db: Session) -> VoiceGenerationPipeline:
    voice_repo = VoiceRepository(db)
    history_repo = HistoryRepository(db)
    voice_svc = VoiceService(voice_repo, _storage_manager, _voice_validator)
    return VoiceGenerationPipeline(
        voice_service=voice_svc,
        model_manager=_model_manager,
        storage_manager=_storage_manager,
        history_repository=history_repo,
        preprocessor=_preprocessor,
        postprocessor=_postprocessor,
    )


def get_voice_generation_pipeline(
    db: Session = Depends(get_db),
) -> VoiceGenerationPipeline:
    return build_pipeline_for_session(db)


def get_job_service(
    job_repo: JobRepository = Depends(get_job_repository),
) -> JobService:
    return JobService(job_repository=job_repo)


# Instantiate worker daemon
worker_daemon = BackgroundWorkerDaemon(
    queue_svc=queue_service,
    pipeline_factory=build_pipeline_for_session,
)
