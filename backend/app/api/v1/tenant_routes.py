from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.dependencies.authorization import require_permission
from app.core.auth import AuthenticatedUser
from app.core.permissions import PermissionEnum
from app.db.session import get_db_session
from app.models.analysis import Analysis
from app.models.resource import Resource
from app.models.user import User
from app.schemas.tenant_schema import TenantMeResponse, TenantStatsResponse

router = APIRouter(prefix="/tenant", tags=["Tenant"])


@router.get(
    "/me",
    response_model=TenantMeResponse,
    summary="Get current tenant context",
)
def get_tenant_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> TenantMeResponse:
    return TenantMeResponse(tenant_id=current_user.tenant_id)


@router.get(
    "/stats",
    response_model=TenantStatsResponse,
    summary="Get tenant-wide aggregated statistics",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_ANALYSIS))],
)
def get_tenant_stats(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> TenantStatsResponse:
    tenant_id = current_user.tenant_id
    
    user_count = db.scalar(select(func.count(User.id)).where(User.tenant_id == tenant_id)) or 0
    analysis_count = db.scalar(select(func.count(Analysis.id)).where(Analysis.tenant_id == tenant_id)) or 0
    resource_count = db.scalar(select(func.count(Resource.id)).where(Resource.tenant_id == tenant_id)) or 0
    
    return TenantStatsResponse(
        tenant_id=tenant_id,
        user_count=user_count,
        analysis_count=analysis_count,
        resource_count=resource_count
    )