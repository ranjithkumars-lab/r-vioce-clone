from typing import Any, Dict, List
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    environment: str
    version: str = "1.0.0"


class SystemStatusResponse(BaseModel):
    app_name: str
    environment: str
    storage_base_dir: str
    cuda_status: Dict[str, Any]
