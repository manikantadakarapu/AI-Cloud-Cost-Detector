from datetime import date
from decimal import Decimal

from app.schemas.advisor_schema import AdvisorRecommendation
from app.schemas.cost_schema import ResourceCostBreakdown
from app.schemas.metrics_schema import ResourceMetrics
from app.schemas.resource_schema import AzureResource
from app.services.finops_engine import FinOpsEngine


def test_overprovisioned_vm_rule_generates_high_compute_finding() -> None:
    engine = FinOpsEngine()
    resource_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm01"

    findings = engine.evaluate(
        resources=[
            AzureResource(
                resource_id=resource_id,
                name="vm01",
                type="microsoft.compute/virtualmachines",
                location="eastus",
                sku="Standard_D4s_v5",
            )
        ],
        costs=[
            ResourceCostBreakdown(
                resource_id=resource_id.lower(),
                resource_name="vm01",
                service_name="Virtual Machines",
                monthly_cost=Decimal("120"),
                currency="USD",
                billing_period=date(2026, 6, 1),
            )
        ],
        metrics=[ResourceMetrics(resource_id=resource_id.lower(), cpu_avg=8.0, cpu_peak=25.0)],
        advisor_recommendations=[],
    )

    assert any(finding.title == "Overprovisioned VM" and finding.severity == "High" for finding in findings)


def test_idle_vm_rule_takes_precedence_over_overprovisioned_rule() -> None:
    engine = FinOpsEngine()
    resource_id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm02"

    findings = engine.evaluate(
        resources=[
            AzureResource(
                resource_id=resource_id,
                name="vm02",
                type="microsoft.compute/virtualmachines",
            )
        ],
        costs=[
            ResourceCostBreakdown(
                resource_id=resource_id.lower(),
                resource_name="vm02",
                service_name="Virtual Machines",
                monthly_cost=Decimal("90"),
                currency="USD",
                billing_period=date(2026, 6, 1),
            )
        ],
        metrics=[ResourceMetrics(resource_id=resource_id.lower(), cpu_avg=1.5, cpu_peak=3.0)],
        advisor_recommendations=[],
    )

    titles = [finding.title for finding in findings]
    assert "Idle VM" in titles
    assert "Overprovisioned VM" not in titles


def test_storage_network_and_advisor_rules_generate_findings() -> None:
    engine = FinOpsEngine()

    findings = engine.evaluate(
        resources=[
            AzureResource(
                resource_id="/disk",
                name="disk01",
                type="microsoft.compute/disks",
                properties={"managedBy": None},
            ),
            AzureResource(
                resource_id="/pip",
                name="pip01",
                type="microsoft.network/publicipaddresses",
                properties={"ipConfiguration": None},
            ),
        ],
        costs=[],
        metrics=[],
        advisor_recommendations=[
            AdvisorRecommendation(
                resource_id="/vm",
                recommendation="Resize virtual machine",
                category="Cost",
                estimated_savings=Decimal("35"),
            )
        ],
    )

    assert {finding.title for finding in findings} == {
        "Unattached Managed Disk",
        "Unused Public IP",
        "Azure Advisor Cost Recommendation",
    }
