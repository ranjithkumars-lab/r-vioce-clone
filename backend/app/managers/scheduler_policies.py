from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseSchedulerPolicy(ABC):
    @abstractmethod
    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        """
        Selects a GPU device index based on the specific policy.
        Returns the index of the selected device, or None if no device is suitable.
        """
        pass

class FirstAvailablePolicy(BaseSchedulerPolicy):
    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        for device in devices:
            if device["usable_memory_mb"] >= required_vram_mb:
                return device["index"]
        return None

class LeastVRAMUsedPolicy(BaseSchedulerPolicy):
    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        suitable_devices = [d for d in devices if d["usable_memory_mb"] >= required_vram_mb]
        if not suitable_devices:
            return None
            
        # Pick device with the MAXIMUM free usable memory
        best_device = max(suitable_devices, key=lambda d: d["usable_memory_mb"])
        return best_device["index"]

class RoundRobinPolicy(BaseSchedulerPolicy):
    def __init__(self):
        self._last_index = -1

    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        if not devices:
            return None

        n = len(devices)
        for _ in range(n):
            self._last_index = (self._last_index + 1) % n
            device = devices[self._last_index]
            if device["usable_memory_mb"] >= required_vram_mb:
                return device["index"]
        return None

class LeastLoadedPolicy(BaseSchedulerPolicy):
    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        suitable_devices = [d for d in devices if d["usable_memory_mb"] >= required_vram_mb]
        if not suitable_devices:
            return None
            
        # Pick device with the MINIMUM active jobs
        best_device = min(suitable_devices, key=lambda d: d["active_jobs"])
        return best_device["index"]

class ModelAffinityPolicy(BaseSchedulerPolicy):
    def select_device(self, devices: List[Dict[str, Any]], required_vram_mb: float, engine_name: str) -> Optional[int]:
        suitable_devices = [d for d in devices if d["usable_memory_mb"] >= required_vram_mb]
        if not suitable_devices:
            return None
            
        # First try to find a device that already has the model loaded
        affinity_devices = [d for d in suitable_devices if engine_name in d["loaded_models"]]
        if affinity_devices:
            # Tie-break with least active jobs
            best_device = min(affinity_devices, key=lambda d: d["active_jobs"])
            return best_device["index"]
            
        # Fallback to least loaded if model is not loaded anywhere
        best_device = min(suitable_devices, key=lambda d: d["active_jobs"])
        return best_device["index"]

def get_scheduler_policy(policy_name: str) -> BaseSchedulerPolicy:
    policies = {
        "first_available": FirstAvailablePolicy,
        "least_vram_used": LeastVRAMUsedPolicy,
        "round_robin": RoundRobinPolicy,
        "least_loaded": LeastLoadedPolicy,
        "model_affinity": ModelAffinityPolicy,
    }
    policy_cls = policies.get(policy_name.lower(), LeastVRAMUsedPolicy)
    return policy_cls()
