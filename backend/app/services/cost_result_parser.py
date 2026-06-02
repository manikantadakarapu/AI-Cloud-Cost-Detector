from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.schemas.cost_schema import DailyCost, ResourceCostBreakdown


def parse_cost_query_result(result: Any, billing_period: date) -> list[ResourceCostBreakdown]:
    columns = [getattr(column, "name", str(column)) for column in getattr(result, "columns", [])]
    rows = getattr(result, "rows", None) or []
    grouped: dict[str, dict[str, Any]] = {}
    daily_costs: dict[str, dict[date, Decimal]] = defaultdict(lambda: defaultdict(Decimal))

    for row in rows:
        values = dict(zip(columns, row, strict=False))
        resource_id = str(values.get("ResourceId") or values.get("resourceId") or "").lower()
        if not resource_id:
            continue
        usage_date = parse_usage_date(values.get("UsageDate") or values.get("Date"))
        amount = Decimal(str(values.get("PreTaxCost") or values.get("Cost") or values.get("totalCost") or 0))
        grouped.setdefault(
            resource_id,
            {
                "resource_id": resource_id,
                "resource_name": str(values.get("ResourceName") or ""),
                "service_name": str(values.get("ServiceName") or "Unknown"),
                "currency": str(values.get("Currency") or "USD"),
                "monthly_cost": Decimal("0"),
            },
        )
        grouped[resource_id]["monthly_cost"] += amount
        if usage_date is not None:
            daily_costs[resource_id][usage_date] += amount

    return [
        ResourceCostBreakdown(
            resource_id=data["resource_id"],
            resource_name=data["resource_name"],
            service_name=data["service_name"],
            monthly_cost=data["monthly_cost"],
            currency=data["currency"],
            billing_period=billing_period,
            daily_costs=[
                DailyCost(date=cost_date, amount=amount)
                for cost_date, amount in sorted(daily_costs[resource_id].items())
            ],
        )
        for resource_id, data in grouped.items()
    ]


def parse_usage_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, int):
        return datetime.strptime(str(value), "%Y%m%d").date()
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return None
