import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.event_bus import global_event_bus
from app.core.logging import logger

router = APIRouter(tags=["WebSockets & Events"])


@router.websocket("/ws/jobs")
async def websocket_job_updates(websocket: WebSocket):
    """WebSocket endpoint pushing real-time job progress events to connected UI clients."""
    await websocket.accept()
    logger.info("WebSocket client connected to /ws/jobs event stream.")
    
    loop = asyncio.get_running_loop()

    def on_event(event_type: str, payload: dict):
        async def send():
            try:
                await websocket.send_json({"event": event_type, "data": payload})
            except Exception as send_err:
                logger.debug(f"WebSocket send error: {send_err}")

        try:
            asyncio.run_coroutine_threadsafe(send(), loop)
        except Exception as err:
            logger.debug(f"Failed to schedule WS event: {err}")

    global_event_bus.subscribe(on_event)
    try:
        while True:
            # Send keep-alive ping every 15 seconds to prevent proxy connection timeouts
            await asyncio.sleep(15)
            await websocket.send_json({"event": "ping", "data": {}})
    except (WebSocketDisconnect, Exception) as e:
        logger.info(f"WebSocket client disconnected from /ws/jobs ({e}).")
    finally:
        global_event_bus.unsubscribe(on_event)
