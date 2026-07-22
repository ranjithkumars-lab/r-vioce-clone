from typing import Any, Dict, List, Set
from app.core.config_registry import ConfigRegistry
from app.core.logging import logger
import threading


class GPUManager:
    """GPU Manager handling CUDA detection, VRAM monitoring, and DGX multi-GPU state."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GPUManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.settings = ConfigRegistry.get_settings()
        self._lock = threading.Lock()
        
        # State tracking per device index
        self._logical_reservations_mb: Dict[int, float] = {}
        self._active_jobs: Dict[int, int] = {}
        self._loaded_models: Dict[int, Set[str]] = {}
        
        self._initialized = True

    def get_status(self) -> Dict[str, Any]:
        """Query PyTorch CUDA state, device count, memory, and active device info."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count() if cuda_available else 0

            devices = []
            if cuda_available:
                for idx in range(device_count):
                    device_name = torch.cuda.get_device_name(idx)
                    total_mem = torch.cuda.get_device_properties(idx).total_memory / (1024 ** 2)  # MB
                    allocated_mem = torch.cuda.memory_allocated(idx) / (1024 ** 2)
                    reserved_mem = torch.cuda.memory_reserved(idx) / (1024 ** 2)
                    
                    with self._lock:
                        logical_res = self._logical_reservations_mb.get(idx, 0.0)
                        active_jobs = self._active_jobs.get(idx, 0)
                        models = list(self._loaded_models.get(idx, set()))
                        
                    # Calculate available taking logical reservations into account
                    buffer_mb = self.settings.GPU_RESERVATION_BUFFER_MB
                    physical_free = total_mem - reserved_mem
                    usable_vram = physical_free - logical_res - buffer_mb
                    
                    devices.append({
                        "index": idx,
                        "name": device_name,
                        "total_memory_mb": round(total_mem, 2),
                        "allocated_memory_mb": round(allocated_mem, 2),
                        "reserved_memory_mb": round(reserved_mem, 2),
                        "logical_reserved_mb": round(logical_res, 2),
                        "free_memory_mb": round(physical_free, 2),
                        "usable_memory_mb": round(max(0, usable_vram), 2),
                        "active_jobs": active_jobs,
                        "loaded_models": models,
                    })

            return {
                "cuda_available": cuda_available,
                "device_count": device_count,
                "target_device_index": self.settings.DEFAULT_GPU_INDEX,
                "devices": devices,
                "pytorch_version": torch.__version__,
            }
        except ImportError:
            logger.warning("PyTorch is not installed in the environment. Returning CPU fallback status.")
            return {
                "cuda_available": False,
                "device_count": 0,
                "target_device_index": -1,
                "devices": [],
                "pytorch_version": "None (ImportError)",
            }

    def reserve_logical_memory(self, device_idx: int, mb: float) -> None:
        with self._lock:
            current = self._logical_reservations_mb.get(device_idx, 0.0)
            self._logical_reservations_mb[device_idx] = current + mb
            self._active_jobs[device_idx] = self._active_jobs.get(device_idx, 0) + 1

    def release_logical_memory(self, device_idx: int, mb: float) -> None:
        with self._lock:
            current = self._logical_reservations_mb.get(device_idx, 0.0)
            self._logical_reservations_mb[device_idx] = max(0.0, current - mb)
            current_jobs = self._active_jobs.get(device_idx, 0)
            self._active_jobs[device_idx] = max(0, current_jobs - 1)

    def mark_model_loaded(self, device_idx: int, engine_name: str) -> None:
        with self._lock:
            if device_idx not in self._loaded_models:
                self._loaded_models[device_idx] = set()
            self._loaded_models[device_idx].add(engine_name)
            
    def mark_model_unloaded(self, device_idx: int, engine_name: str) -> None:
        with self._lock:
            if device_idx in self._loaded_models and engine_name in self._loaded_models[device_idx]:
                self._loaded_models[device_idx].remove(engine_name)

    def is_model_loaded(self, device_idx: int, engine_name: str) -> bool:
        with self._lock:
            return engine_name in self._loaded_models.get(device_idx, set())

    def clear_vram_cache(self) -> bool:
        """Attempt to purge CUDA VRAM cache."""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Cleared PyTorch CUDA VRAM cache.")
                return True
        except Exception as e:
            logger.error(f"Error clearing CUDA VRAM: {e}")
        return False

gpu_manager = GPUManager()
