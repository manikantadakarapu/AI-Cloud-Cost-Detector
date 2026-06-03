import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import get_async_redis_connection, get_redis_connection
from app.schemas.progress_schema import AnalysisProgressMessage
from app.websockets.manager import connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()


def progress_channel(tenant_id: str, analysis_id: uuid.UUID | str) -> str:
    return f"tenant:{tenant_id}:analysis-progress:{analysis_id}"


def publish_analysis_progress(message: AnalysisProgressMessage, tenant_id: str) -> None:
    payload = message.model_dump_json()
    redis_connection = get_redis_connection()
    try:
        redis_connection.publish(progress_channel(tenant_id, message.analysis_id), payload)
        logger.info(
            "Published analysis progress",
            extra={"extra": {"tenant_id": tenant_id, "analysis_id": str(message.analysis_id), "status": message.status, "progress": message.progress}},
        )
    finally:
        redis_connection.close()


@router.websocket("/ws/analysis/{analysis_id}")
async def analysis_progress_websocket(websocket: WebSocket, analysis_id: uuid.UUID, tenant_id: str) -> None:
    await connection_manager.connect(tenant_id, analysis_id, websocket)
    redis_connection = get_async_redis_connection()
    pubsub = redis_connection.pubsub()
    channel = progress_channel(tenant_id, analysis_id)
    try:
        await pubsub.subscribe(channel)
        logger.info("WebSocket subscribed to analysis progress", extra={"extra": {"tenant_id": tenant_id, "analysis_id": str(analysis_id)}})
        async for event in pubsub.listen():
            if event.get("type") != "message":
                continue
            data = event.get("data")
            message = data if isinstance(data, str) else json.dumps(data)
            await websocket.send_text(message)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", extra={"extra": {"tenant_id": tenant_id, "analysis_id": str(analysis_id)}})
    finally:
        connection_manager.disconnect(tenant_id, analysis_id, websocket)
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis_connection.close()
