import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.analysis_finding import AnalysisFinding
from app.schemas.finding_schema import FinOpsFinding


class FindingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, *, analysis_id: uuid.UUID, findings: list[FinOpsFinding]) -> list[AnalysisFinding]:
        entities = [
            AnalysisFinding(
                analysis_id=analysis_id,
                resource_id=finding.resource_id,
                severity=finding.severity,
                category=finding.category,
                title=finding.title,
                description=finding.description,
                estimated_monthly_savings=finding.estimated_monthly_savings,
                confidence_score=finding.confidence_score,
            )
            for finding in findings
        ]
        self.db.add_all(entities)
        self.db.flush()
        return entities

    def list_by_analysis(self, analysis_id: uuid.UUID) -> list[AnalysisFinding]:
        statement = (
            select(AnalysisFinding)
            .where(AnalysisFinding.analysis_id == analysis_id)
            .order_by(AnalysisFinding.severity, AnalysisFinding.created_at)
        )
        return list(self.db.scalars(statement))

    def get_potential_savings(self, analysis_id: uuid.UUID) -> Decimal:
        statement = select(func.coalesce(func.sum(AnalysisFinding.estimated_monthly_savings), 0)).where(
            AnalysisFinding.analysis_id == analysis_id
        )
        return Decimal(self.db.scalar(statement) or 0)
