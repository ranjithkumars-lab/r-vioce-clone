from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.event_bus import global_event_bus
from app.core.logging import logger

router = APIRouter(tags=["WebSockets & Events"])


@router.websocket("/ws/jobs")
async def websocket_job_updates(websocket: WebSocket):
    """WebSocket endpoint pushing real-time job progress events to connected UI clients."""
    await websocket.accept()
    logger.info("WebSocket client connected to /ws/jobs event stream.")

    def on_event(event_type: str, payload: dict):
        try:
            import asyncio
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({"event": event_type, "data": payload}),
                asyncio.get_event_loop(),
            )
        except Exception:
            pass

    global_event_bus.subscribe(on_event)
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from /ws/jobs.")
    finally:
        global_event_bus.unsubscribe(on_event)
