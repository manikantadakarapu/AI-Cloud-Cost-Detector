import uuid

import pytest

from app.websockets.manager import ConnectionManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[str] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_text(self, message: str) -> None:
        self.messages.append(message)


@pytest.mark.anyio
async def test_connection_manager_broadcasts_to_multiple_clients() -> None:
    manager = ConnectionManager()
    analysis_id = uuid.uuid4()
    first = FakeWebSocket()
    second = FakeWebSocket()

    await manager.connect(analysis_id, first)
    await manager.connect(analysis_id, second)
    await manager.broadcast(analysis_id, '{"status":"running"}')

    assert first.accepted is True
    assert second.accepted is True
    assert first.messages == ['{"status":"running"}']
    assert second.messages == ['{"status":"running"}']

    manager.disconnect(analysis_id, first)
    await manager.broadcast(analysis_id, '{"status":"completed"}')

    assert first.messages == ['{"status":"running"}']
    assert second.messages[-1] == '{"status":"completed"}'
