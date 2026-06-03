import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.finops_score import FinOpsScore
from app.schemas.score_schema import FinOpsScoreCreate


class ScoreRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, tenant_id: str, analysis_id: uuid.UUID, score: FinOpsScoreCreate) -> FinOpsScore:
        entity = FinOpsScore(
            tenant_id=tenant_id,
            analysis_id=analysis_id,
            overall_score=score.overall_score,
            compute_score=score.compute_score,
            storage_score=score.storage_score,
            network_score=score.network_score,
            recommendation_count=score.recommendation_count,
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_analysis(self, tenant_id: str, analysis_id: uuid.UUID) -> FinOpsScore | None:
        statement = select(FinOpsScore).where(
            (FinOpsScore.tenant_id == tenant_id) & (FinOpsScore.analysis_id == analysis_id)
        )
        return self.db.scalar(statement)
