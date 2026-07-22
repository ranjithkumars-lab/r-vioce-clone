import threading
import time
from typing import Any, Dict, Optional, List
from app.core.enums import JobStatus
from app.core.event_bus import global_event_bus
from app.core.logging import logger
from app.database.session import SessionLocal
from app.managers.metrics_manager import metrics_manager
from app.repositories.job_repository import JobRepository
from app.services.voice_generation_pipeline import VoiceGenerationPipeline


class BackgroundWorkerDaemon:
    """Daemon worker process picking jobs from QueueService and executing generation pipelines."""

    def __init__(self, queue_svc, pipeline_factory):
        from app.core.config_registry import ConfigRegistry
        self.settings = ConfigRegistry.get_settings()
        self.queue_svc = queue_svc
        self.pipeline_factory = pipeline_factory
        self._running = False
        self._threads: List[threading.Thread] = []

    def start(self) -> None:
        """Start worker loops in background threads."""
        if not self._running:
            self._running = True
            for i in range(self.settings.WORKER_CONCURRENCY):
                thread = threading.Thread(target=self._run_loop, daemon=True, name=f"Worker-{i}")
                self._threads.append(thread)
                thread.start()
            logger.info(f"Background Worker Daemon started successfully with {self.settings.WORKER_CONCURRENCY} threads.")

    def stop(self) -> None:
        """Stop worker loops."""
        self._running = False
        for thread in self._threads:
            thread.join(timeout=2.0)
        self._threads.clear()
        logger.info("Background Worker Daemon stopped.")

    def _run_loop(self) -> None:
        while self._running:
            job_data = self.queue_svc.dequeue(block=True, timeout=0.5)
            if job_data:
                self._process_job(job_data)

    def _process_job(self, job_data: Dict[str, Any]) -> None:
        from app.managers.gpu_scheduler import gpu_scheduler
        from app.core.execution_context import ExecutionContext

        job_id = job_data["job_id"]
        voice_id = job_data["voice_id"]
        text = job_data["text"]
        engine_name = job_data.get("engine", "f5tts")
        speed = job_data.get("speed", 1.0)

        db = SessionLocal()
        job_repo = JobRepository(db)

        start_time = time.time()
        try:
            # 1. Update status: VALIDATING (10%)
            job_repo.update_status(job_id, JobStatus.VALIDATING.value, progress=10)
            global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.VALIDATING.value, "progress": 10})

            # Wait for GPU reservation. 
            # We assume a fixed VRAM requirement for now, e.g. 4000 MB for f5tts.
            # In a full implementation, this could come from model_manager.get_model_memory(engine_name)
            required_vram = 4000.0 if engine_name == "f5tts" else 100.0 

            logger.info(f"Worker requesting {required_vram}MB VRAM for job {job_id} using engine '{engine_name}'.")
            
            with gpu_scheduler.reserve(required_vram, engine_name) as device_index:
                context = ExecutionContext(
                    device_index=device_index,
                    engine_name=engine_name,
                    job_id=job_id,
                )

                # 2. Update status: LOADING_MODEL (25%)
                job_repo.update_status(job_id, JobStatus.LOADING_MODEL.value, progress=25)
                global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.LOADING_MODEL.value, "progress": 25})

                # 3. Update status: PREPROCESSING (40%)
                job_repo.update_status(job_id, JobStatus.PREPROCESSING.value, progress=40)
                global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.PREPROCESSING.value, "progress": 40})

                # 4. Update status: GENERATING (65%)
                job_repo.update_status(job_id, JobStatus.GENERATING.value, progress=65)
                global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.GENERATING.value, "progress": 65})

                # Execute pipeline
                pipeline = self.pipeline_factory(db)
                result = pipeline.generate(
                    voice_id=voice_id,
                    text=text,
                    engine_name=engine_name,
                    speed=speed,
                    context=context,
                )

            # 5. Update status: POSTPROCESSING (85%)
            job_repo.update_status(job_id, JobStatus.POSTPROCESSING.value, progress=85)
            global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.POSTPROCESSING.value, "progress": 85})

            # 6. Update status: SAVING & COMPLETED (100%)
            job_repo.update_status(
                job_id=job_id,
                status=JobStatus.COMPLETED.value,
                progress=100,
                output_path=result["output_path"],
            )

            total_sec = time.time() - start_time
            metrics_manager.record_job_completion(total_sec)
            global_event_bus.publish(
                "job_update",
                {
                    "job_id": job_id,
                    "status": JobStatus.COMPLETED.value,
                    "progress": 100,
                    "output_path": result["output_path"],
                    "duration": result["duration"],
                },
            )
            logger.info(f"Worker processed job '{job_id}' in {total_sec:.2f}s.")
        except Exception as e:
            logger.error(f"Worker failed on job '{job_id}': {e}")
            metrics_manager.record_job_failure()
            job_repo.update_status(job_id, JobStatus.FAILED.value, progress=0, error_message=str(e))
            global_event_bus.publish("job_update", {"job_id": job_id, "status": JobStatus.FAILED.value, "error": str(e)})
        finally:
            db.close()
