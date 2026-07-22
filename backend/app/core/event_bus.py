import asyncio
from typing import Any, Callable, Dict, List, Set
from app.core.logging import logger


class EventBus:
    """Decoupled Event Bus for publishing and subscribing to real-time job state events."""

    def __init__(self):
        self._listeners: Set[Callable[[str, Dict[str, Any]], None]] = set()

    def subscribe(self, listener: Callable[[str, Dict[str, Any]], None]) -> None:
        self._listeners.add(listener)

    def unsubscribe(self, listener: Callable[[str, Dict[str, Any]], None]) -> None:
        self._listeners.discard(listener)

    def publish(self, event_type: str, payload: Dict[str, Any]) -> None:
        logger.debug(f"EventBus publishing [{event_type}]: {payload}")
        for listener in list(self._listeners):
            try:
                listener(event_type, payload)
            except Exception as e:
                logger.error(f"Error in EventBus listener: {e}")


global_event_bus = EventBus()
