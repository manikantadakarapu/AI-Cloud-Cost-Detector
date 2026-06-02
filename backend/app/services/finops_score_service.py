import logging
from decimal import Decimal, ROUND_HALF_UP

from app.schemas.finding_schema import FinOpsFinding
from app.schemas.score_schema import FinOpsScoreCreate

logger = logging.getLogger(__name__)


class FinOpsScoreService:
    _SEVERITY_WEIGHTS = {
        "Critical": Decimal("18"),
        "High": Decimal("10"),
        "Medium": Decimal("5"),
        "Low": Decimal("2"),
    }

    def calculate(self, *, findings: list[FinOpsFinding], total_monthly_cost: Decimal) -> FinOpsScoreCreate:
        logger.info(
            "Calculating FinOps score",
            extra={"extra": {"finding_count": len(findings), "total_monthly_cost": str(total_monthly_cost)}},
        )
        compute_findings = self._filter_category(findings, ("Compute", "Advisor Recommendation"))
        storage_findings = self._filter_category(findings, ("Storage", "Storage Waste"))
        network_findings = self._filter_category(findings, ("Network", "Networking Waste"))

        compute_score = self._score_for_findings(compute_findings, total_monthly_cost)
        storage_score = self._score_for_findings(storage_findings, total_monthly_cost)
        network_score = self._score_for_findings(network_findings, total_monthly_cost)
        overall_score = ((compute_score + storage_score + network_score) / Decimal("3")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return FinOpsScoreCreate(
            overall_score=overall_score,
            compute_score=compute_score,
            storage_score=storage_score,
            network_score=network_score,
            recommendation_count=len(findings),
        )

    def _score_for_findings(self, findings: list[FinOpsFinding], total_monthly_cost: Decimal) -> Decimal:
        deduction = sum((self._SEVERITY_WEIGHTS.get(finding.severity, Decimal("3")) for finding in findings), Decimal("0"))
        potential_savings = sum((finding.estimated_monthly_savings for finding in findings), Decimal("0"))
        if total_monthly_cost > 0:
            savings_ratio = min(potential_savings / total_monthly_cost, Decimal("1"))
            deduction += savings_ratio * Decimal("20")
        score = max(Decimal("0"), Decimal("100") - deduction)
        return score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _filter_category(findings: list[FinOpsFinding], categories: tuple[str, ...]) -> list[FinOpsFinding]:
        return [finding for finding in findings if finding.category in categories]
