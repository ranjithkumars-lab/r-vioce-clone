from fastapi import APIRouter
from app.api.v1.routes_audio import router as audio_router
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_jobs import router as jobs_router
from app.api.v1.routes_system import router as system_router
from app.api.v1.routes_voices import router as voices_router
from app.api.v1.routes_ws import router as ws_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(voices_router)
api_v1_router.include_router(audio_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(ws_router)
