import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import ApiModel


class FinOpsScoreCreate(ApiModel):
    overall_score: Decimal = Field(examples=["78.50"])
    compute_score: Decimal = Field(examples=["72.00"])
    storage_score: Decimal = Field(examples=["88.00"])
    network_score: Decimal = Field(examples=["91.00"])
    recommendation_count: int = Field(examples=[7])


class FinOpsScoreResponse(FinOpsScoreCreate):
    id: uuid.UUID | None = None
    analysis_id: uuid.UUID | None = None
    created_at: datetime | None = None
