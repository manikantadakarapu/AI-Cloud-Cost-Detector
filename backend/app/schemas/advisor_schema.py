from decimal import Decimal

from pydantic import Field

from app.schemas.common import ApiModel


class AdvisorRecommendation(ApiModel):
    resource_id: str = Field(examples=["/subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm01"])
    recommendation: str = Field(examples=["Right-size or shutdown underutilized virtual machines"])
    category: str = Field(examples=["Cost"])
    estimated_savings: Decimal = Field(default=Decimal("0"), examples=["42.50"])
