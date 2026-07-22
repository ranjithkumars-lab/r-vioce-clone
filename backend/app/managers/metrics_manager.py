import time
from typing import Any, Dict
from app.core.logging import logger


class MetricsManager:
    """Metrics Manager tracking system performance counters, job queue depths, and synthesis latencies."""

    def __init__(self):
        self.total_requests = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
        self.total_generation_time_sec = 0.0

    def record_job_completion(self, duration_sec: float) -> None:
        self.completed_jobs += 1
        self.total_generation_time_sec += duration_sec

    def record_job_failure(self) -> None:
        self.failed_jobs += 1

    def get_metrics(self) -> Dict[str, Any]:
        avg_gen_time = (
            self.total_generation_time_sec / self.completed_jobs
            if self.completed_jobs > 0
            else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "average_generation_latency_sec": round(avg_gen_time, 2),
            "total_generation_time_sec": round(self.total_generation_time_sec, 2),
        }


metrics_manager = MetricsManager()
