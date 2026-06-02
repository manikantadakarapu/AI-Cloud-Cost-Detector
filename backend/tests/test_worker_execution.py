import uuid

from app.workers import analysis_worker


class FakeDb:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_worker_executes_analysis_service(monkeypatch) -> None:
    analysis_id = uuid.uuid4()
    fake_db = FakeDb()
    executed: list[uuid.UUID] = []

    class FakeAnalysisService:
        def execute_analysis(self, parsed_analysis_id: uuid.UUID) -> None:
            executed.append(parsed_analysis_id)

    monkeypatch.setattr(analysis_worker, "create_worker_session", lambda: fake_db)
    monkeypatch.setattr(analysis_worker, "build_analysis_service", lambda db: FakeAnalysisService())

    analysis_worker.process_analysis_job(str(analysis_id))

    assert executed == [analysis_id]
    assert fake_db.closed is True
