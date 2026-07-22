import time
import threading
from contextlib import contextmanager
from typing import Generator

from app.core.config_registry import ConfigRegistry
from app.core.logging import logger
from app.managers.gpu_manager import gpu_manager
from app.managers.scheduler_policies import get_scheduler_policy


class GPUScheduler:
    """Schedules jobs across GPUs using configurable policies and logical VRAM reservations."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GPUScheduler, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.settings = ConfigRegistry.get_settings()
        self.policy = get_scheduler_policy(self.settings.SCHEDULER_POLICY)
        # Using a condition variable to efficiently wait for GPU availability
        self._cv = threading.Condition(threading.Lock())
        
        self._initialized = True

    @contextmanager
    def reserve(self, required_vram_mb: float, engine_name: str) -> Generator[int, None, None]:
        """
        Context manager to reserve VRAM on the best available GPU.
        Blocks until a suitable GPU is found.
        Yields the allocated device index.
        """
        device_idx = None
        
        with self._cv:
            while True:
                status = gpu_manager.get_status()
                if not status["cuda_available"] or status["device_count"] == 0:
                    # Fallback for CPU-only systems or missing CUDA
                    logger.warning("No CUDA devices found. Falling back to CPU/default device.")
                    device_idx = self.settings.DEFAULT_GPU_INDEX
                    break
                    
                devices = status["devices"]
                device_idx = self.policy.select_device(devices, required_vram_mb, engine_name)
                
                if device_idx is not None:
                    # GPU found! Reserve logical VRAM
                    gpu_manager.reserve_logical_memory(device_idx, required_vram_mb)
                    logger.info(f"Scheduled job for engine '{engine_name}' on GPU {device_idx}. Reserved {required_vram_mb} MB.")
                    break
                
                # No GPU has enough VRAM right now, wait until someone releases memory
                logger.debug(f"No GPU available with {required_vram_mb} MB for '{engine_name}'. Waiting...")
                self._cv.wait(timeout=5.0) # Check periodically even without notifies just in case

        try:
            yield device_idx
        finally:
            if status.get("cuda_available") and status.get("device_count") > 0 and device_idx is not None:
                # Always release logical VRAM after job finishes (or fails)
                gpu_manager.release_logical_memory(device_idx, required_vram_mb)
                
                # Notify any waiting threads that VRAM is freed
                with self._cv:
                    self._cv.notify_all()
                    
                logger.info(f"Released {required_vram_mb} MB reservation on GPU {device_idx}.")


gpu_scheduler = GPUScheduler()
