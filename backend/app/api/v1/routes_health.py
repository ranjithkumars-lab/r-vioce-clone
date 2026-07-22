from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config_registry import ConfigRegistry
from app.database.session import get_db
from app.managers.storage_manager import StorageManager
from app.schemas.system import HealthResponse

router = APIRouter(tags=["Health & Probes"])


@router.get("/health", response_model=HealthResponse, summary="Liveness Probe")
def health_check():
    """Liveness probe returning basic health status."""
    settings = ConfigRegistry.get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
    )


@router.get("/ready", response_model=HealthResponse, summary="Readiness Probe")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity and storage directory availability."""
    settings = ConfigRegistry.get_settings()
    try:
        # Check Database connectivity
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {e}",
        )

    try:
        # Check Storage Directory
        StorageManager().ensure_directories()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage readiness check failed: {e}",
        )

    return HealthResponse(
        status="ready",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
    )


@router.get("/live", response_model=HealthResponse, summary="Detailed Status Probe")
def liveness_detailed():
    """Detailed system probe endpoint."""
    settings = ConfigRegistry.get_settings()
    return HealthResponse(
        status="live",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="1.0.0",
    )
