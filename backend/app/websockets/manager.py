import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, analysis_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[str(analysis_id)].add(websocket)

    def disconnect(self, analysis_id: uuid.UUID, websocket: WebSocket) -> None:
        connections = self._connections.get(str(analysis_id))
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(str(analysis_id), None)

    async def broadcast(self, analysis_id: uuid.UUID, message: str) -> None:
        stale_connections: list[WebSocket] = []
        for websocket in self._connections.get(str(analysis_id), set()):
            try:
                await websocket.send_text(message)
            except RuntimeError:
                stale_connections.append(websocket)
        for websocket in stale_connections:
            self.disconnect(analysis_id, websocket)


connection_manager = ConnectionManager()
