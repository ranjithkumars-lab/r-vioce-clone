from fastapi import APIRouter, Depends
from app.core.config_registry import ConfigRegistry
from app.dependencies import get_gpu_manager
from app.managers.gpu_manager import GPUManager
from app.schemas.system import SystemStatusResponse

router = APIRouter(prefix="/system", tags=["System Information"])


@router.get("/status", response_model=SystemStatusResponse, summary="Get System & GPU Status")
def get_system_status(gpu_manager: GPUManager = Depends(get_gpu_manager)):
    """Fetch system configuration, storage directory layout, and CUDA/GPU status."""
    settings = ConfigRegistry.get_settings()
    gpu_status = gpu_manager.get_status()

    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        storage_base_dir=str(settings.STORAGE_DIR),
        cuda_status=gpu_status,
    )
