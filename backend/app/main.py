from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import api_v1_router
from app.core.config_registry import ConfigRegistry
from app.core.exceptions import VoiceStudioException
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.database.session import init_db
from app.dependencies import worker_daemon
from app.managers.storage_manager import StorageManager

settings = ConfigRegistry.get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode...")
    # 1. Initialize storage directory structure
    StorageManager().ensure_directories()
    # 2. Initialize SQLite database schema
    init_db()
    # 3. Start background worker daemon
    worker_daemon.start()
    logger.info("Startup complete - ready to accept API requests.")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")
    worker_daemon.stop()


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI Audio Platform & Voice Studio API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(VoiceStudioException)
async def voice_studio_exception_handler(request: Request, exc: VoiceStudioException):
    logger.warning(
        f"Handled application exception [{exc.error_code.value}]: {exc.message} | Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code.value,
            "message": exc.message,
            "details": exc.details,
        },
    )


# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# Mount static media files
from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.STORAGE_DIR / "generated", exist_ok=True)
app.mount(f"{settings.API_V1_STR}/media", StaticFiles(directory=settings.STORAGE_DIR / "generated"), name="media")

# Observability: Prometheus Metrics
from prometheus_client import make_asgi_app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/live", include_in_schema=False)
def liveness_probe():
    """Returns 200 if the process is running."""
    return {"status": "ok"}

@app.get("/ready", include_in_schema=False)
def readiness_probe():
    """Returns 200 if the application is ready to accept traffic."""
    # In a full production system, check DB connection, storage, etc.
    from app.database.session import SessionLocal
    from sqlalchemy import text
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")

@app.get("/health", include_in_schema=False)
def health_check():
    """Detailed health check."""
    from app.managers.gpu_manager import gpu_manager
    gpu_status = gpu_manager.get_status()
    return {
        "status": "healthy",
        "gpu_available": gpu_status.get("cuda_available", False),
        "device_count": gpu_status.get("device_count", 0)
    }

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API v1",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }
