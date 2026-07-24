import json
import os
import queue
import uuid
from typing import Any, Dict, Optional
from app.core.logging import logger


class QueueService:
    """Thread-safe and cross-container queue service supporting Redis, SQLite DB, and In-Memory modes."""

    def __init__(self):
        self.redis_client = None
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self._memory_queue: queue.Queue = queue.Queue()
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            client = redis.Redis.from_url(self.redis_url, socket_connect_timeout=1)
            client.ping()
            self.redis_client = client
            logger.info(f"QueueService connected to Redis at '{self.redis_url}'")
        except Exception as e:
            self.redis_client = None
            logger.info(f"QueueService Redis unavailable ({e}). Using DB/In-memory queue fallback.")

    def enqueue(self, job_data: Dict[str, Any]) -> None:
        """Push job execution payload to the queue."""
        if not job_data.get("job_id"):
            job_data["job_id"] = str(uuid.uuid4())
            
        job_id = job_data["job_id"]
        job_type = job_data.get("job_type", "tts")

        # 1. Try Redis Queue
        if self.redis_client:
            try:
                self.redis_client.rpush("voice_studio_jobs", json.dumps(job_data))
                depth = self.redis_client.llen("voice_studio_jobs")
                logger.info(f"Queued job payload via Redis: ID '{job_id}' (Type: {job_type}, Queue depth: {depth})")
                return
            except Exception as e:
                logger.warning(f"Redis enqueue failed ({e}), falling back to DB queue.")

        # 2. Try SQLite DB Queue Fallback (Shared across containers via storage volume)
        try:
            from app.database.session import SessionLocal
            from app.models.job import QueueJobRecord
            
            db = SessionLocal()
            db_record = QueueJobRecord(
                id=job_id,
                payload=json.dumps(job_data),
                status="QUEUED"
            )
            db.add(db_record)
            db.commit()
            db.close()
            logger.info(f"Queued job payload via DB: ID '{job_id}' (Type: {job_type})")
            return
        except Exception as e:
            logger.warning(f"DB enqueue fallback error ({e}), storing in local memory queue.")

        # 3. Fallback to memory queue
        self._memory_queue.put(job_data)
        logger.info(f"Queued job payload via Memory: ID '{job_id}' (Type: {job_type})")

    def dequeue(self, block: bool = True, timeout: Optional[float] = 1.0) -> Optional[Dict[str, Any]]:
        """Pop next job payload off the queue."""
        # 1. Try Redis
        if self.redis_client:
            try:
                res = self.redis_client.blpop("voice_studio_jobs", timeout=int(timeout or 1))
                if res:
                    _, payload_bytes = res
                    payload = json.loads(payload_bytes.decode("utf-8"))
                    logger.info(f"Dequeued job payload via Redis: ID '{payload.get('job_id')}' (Type: {payload.get('job_type', 'tts')})")
                    return payload
            except Exception as e:
                err_msg = str(e)
                if "Timeout" in err_msg or "timed out" in err_msg:
                    logger.debug("Redis queue poll timed out (idle).")
                else:
                    logger.warning(f"Redis dequeue error ({e}), checking DB queue.")

        # 2. Try DB Queue
        try:
            from app.database.session import SessionLocal
            from app.models.job import QueueJobRecord
            
            db = SessionLocal()
            record = db.query(QueueJobRecord).filter(QueueJobRecord.status == "QUEUED").order_by(QueueJobRecord.created_at.asc()).first()
            if record:
                record.status = "PROCESSING"
                db.commit()
                payload = json.loads(record.payload)
                db.delete(record)
                db.commit()
                db.close()
                logger.info(f"Dequeued job payload via DB: ID '{payload.get('job_id')}' (Type: {payload.get('job_type', 'tts')})")
                return payload
            db.close()
        except Exception as e:
            logger.error(f"DB dequeue error: {e}")

        # 3. Try Memory Queue
        try:
            return self._memory_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def size(self) -> int:
        if self.redis_client:
            try:
                return self.redis_client.llen("voice_studio_jobs")
            except Exception:
                pass
        return self._memory_queue.qsize()


queue_service = QueueService()
