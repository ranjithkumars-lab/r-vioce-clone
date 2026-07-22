import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.core.execution_context import ExecutionContext
from app.managers.model_manager import ModelManager
from app.managers.storage_manager import StorageManager
from app.models.history import HistoryRecord
from app.repositories.history_repository import HistoryRepository
from app.services.audio_postprocessor import AudioPostprocessor
from app.services.audio_preprocessor import AudioPreprocessor
from app.services.voice_service import VoiceService


class VoiceGenerationPipeline:
    """Orchestrator pipeline decoupling API handlers from audio preprocessing, engine synthesis, and postprocessing."""

    def __init__(
        self,
        voice_service: VoiceService,
        model_manager: ModelManager,
        storage_manager: StorageManager,
        history_repository: HistoryRepository,
        preprocessor: Optional[AudioPreprocessor] = None,
        postprocessor: Optional[AudioPostprocessor] = None,
    ):
        self.voice_service = voice_service
        self.model_manager = model_manager
        self.storage_manager = storage_manager
        self.history_repository = history_repository
        self.preprocessor = preprocessor or AudioPreprocessor()
        self.postprocessor = postprocessor or AudioPostprocessor()

    def generate(
        self,
        voice_id: str,
        text: str,
        engine_name: str = "f5tts",
        speed: float = 1.0,
        options: Optional[Dict[str, Any]] = None,
        context: Optional['ExecutionContext'] = None,
    ) -> Dict[str, Any]:
        """Execute complete speech synthesis pipeline."""
        # 1. Fetch reference voice profile
        voice_record = self.voice_service.get_voice(voice_id)
        ref_audio_path = Path(voice_record.file_path)

        # 2. Preprocess input script text and reference audio
        clean_text, ref_audio_path, pre_info = self.preprocessor.preprocess(text, ref_audio_path)

        # 3. Retrieve target BaseAudioEngine plugin from ModelManager
        engine = self.model_manager.get_engine(engine_name)

        # 4. Synthesize WAV audio clip
        clip_id = str(uuid.uuid4())
        output_filename = f"gen_{clip_id}.wav"
        target_output_path = self.storage_manager.generated_dir / output_filename

        # Add reference text to options for engines like F5-TTS
        merged_options = options or {}
        merged_options["reference_text"] = voice_record.reference_text

        logger.info(f"Pipeline running synthesis clip '{clip_id}' via engine '{engine.engine_name}'...")
        synthesized_path = engine.synthesize(
            text=clean_text,
            reference_audio_path=ref_audio_path,
            output_path=target_output_path,
            speed=speed,
            options=merged_options,
            context=context,
        )

        # 5. Postprocess synthesized audio output
        post_info = self.postprocessor.postprocess(synthesized_path)

        # 6. Record entry in History table
        history_record = HistoryRecord(
            id=clip_id,
            voice_id=voice_id,
            text_prompt=clean_text,
            audio_file_path=str(synthesized_path),
            duration=post_info["duration"],
            sample_rate=post_info["sample_rate"],
            engine_used=engine.engine_name,
            created_at=datetime.utcnow(),
        )
        self.history_repository.create(history_record)
        logger.info(f"Pipeline completed clip '{clip_id}': {post_info['duration']}s WAV saved.")

        return {
            "history_id": clip_id,
            "voice_id": voice_id,
            "text": clean_text,
            "output_path": str(synthesized_path),
            "duration": post_info["duration"],
            "sample_rate": post_info["sample_rate"],
            "engine": engine.engine_name,
        }
