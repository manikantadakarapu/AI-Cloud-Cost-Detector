import logging
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi_azure_auth.user import User as AzureUser
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, azure_scheme
from app.core.redis import get_analysis_queue
from app.core.settings import Settings, get_settings
from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.services.analysis_job_service import AnalysisJobService
from app.services.analysis_service import AnalysisService
from app.services.azure_advisor_service import AzureAdvisorService
from app.services.azure_auth import AzureCredentialProvider
from app.services.azure_cost_service import AzureCostService
from app.services.azure_monitor_service import AzureMonitorService
from app.services.azure_resource_service import AzureResourceService
from app.services.finops_engine import FinOpsEngine
from app.services.finops_score_service import FinOpsScoreService

logger = logging.getLogger(__name__)


def get_current_user(
    azure_user: AzureUser = Depends(azure_scheme),
    db: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    user_repo = UserRepository(db)
    
    # Extract claims, handling different token formats
    claims = getattr(azure_user, "claims", {}) or {}
    azure_object_id = getattr(azure_user, "oid", None) or claims.get("oid")
    tenant_id = getattr(azure_user, "tid", None) or claims.get("tid")
    email = getattr(azure_user, "preferred_username", None) or claims.get("preferred_username") or claims.get("upn")
    display_name = getattr(azure_user, "name", None) or claims.get("name")
    
    if not azure_object_id:
        logger.error("Authentication failure: JWT token missing 'oid' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing 'oid' claim",
        )
    
    if not tenant_id:
        logger.error("Authentication failure: JWT token missing 'tid' (tenant_id) claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing 'tid' claim",
        )
        
    user = user_repo.get_by_azure_object_id(tenant_id, azure_object_id)
    if not user:
        logger.info(
            "User auto-provisioning triggered", 
            extra={"extra": {"azure_object_id": azure_object_id, "tenant_id": tenant_id}}
        )
        user = user_repo.create(
            tenant_id=tenant_id,
            azure_object_id=azure_object_id,
            email=email or f"{azure_object_id}@unknown.com",
            display_name=display_name or "Unknown User",
            role="viewer"
        )
        db.commit()
        logger.info("User creation successful", extra={"extra": {"user_id": str(user.id), "tenant_id": tenant_id}})
    else:
        user_repo.update_last_login(user.id)
        db.commit()
        logger.info("User login successful", extra={"extra": {"user_id": str(user.id), "tenant_id": tenant_id}})
         
    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        tenant_id=user.tenant_id,
    )


def get_settings_dependency() -> Settings:
    return get_settings()


def get_azure_resource_service(
    settings: Settings = Depends(get_settings_dependency),
) -> AzureResourceService:
    credential_provider = AzureCredentialProvider(settings)
    return AzureResourceService(credential_provider)


def get_azure_cost_service(
    settings: Settings = Depends(get_settings_dependency),
) -> AzureCostService:
    credential_provider = AzureCredentialProvider(settings)
    return AzureCostService(credential_provider)


def get_azure_advisor_service(
    settings: Settings = Depends(get_settings_dependency),
) -> AzureAdvisorService:
    credential_provider = AzureCredentialProvider(settings)
    return AzureAdvisorService(credential_provider)


def get_azure_monitor_service(
    settings: Settings = Depends(get_settings_dependency),
) -> AzureMonitorService:
    credential_provider = AzureCredentialProvider(settings)
    return AzureMonitorService(credential_provider)


def get_finops_engine() -> FinOpsEngine:
    return FinOpsEngine()


def get_finops_score_service() -> FinOpsScoreService:
    return FinOpsScoreService()


def get_analysis_service(
    db: Session = Depends(get_db_session),
    azure_resource_service: AzureResourceService = Depends(get_azure_resource_service),
    azure_cost_service: AzureCostService = Depends(get_azure_cost_service),
    azure_advisor_service: AzureAdvisorService = Depends(get_azure_advisor_service),
    azure_monitor_service: AzureMonitorService = Depends(get_azure_monitor_service),
    finops_engine: FinOpsEngine = Depends(get_finops_engine),
    finops_score_service: FinOpsScoreService = Depends(get_finops_score_service),
) -> Generator[AnalysisService, None, None]:
    yield AnalysisService(
        db,
        azure_resource_service,
        azure_cost_service,
        azure_advisor_service,
        azure_monitor_service,
        finops_engine,
        finops_score_service,
    )


def get_analysis_job_service(
    db: Session = Depends(get_db_session),
) -> AnalysisJobService:
    return AnalysisJobService(db, get_analysis_queue())
