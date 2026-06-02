import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.analysis_cost import AnalysisCost
from app.schemas.cost_schema import ResourceCostBreakdown


class CostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, *, analysis_id: uuid.UUID, costs: list[ResourceCostBreakdown]) -> list[AnalysisCost]:
        entities = [
            AnalysisCost(
                analysis_id=analysis_id,
                resource_id=cost.resource_id,
                resource_name=cost.resource_name,
                service_name=cost.service_name,
                cost_amount=cost.monthly_cost,
                currency=cost.currency,
                billing_period=cost.billing_period,
            )
            for cost in costs
        ]
        self.db.add_all(entities)
        self.db.flush()
        return entities

    def get_total_monthly_cost(self, analysis_id: uuid.UUID) -> Decimal:
        statement = select(func.coalesce(func.sum(AnalysisCost.cost_amount), 0)).where(
            AnalysisCost.analysis_id == analysis_id
        )
        return Decimal(self.db.scalar(statement) or 0)

    def list_by_analysis(self, analysis_id: uuid.UUID) -> list[AnalysisCost]:
        statement = select(AnalysisCost).where(AnalysisCost.analysis_id == analysis_id)
        return list(self.db.scalars(statement))

    def latest_billing_period(self, analysis_id: uuid.UUID) -> date | None:
        statement = select(func.max(AnalysisCost.billing_period)).where(AnalysisCost.analysis_id == analysis_id)
        return self.db.scalar(statement)
