import logging
import uuid
from typing import Any

from rq import Retry
from sqlalchemy.orm import Session

from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis_schema import AnalysisCreateRequest, AnalysisCreateResponse, AnalysisStatusResponse

logger = logging.getLogger(__name__)


class AnalysisJobService:
    def __init__(self, db: Session, queue: Any) -> None:
        self.db = db
        self.queue = queue
        self.analysis_repository = AnalysisRepository(db)

    def create_and_enqueue(self, payload: AnalysisCreateRequest) -> AnalysisCreateResponse:
        analysis = self.analysis_repository.create(payload, status="queued")
        job_id = f"analysis-{analysis.id.hex}"
        self.analysis_repository.set_job_id(analysis.id, job_id)
        self.analysis_repository.update_progress(
            analysis.id,
            status="queued",
            progress_percentage=0,
            current_stage=None,
        )
        self.db.commit()

        self.queue.enqueue(
            "app.workers.analysis_worker.process_analysis_job",
            str(analysis.id),
            job_id=job_id,
            retry=Retry(max=3, interval=[10, 30, 60]),
            job_timeout="2h",
            result_ttl=86400,
            failure_ttl=604800,
        )
        logger.info(
            "Queued analysis job",
            extra={"extra": {"analysis_id": str(analysis.id), "job_id": job_id}},
        )
        return AnalysisCreateResponse(
            analysis_id=analysis.id,
            job_id=job_id,
            status="queued",
            resource_count=0,
        )

    def get_status(self, analysis_id: uuid.UUID) -> AnalysisStatusResponse:
        analysis = self.analysis_repository.get(analysis_id)
        if analysis is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Analysis not found")
        return AnalysisStatusResponse(
            analysis_id=analysis.id,
            job_id=analysis.job_id,
            status=analysis.status,
            progress_percentage=analysis.progress_percentage,
            current_stage=analysis.current_stage,
            error_message=analysis.error_message,
        )
