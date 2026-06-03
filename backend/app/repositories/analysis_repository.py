import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.schemas.analysis_schema import AnalysisCreateRequest


class AnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, tenant_id: str, payload: AnalysisCreateRequest, *, status: str = "pending") -> Analysis:
        analysis = Analysis(
            tenant_id=tenant_id,
            subscription_id=payload.subscription_id,
            resource_group=payload.resource_group,
            status=status,
        )
        self.db.add(analysis)
        self.db.flush()
        return analysis

    def update_status(self, tenant_id: str, analysis_id: uuid.UUID, status: str) -> None:
        analysis = self._get_tenant_scoped(tenant_id, analysis_id)
        if analysis is not None:
            analysis.status = status
            self.db.flush()

    def set_job_id(self, tenant_id: str, analysis_id: uuid.UUID, job_id: str) -> None:
        analysis = self._get_tenant_scoped(tenant_id, analysis_id)
        if analysis is not None:
            analysis.job_id = job_id
            self.db.flush()

    def get(self, tenant_id: str, analysis_id: uuid.UUID) -> Analysis | None:
        return self._get_tenant_scoped(tenant_id, analysis_id)

    def get_by_job_id(self, tenant_id: str, job_id: str) -> Analysis | None:
        statement = select(Analysis).where((Analysis.tenant_id == tenant_id) & (Analysis.job_id == job_id))
        return self.db.scalar(statement)

    def update_progress(
        self,
        tenant_id: str,
        analysis_id: uuid.UUID,
        *,
        status: str,
        progress_percentage: int,
        current_stage: str | None,
        error_message: str | None = None,
    ) -> Analysis | None:
        analysis = self._get_tenant_scoped(tenant_id, analysis_id)
        if analysis is None:
            return None
        analysis.status = status
        analysis.progress_percentage = progress_percentage
        analysis.current_stage = current_stage
        analysis.error_message = error_message
        if status == "running" and analysis.started_at is None:
            analysis.started_at = datetime.now(timezone.utc)
        if status in {"completed", "failed"}:
            analysis.completed_at = datetime.now(timezone.utc)
        self.db.flush()
        return analysis

    def _get_tenant_scoped(self, tenant_id: str, analysis_id: uuid.UUID) -> Analysis | None:
        statement = select(Analysis).where(
            (Analysis.tenant_id == tenant_id) & (Analysis.id == analysis_id)
        )
        return self.db.scalar(statement)
