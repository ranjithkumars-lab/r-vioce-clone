import asyncio
import httpx
from typing import Optional, List
import logging
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)

class BenchmarkClient:
    def __init__(self, base_url: str, metrics: MetricsCollector):
        self.base_url = base_url.rstrip("/")
        self.metrics = metrics
        # Default voice ID to use for generation tasks during benchmarks
        self.default_voice_id: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None

    async def setup(self):
        """Initialize the client and grab a voice ID to use for TTS."""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        try:
            resp = await self.client.get("/api/v1/voices")
            resp.raise_for_status()
            voices = resp.json().get("voices", [])
            if voices:
                self.default_voice_id = voices[0]["id"]
            else:
                logger.warning("No voices found in the database. Benchmarks might fail if the engine requires a voice profile.")
        except Exception as e:
            logger.error(f"Failed to fetch voices during setup: {e}")

    async def teardown(self):
        """Close the client."""
        if self.client:
            await self.client.aclose()

    async def run_lifecycle(self, engine: str, text: str = "This is a synthetic benchmark test.") -> None:
        """Submit a job and poll until completion or failure."""
        if not self.client:
            raise RuntimeError("Client not setup")

        payload = {
            "text": text,
            "engine": engine,
            "voice_id": self.default_voice_id or "benchmark_dummy_voice"
        }

        # 1. Submit Job
        try:
            resp = await self.client.post("/api/v1/jobs/enqueue", json=payload)
            resp.raise_for_status()
            job_data = resp.json()
            job_id = job_data.get("job_id") or job_data.get("id")
            if not job_id:
                raise KeyError(f"Response missing job_id: {job_data}")
        except Exception as e:
            logger.exception("Failed to submit job")
            return

        self.metrics.track_job_submitted(job_id)

        # 2. Poll Status
        completed = False
        attempts = 0
        while not completed and attempts < 600:
            attempts += 1
            await asyncio.sleep(0.5)
            try:
                poll_resp = await self.client.get(f"/api/v1/jobs/{job_id}")
                poll_resp.raise_for_status()
                status_data = poll_resp.json()
                status = status_data["status"]
                
                # Check if it was picked up by a worker (often status goes to PROCESSING or we can inspect metadata)
                worker_id = status_data.get("metadata", {}).get("gpu_device")
                
                self.metrics.update_job_status(job_id, status, worker_id=worker_id)
                
                if status in ["COMPLETED", "FAILED"]:
                    completed = True
            except Exception as e:
                logger.error(f"Failed polling job {job_id}: {e}")
                self.metrics.update_job_status(job_id, "FAILED")
                completed = True
                
        if not completed:
            logger.error(f"Job {job_id} timed out after 5 minutes of polling.")
            self.metrics.update_job_status(job_id, "FAILED")

    async def run_concurrent_batch(self, concurrency: int, total_jobs: int, engine: str):
        """Run a batch of jobs with a specific concurrency limit."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_lifecycle():
            async with semaphore:
                await self.run_lifecycle(engine=engine)
                
        tasks = [bounded_lifecycle() for _ in range(total_jobs)]
        await asyncio.gather(*tasks)
