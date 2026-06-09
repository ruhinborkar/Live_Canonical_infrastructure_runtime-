import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from observability.runtime_observer import RuntimeObserver


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active:
                self.active.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message)
        async with self._lock:
            stale: list[WebSocket] = []
            for connection in self.active:
                try:
                    await connection.send_text(payload)
                except Exception:
                    stale.append(connection)
            for connection in stale:
                self.active.remove(connection)


manager = ConnectionManager()
_loop: asyncio.AbstractEventLoop | None = None


def _stage_listener(stage: str, status: str) -> None:
    message = {"type": "stage", "stage": stage, "status": status}
    if _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast(message), _loop)


def register_observer(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop
    RuntimeObserver.clear_listeners()
    RuntimeObserver.add_listener(_stage_listener)


async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
