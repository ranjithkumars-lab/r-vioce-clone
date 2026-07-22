import time
from typing import Dict, List, Optional
from datetime import datetime

class JobMetric:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.submitted_at: Optional[float] = None
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.failed: bool = False
        self.error_message: Optional[str] = None
        self.gpu_assigned: Optional[str] = None
        
    @property
    def queue_wait_time(self) -> Optional[float]:
        if self.submitted_at and self.started_at:
            return self.started_at - self.submitted_at
        return None

    @property
    def execution_duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def total_latency(self) -> Optional[float]:
        if self.submitted_at and self.completed_at:
            return self.completed_at - self.submitted_at
        return None

class MetricsCollector:
    def __init__(self):
        self.jobs: Dict[str, JobMetric] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start_suite(self):
        self.start_time = time.time()

    def end_suite(self):
        self.end_time = time.time()

    def track_job_submitted(self, job_id: str):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobMetric(job_id)
        self.jobs[job_id].submitted_at = time.time()

    def update_job_status(self, job_id: str, status: str, worker_id: Optional[str] = None):
        if job_id not in self.jobs:
            return
            
        metric = self.jobs[job_id]
        
        if worker_id:
            # worker_id usually contains the gpu device info or worker UUID
            metric.gpu_assigned = worker_id
            
        if status == "PROCESSING" and not metric.started_at:
            metric.started_at = time.time()
        elif status == "COMPLETED" and not metric.completed_at:
            metric.completed_at = time.time()
            # If it missed the processing state in polling
            if not metric.started_at:
                metric.started_at = metric.submitted_at
        elif status == "FAILED":
            metric.failed = True
            metric.completed_at = time.time()
            if not metric.started_at:
                metric.started_at = metric.submitted_at

    def calculate_percentile(self, data: List[float], percentile: float) -> float:
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = int(k)
        c = int(k) + 1 if int(k) + 1 < len(sorted_data) else int(k)
        if f == c:
            return sorted_data[f]
        d0 = sorted_data[f] * (c - k)
        d1 = sorted_data[c] * (k - f)
        return round(d0 + d1, 3)

    def get_summary(self) -> Dict:
        total_time = (self.end_time or time.time()) - (self.start_time or time.time())
        total_jobs = len(self.jobs)
        
        completed_jobs = [j for j in self.jobs.values() if j.completed_at and not j.failed]
        failed_jobs = [j for j in self.jobs.values() if j.failed]
        
        latencies = [j.total_latency for j in completed_jobs if j.total_latency]
        queue_times = [j.queue_wait_time for j in completed_jobs if j.queue_wait_time]
        exec_times = [j.execution_duration for j in completed_jobs if j.execution_duration]
        
        throughput = len(completed_jobs) / total_time if total_time > 0 else 0

        return {
            "total_jobs": total_jobs,
            "completed": len(completed_jobs),
            "failed": len(failed_jobs),
            "total_duration_sec": round(total_time, 2),
            "throughput_jobs_per_sec": round(throughput, 2),
            "queue_wait_time_sec": {
                "avg": round(sum(queue_times) / len(queue_times), 3) if queue_times else 0,
                "p95": self.calculate_percentile(queue_times, 95)
            },
            "execution_time_sec": {
                "avg": round(sum(exec_times) / len(exec_times), 3) if exec_times else 0,
                "p95": self.calculate_percentile(exec_times, 95)
            },
            "total_latency_sec": {
                "avg": round(sum(latencies) / len(latencies), 3) if latencies else 0,
                "p95": self.calculate_percentile(latencies, 95)
            }
        }
