import logging
from decimal import Decimal

from app.schemas.advisor_schema import AdvisorRecommendation
from app.schemas.cost_schema import ResourceCostBreakdown
from app.schemas.finding_schema import FinOpsFinding
from app.schemas.metrics_schema import ResourceMetrics
from app.schemas.resource_schema import AzureResource

logger = logging.getLogger(__name__)


class FinOpsEngine:
    OVERPROVISIONED_CPU_THRESHOLD = 10.0
    IDLE_CPU_THRESHOLD = 2.0
    OVERPROVISIONED_COST_THRESHOLD = Decimal("50")
    RI_COST_THRESHOLD = Decimal("100")

    def evaluate(
        self,
        *,
        resources: list[AzureResource],
        costs: list[ResourceCostBreakdown],
        metrics: list[ResourceMetrics],
        advisor_recommendations: list[AdvisorRecommendation],
    ) -> list[FinOpsFinding]:
        logger.info(
            "Evaluating deterministic FinOps rules",
            extra={"extra": {"resource_count": len(resources), "cost_count": len(costs), "metric_count": len(metrics)}},
        )
        cost_by_resource = {cost.resource_id.lower(): cost for cost in costs}
        metrics_by_resource = {metric.resource_id.lower(): metric for metric in metrics}
        findings: list[FinOpsFinding] = []

        for resource in resources:
            resource_id = resource.resource_id.lower()
            resource_type = resource.type.lower()
            cost = cost_by_resource.get(resource_id)
            metric = metrics_by_resource.get(resource_id)

            if resource_type == "microsoft.compute/virtualmachines":
                findings.extend(self._evaluate_vm(resource, cost, metric))
            elif resource_type == "microsoft.compute/disks":
                finding = self._evaluate_managed_disk(resource)
                if finding is not None:
                    findings.append(finding)
            elif resource_type == "microsoft.network/publicipaddresses":
                finding = self._evaluate_public_ip(resource)
                if finding is not None:
                    findings.append(finding)

        findings.extend(self._advisor_cost_findings(advisor_recommendations))
        return findings

    def _evaluate_vm(
        self,
        resource: AzureResource,
        cost: ResourceCostBreakdown | None,
        metric: ResourceMetrics | None,
    ) -> list[FinOpsFinding]:
        if metric is None or metric.cpu_avg is None:
            return []

        monthly_cost = cost.monthly_cost if cost is not None else Decimal("0")
        findings: list[FinOpsFinding] = []
        if metric.cpu_avg < self.IDLE_CPU_THRESHOLD:
            findings.append(
                FinOpsFinding(
                    resource_id=resource.resource_id,
                    severity="Critical",
                    category="Compute",
                    title="Idle VM",
                    description="CPU average is below 2 percent across the 30-day analysis window.",
                    estimated_monthly_savings=monthly_cost,
                    confidence_score=Decimal("0.90"),
                )
            )
        elif metric.cpu_avg < self.OVERPROVISIONED_CPU_THRESHOLD and monthly_cost > self.OVERPROVISIONED_COST_THRESHOLD:
            findings.append(
                FinOpsFinding(
                    resource_id=resource.resource_id,
                    severity="High",
                    category="Compute",
                    title="Overprovisioned VM",
                    description="CPU average is below 10 percent while monthly cost exceeds 50.",
                    estimated_monthly_savings=(monthly_cost * Decimal("0.50")),
                    confidence_score=Decimal("0.85"),
                )
            )

        if self._is_reserved_instance_candidate(monthly_cost, metric):
            findings.append(
                FinOpsFinding(
                    resource_id=resource.resource_id,
                    severity="Medium",
                    category="Compute",
                    title="Reserved Instance Candidate",
                    description="VM has stable utilization and monthly cost above the reserved instance threshold.",
                    estimated_monthly_savings=(monthly_cost * Decimal("0.30")),
                    confidence_score=Decimal("0.70"),
                )
            )
        return findings

    @staticmethod
    def _evaluate_managed_disk(resource: AzureResource) -> FinOpsFinding | None:
        if resource.properties.get("managedBy"):
            return None
        return FinOpsFinding(
            resource_id=resource.resource_id,
            severity="High",
            category="Storage Waste",
            title="Unattached Managed Disk",
            description="Managed disk has no associated compute attachment.",
            estimated_monthly_savings=Decimal("0"),
            confidence_score=Decimal("0.95"),
        )

    @staticmethod
    def _evaluate_public_ip(resource: AzureResource) -> FinOpsFinding | None:
        if resource.properties.get("ipConfiguration"):
            return None
        return FinOpsFinding(
            resource_id=resource.resource_id,
            severity="Medium",
            category="Networking Waste",
            title="Unused Public IP",
            description="Public IP address has no associated IP configuration.",
            estimated_monthly_savings=Decimal("0"),
            confidence_score=Decimal("0.95"),
        )

    @staticmethod
    def _advisor_cost_findings(recommendations: list[AdvisorRecommendation]) -> list[FinOpsFinding]:
        findings: list[FinOpsFinding] = []
        for recommendation in recommendations:
            if recommendation.category != "Cost":
                continue
            findings.append(
                FinOpsFinding(
                    resource_id=recommendation.resource_id,
                    severity="Medium",
                    category="Advisor Recommendation",
                    title="Azure Advisor Cost Recommendation",
                    description=recommendation.recommendation,
                    estimated_monthly_savings=recommendation.estimated_savings,
                    confidence_score=Decimal("0.80"),
                )
            )
        return findings

    def _is_reserved_instance_candidate(self, monthly_cost: Decimal, metric: ResourceMetrics) -> bool:
        if metric.cpu_avg is None or metric.cpu_peak is None:
            return False
        stable_utilization = 10 <= metric.cpu_avg <= 70 and (metric.cpu_peak - metric.cpu_avg) <= 40
        return stable_utilization and monthly_cost > self.RI_COST_THRESHOLD
