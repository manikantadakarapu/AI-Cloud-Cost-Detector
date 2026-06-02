import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import ApiModel


class FinOpsFinding(ApiModel):
    resource_id: str = Field(examples=["/subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm01"])
    severity: str = Field(examples=["High"])
    category: str = Field(examples=["Compute"])
    title: str = Field(examples=["Overprovisioned VM"])
    description: str = Field(examples=["CPU utilization is below 10 percent while monthly cost exceeds threshold."])
    estimated_monthly_savings: Decimal = Field(examples=["61.25"])
    confidence_score: Decimal = Field(examples=["0.85"])


class AnalysisFindingResponse(FinOpsFinding):
    id: uuid.UUID
    analysis_id: uuid.UUID
    created_at: datetime
