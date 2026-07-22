import asyncio
import subprocess
from typing import Dict, List, Optional
import time

class GPUMonitor:
    def __init__(self, interval_seconds: float = 1.0):
        self.interval = interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        # Structure: { gpu_index: { "utilization": [], "memory": [], "temperature": [], "power": [] } }
        self.metrics: Dict[str, Dict[str, List[float]]] = {}

    def start(self):
        self.is_running = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self.is_running = False
        if self._task:
            await self._task

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        summary = {}
        for gpu_id, stats in self.metrics.items():
            if not stats["utilization"]:
                continue
            summary[f"gpu{gpu_id}"] = {
                "avg_utilization_pct": round(sum(stats["utilization"]) / len(stats["utilization"]), 2),
                "peak_utilization_pct": max(stats["utilization"]),
                "peak_memory_mb": max(stats["memory"]),
                "avg_temperature_c": round(sum(stats["temperature"]) / len(stats["temperature"]), 2),
                "peak_power_w": max(stats["power"]) if stats["power"] else 0.0,
            }
        return summary

    async def _monitor_loop(self):
        while self.is_running:
            try:
                # Run nvidia-smi
                process = await asyncio.create_subprocess_shell(
                    "nvidia-smi --query-gpu=index,utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv,noheader,nounits",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()
                
                if process.returncode == 0 and stdout:
                    lines = stdout.decode().strip().split('\n')
                    for line in lines:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            gpu_idx = parts[0]
                            util = float(parts[1]) if parts[1] != '[Not Supported]' else 0.0
                            mem = float(parts[2]) if parts[2] != '[Not Supported]' else 0.0
                            temp = float(parts[3]) if parts[3] != '[Not Supported]' else 0.0
                            power = float(parts[4]) if len(parts) > 4 and parts[4] != '[Not Supported]' else 0.0
                            
                            if gpu_idx not in self.metrics:
                                self.metrics[gpu_idx] = {"utilization": [], "memory": [], "temperature": [], "power": []}
                                
                            self.metrics[gpu_idx]["utilization"].append(util)
                            self.metrics[gpu_idx]["memory"].append(mem)
                            self.metrics[gpu_idx]["temperature"].append(temp)
                            self.metrics[gpu_idx]["power"].append(power)
            except Exception as e:
                # If nvidia-smi fails or isn't installed, just ignore and sleep
                pass
                
            await asyncio.sleep(self.interval)
