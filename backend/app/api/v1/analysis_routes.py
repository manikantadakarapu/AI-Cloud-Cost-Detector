import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_analysis_job_service, get_analysis_service
from app.api.dependencies.authorization import require_permission
from app.api.dependencies.core import get_current_user
from app.core.auth import AuthenticatedUser
from app.core.permissions import PermissionEnum
from app.schemas.analysis_schema import AnalysisCreateRequest, AnalysisCreateResponse, AnalysisStatusResponse, AnalysisResponse
from app.schemas.cost_schema import CostSummaryResponse
from app.schemas.finding_schema import AnalysisFindingResponse
from app.schemas.score_schema import FinOpsScoreResponse
from app.services.analysis_job_service import AnalysisJobService
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["Analysis"])


@router.get(
    "/analyses",
    response_model=list[AnalysisResponse],
    summary="List analyses",
    description="Returns all analyses for the current tenant, sorted by most recent first.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_ANALYSIS))],
)
def list_analyses(
    skip: int = 0,
    limit: int = 50,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AnalysisResponse]:
    return service.list_analyses(current_user.tenant_id, skip=skip, limit=limit)


@router.post(
    "/analysis",
    response_model=AnalysisCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start resource analysis",
    description="Creates an analysis record, queues background analysis execution, and returns immediately.",
    dependencies=[Depends(require_permission(PermissionEnum.CREATE_ANALYSIS))],
    responses={502: {"description": "Azure integration error"}},
)
def start_analysis(
    payload: AnalysisCreateRequest,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnalysisCreateResponse:
    return service.create_and_enqueue(current_user.tenant_id, payload)


@router.get(
    "/analysis/{analysis_id}/status",
    response_model=AnalysisStatusResponse,
    summary="Get analysis status",
    description="Returns queued/running/completed/failed state and current progress for a background analysis.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_ANALYSIS))],
    responses={404: {"description": "Analysis not found"}},
)
def get_analysis_status(
    analysis_id: uuid.UUID,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnalysisStatusResponse:
    return service.get_status(current_user.tenant_id, analysis_id)


@router.get(
    "/analysis/{analysis_id}/findings",
    response_model=list[AnalysisFindingResponse],
    summary="Get analysis findings",
    description="Returns deterministic FinOps findings generated for an analysis.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_FINDINGS))],
    responses={404: {"description": "Analysis not found"}},
)
def get_analysis_findings(
    analysis_id: uuid.UUID,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AnalysisFindingResponse]:
    return service.get_findings(current_user.tenant_id, analysis_id)


@router.get(
    "/analysis/{analysis_id}/cost-summary",
    response_model=CostSummaryResponse,
    summary="Get analysis cost summary",
    description="Returns total monthly cost, estimated potential savings, and discovered resource count for an analysis.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_COSTS))],
    responses={404: {"description": "Analysis not found"}},
)
def get_analysis_cost_summary(
    analysis_id: uuid.UUID,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> CostSummaryResponse:
    return service.get_cost_summary(current_user.tenant_id, analysis_id)


@router.get(
    "/analysis/{analysis_id}/score",
    response_model=FinOpsScoreResponse,
    summary="Get FinOps score",
    description="Returns the calculated deterministic FinOps score for an analysis.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_ANALYSIS))],
    responses={403: {"description": "Permission denied"}, 404: {"description": "FinOps score not found"}},
)
def get_analysis_score(
    analysis_id: uuid.UUID,
    service: AnalysisService = Depends(get_analysis_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FinOpsScoreResponse:
    return service.get_score(current_user.tenant_id, analysis_id)
