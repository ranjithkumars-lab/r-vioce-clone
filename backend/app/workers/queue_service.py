import queue
from typing import Any, Dict, Optional
from app.core.logging import logger


class QueueService:
    """Thread-safe queue abstraction providing Redis-ready interface with in-memory fallback."""

    def __init__(self):
        self._queue: queue.Queue[Dict[str, Any]] = queue.Queue()

    def enqueue(self, job_data: Dict[str, Any]) -> None:
        """Push job execution payload to the queue."""
        self._queue.put(job_data)
        logger.info(f"Queued job payload: ID '{job_data.get('job_id')}' (Queue depth: {self.size()})")

    def dequeue(self, block: bool = True, timeout: Optional[float] = 1.0) -> Optional[Dict[str, Any]]:
        """Pop next job payload off the queue."""
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def size(self) -> int:
        return self._queue.qsize()


queue_service = QueueService()
