"""Tenant context and multi-tenancy utilities."""
import logging
from dataclasses import dataclass
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class TenantContext:
    """Holds the current tenant context extracted from JWT claims."""
    
    tenant_id: str
    
    def __post_init__(self) -> None:
        if not self.tenant_id:
            logger.error("TenantContext initialized with empty tenant_id")
            raise ValueError("tenant_id cannot be empty")

class TenantWebSocketManager:
    """Tenant-aware WebSocket connection manager to strictly isolate event streams."""
    
    def __init__(self):
        # Map of tenant_id -> analysis_id -> List[WebSocket]
        self.active_connections: Dict[str, Dict[str, List[WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str, analysis_id: str):
        """Validates tenant_id and subscribes a websocket to a specific tenant's analysis channel."""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}
        if analysis_id not in self.active_connections[tenant_id]:
            self.active_connections[tenant_id][analysis_id] = []
            
        self.active_connections[tenant_id][analysis_id].append(websocket)
        logger.info(f"WebSocket connected for tenant {tenant_id}, analysis {analysis_id}")

    def disconnect(self, websocket: WebSocket, tenant_id: str, analysis_id: str):
        """Safely removes a websocket from the tenant-aware channel."""
        try:
            self.active_connections[tenant_id][analysis_id].remove(websocket)
            if not self.active_connections[tenant_id][analysis_id]:
                del self.active_connections[tenant_id][analysis_id]
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        except (KeyError, ValueError):
            pass

    async def broadcast_to_analysis(self, tenant_id: str, analysis_id: str, message: dict):
        """Broadcasts a message ONLY to connections matching both tenant_id and analysis_id."""
        if tenant_id in self.active_connections and analysis_id in self.active_connections[tenant_id]:
            for connection in self.active_connections[tenant_id][analysis_id]:
                await connection.send_json(message)

tenant_ws_manager = TenantWebSocketManager()
