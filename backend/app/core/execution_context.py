from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionContext:
    device_index: int
    engine_name: str
    job_id: str
    
    @property
    def device_str(self) -> str:
        # e.g., 'cuda:0'
        return f"cuda:{self.device_index}"
