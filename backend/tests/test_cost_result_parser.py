from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.cost_result_parser import parse_cost_query_result


def test_parse_cost_query_result_groups_daily_costs_by_resource() -> None:
    result = SimpleNamespace(
        columns=[
            SimpleNamespace(name="UsageDate"),
            SimpleNamespace(name="PreTaxCost"),
            SimpleNamespace(name="ResourceId"),
            SimpleNamespace(name="ResourceName"),
            SimpleNamespace(name="ServiceName"),
            SimpleNamespace(name="Currency"),
        ],
        rows=[
            [20260501, 10.25, "/Resource/One", "one", "Virtual Machines", "USD"],
            [20260502, 4.75, "/Resource/One", "one", "Virtual Machines", "USD"],
            [20260501, 3.00, "/Resource/Two", "two", "Storage", "USD"],
        ],
    )

    costs = parse_cost_query_result(result, date(2026, 6, 1))

    assert len(costs) == 2
    first = next(cost for cost in costs if cost.resource_id == "/resource/one")
    assert first.monthly_cost == Decimal("15.0")
    assert len(first.daily_costs) == 2
