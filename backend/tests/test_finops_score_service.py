from decimal import Decimal

from app.schemas.finding_schema import FinOpsFinding
from app.services.finops_score_service import FinOpsScoreService


def test_score_decreases_for_critical_and_high_findings() -> None:
    service = FinOpsScoreService()
    score = service.calculate(
        findings=[
            FinOpsFinding(
                resource_id="/vm1",
                severity="Critical",
                category="Compute",
                title="Idle VM",
                description="Idle",
                estimated_monthly_savings=Decimal("100"),
                confidence_score=Decimal("0.90"),
            ),
            FinOpsFinding(
                resource_id="/disk1",
                severity="High",
                category="Storage Waste",
                title="Unattached Managed Disk",
                description="Unattached",
                estimated_monthly_savings=Decimal("20"),
                confidence_score=Decimal("0.95"),
            ),
        ],
        total_monthly_cost=Decimal("500"),
    )

    assert score.overall_score < Decimal("100")
    assert score.compute_score < Decimal("100")
    assert score.storage_score < Decimal("100")
    assert score.network_score == Decimal("100.00")
    assert score.recommendation_count == 2
