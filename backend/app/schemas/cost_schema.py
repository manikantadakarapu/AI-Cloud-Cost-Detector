from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import Field

from app.schemas.common import ApiModel


class DailyCost(ApiModel):
    cost_date: date = Field(alias="date", examples=["2026-05-01"])
    amount: Decimal = Field(examples=["12.45"])


class ResourceCostBreakdown(ApiModel):
    resource_id: str = Field(examples=["/subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm01"])
    resource_name: str = Field(examples=["vm01"])
    service_name: str = Field(examples=["Virtual Machines"])
    monthly_cost: Decimal = Field(examples=["123.45"])
    currency: str = Field(default="USD", examples=["USD"])
    billing_period: date = Field(examples=["2026-06-01"])
    daily_costs: list[DailyCost] = Field(default_factory=list)


class CostSummaryResponse(ApiModel):
    total_monthly_cost: Decimal = Field(examples=["1285.44"])
    potential_savings: Decimal = Field(examples=["245.00"])
    resource_count: int = Field(examples=[24])
