import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    def _connection_key(self, tenant_id: str, analysis_id: uuid.UUID) -> str:
        return f"{tenant_id}:{analysis_id}"

    async def connect(self, tenant_id: str, analysis_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        key = self._connection_key(tenant_id, analysis_id)
        self._connections[key].add(websocket)

    def disconnect(self, tenant_id: str, analysis_id: uuid.UUID, websocket: WebSocket) -> None:
        key = self._connection_key(tenant_id, analysis_id)
        connections = self._connections.get(key)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(key, None)

    async def broadcast(self, tenant_id: str, analysis_id: uuid.UUID, message: str) -> None:
        key = self._connection_key(tenant_id, analysis_id)
        stale_connections: list[WebSocket] = []
        for websocket in self._connections.get(key, set()):
            try:
                await websocket.send_text(message)
            except RuntimeError:
                stale_connections.append(websocket)
        for websocket in stale_connections:
            self.disconnect(tenant_id, analysis_id, websocket)


connection_manager = ConnectionManager()
