import logging
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.cost_repository import CostRepository
from app.repositories.finding_repository import FindingRepository
from app.repositories.resource_repository import ResourceRepository
from app.repositories.score_repository import ScoreRepository
from app.schemas.analysis_schema import AnalysisCreateRequest, AnalysisCreateResponse
from app.schemas.analysis_schema import AnalysisStatusResponse
from app.schemas.cost_schema import CostSummaryResponse
from app.schemas.finding_schema import AnalysisFindingResponse
from app.schemas.progress_schema import AnalysisProgressMessage
from app.schemas.score_schema import FinOpsScoreResponse
from app.services.azure_advisor_service import AzureAdvisorService
from app.services.azure_cost_service import AzureCostService
from app.services.azure_monitor_service import AzureMonitorService
from app.services.azure_resource_service import AzureResourceService
from app.services.finops_engine import FinOpsEngine
from app.services.finops_score_service import FinOpsScoreService
from app.utils.retry import run_with_retries
from app.websockets.progress import publish_analysis_progress

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(
        self,
        db: Session,
        azure_resource_service: AzureResourceService,
        azure_cost_service: AzureCostService,
        azure_advisor_service: AzureAdvisorService,
        azure_monitor_service: AzureMonitorService,
        finops_engine: FinOpsEngine,
        finops_score_service: FinOpsScoreService,
    ) -> None:
        self.db = db
        self.analysis_repository = AnalysisRepository(db)
        self.resource_repository = ResourceRepository(db)
        self.cost_repository = CostRepository(db)
        self.finding_repository = FindingRepository(db)
        self.score_repository = ScoreRepository(db)
        self.azure_resource_service = azure_resource_service
        self.azure_cost_service = azure_cost_service
        self.azure_advisor_service = azure_advisor_service
        self.azure_monitor_service = azure_monitor_service
        self.finops_engine = finops_engine
        self.finops_score_service = finops_score_service

    def start_analysis(self, payload: AnalysisCreateRequest) -> AnalysisCreateResponse:
        analysis = self.analysis_repository.create(payload, status="queued")
        self.db.commit()
        return AnalysisCreateResponse(
            analysis_id=analysis.id,
            job_id=analysis.job_id,
            status=analysis.status,
            resource_count=0,
        )

    def execute_analysis(self, analysis_id: uuid.UUID) -> None:
        analysis = self.analysis_repository.get(analysis_id)
        if analysis is None:
            raise NotFoundError("Analysis not found")

        try:
            self._update_progress(analysis_id, status="running", progress=10, stage="resource-discovery")
            resources = run_with_retries(
                "resource-discovery",
                lambda: self.azure_resource_service.discover_resources(
                    subscription_id=analysis.subscription_id,
                    resource_group=analysis.resource_group,
                ),
            )
            self.resource_repository.bulk_create(analysis_id=analysis.id, resources=resources)
            self.db.commit()

            self._update_progress(analysis_id, status="running", progress=30, stage="cost-analysis")
            costs = run_with_retries(
                "cost-analysis",
                lambda: self.azure_cost_service.get_resource_cost_breakdown(
                    subscription_id=analysis.subscription_id,
                    resource_group=analysis.resource_group,
                ),
            )
            self.cost_repository.bulk_create(analysis_id=analysis.id, costs=costs)
            self.db.commit()

            self._update_progress(analysis_id, status="running", progress=50, stage="advisor-analysis")
            advisor_recommendations = run_with_retries(
                "advisor-analysis",
                lambda: self.azure_advisor_service.get_recommendations(analysis.subscription_id),
            )

            self._update_progress(analysis_id, status="running", progress=70, stage="metrics-analysis")
            metrics = run_with_retries(
                "metrics-analysis",
                lambda: self.azure_monitor_service.get_resource_metrics(resources),
            )

            self._update_progress(analysis_id, status="running", progress=85, stage="finops-analysis")
            findings = self.finops_engine.evaluate(
                resources=resources,
                costs=costs,
                metrics=metrics,
                advisor_recommendations=advisor_recommendations,
            )
            self.finding_repository.bulk_create(analysis_id=analysis.id, findings=findings)
            self.db.commit()

            self._update_progress(analysis_id, status="running", progress=95, stage="scoring")
            total_cost = self.cost_repository.get_total_monthly_cost(analysis.id)
            score = self.finops_score_service.calculate(findings=findings, total_monthly_cost=total_cost)
            self.score_repository.create(analysis_id=analysis.id, score=score)
            self.db.commit()

            self._update_progress(analysis_id, status="completed", progress=100, stage="completed")
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed to execute analysis", extra={"extra": {"analysis_id": str(analysis_id)}})
            self._update_progress(
                analysis_id,
                status="failed",
                progress=100,
                stage=None,
                error_message=str(exc),
            )

    def get_findings(self, analysis_id: uuid.UUID) -> list[AnalysisFindingResponse]:
        findings = self.finding_repository.list_by_analysis(analysis_id)
        return [AnalysisFindingResponse.model_validate(finding) for finding in findings]

    def get_cost_summary(self, analysis_id: uuid.UUID) -> CostSummaryResponse:
        return CostSummaryResponse(
            total_monthly_cost=self.cost_repository.get_total_monthly_cost(analysis_id),
            potential_savings=self.finding_repository.get_potential_savings(analysis_id),
            resource_count=self.resource_repository.count_by_analysis(analysis_id),
        )

    def get_score(self, analysis_id: uuid.UUID) -> FinOpsScoreResponse:
        score = self.score_repository.get_by_analysis(analysis_id)
        if score is None:
            raise NotFoundError("FinOps score not found for analysis")
        return FinOpsScoreResponse.model_validate(score)

    def get_status(self, analysis_id: uuid.UUID) -> AnalysisStatusResponse:
        analysis = self.analysis_repository.get(analysis_id)
        if analysis is None:
            raise NotFoundError("Analysis not found")
        return AnalysisStatusResponse(
            analysis_id=analysis.id,
            job_id=analysis.job_id,
            status=analysis.status,
            progress_percentage=analysis.progress_percentage,
            current_stage=analysis.current_stage,
            error_message=analysis.error_message,
        )

    def _update_progress(
        self,
        analysis_id: uuid.UUID,
        *,
        status: str,
        progress: int,
        stage: str | None,
        error_message: str | None = None,
    ) -> None:
        self.analysis_repository.update_progress(
            analysis_id,
            status=status,
            progress_percentage=progress,
            current_stage=stage,
            error_message=error_message,
        )
        self.db.commit()
        publish_analysis_progress(
            AnalysisProgressMessage(
                analysis_id=analysis_id,
                status=status,
                progress=progress,
                stage=stage,
                error=error_message,
            )
        )
        logger.info(
            "Analysis progress updated",
            extra={"extra": {"analysis_id": str(analysis_id), "status": status, "progress": progress, "stage": stage}},
        )
