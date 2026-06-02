from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.analysis import Analysis
from app.schemas.analysis_schema import AnalysisCreateRequest
from app.services.analysis_job_service import AnalysisJobService


class FakeQueue:
    def __init__(self) -> None:
        self.enqueued: list[dict[str, object]] = []

    def enqueue(self, func: object, *args: object, **kwargs: object) -> None:
        self.enqueued.append({"func": func, "args": args, "kwargs": kwargs})


def test_create_and_enqueue_returns_immediately_with_job_id() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Analysis.__table__.create(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    queue = FakeQueue()

    service = AnalysisJobService(session, queue)
    response = service.create_and_enqueue(
        AnalysisCreateRequest(subscription_id="00000000-0000-0000-0000-000000000000", resource_group="rg-prod")
    )

    assert response.status == "queued"
    assert response.job_id is not None
    assert response.resource_count == 0
    assert len(queue.enqueued) == 1
    assert queue.enqueued[0]["args"] == (str(response.analysis_id),)
    assert queue.enqueued[0]["kwargs"]["job_id"] == response.job_id


def test_get_status_reads_persisted_progress() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Analysis.__table__.create(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    queue = FakeQueue()

    service = AnalysisJobService(session, queue)
    created = service.create_and_enqueue(
        AnalysisCreateRequest(subscription_id="sub", resource_group="rg")
    )
    analysis = session.get(Analysis, created.analysis_id)
    assert analysis is not None
    analysis.status = "running"
    analysis.progress_percentage = 65
    analysis.current_stage = "cost-analysis"
    session.commit()

    status = service.get_status(created.analysis_id)

    assert status.status == "running"
    assert status.progress_percentage == 65
    assert status.current_stage == "cost-analysis"
