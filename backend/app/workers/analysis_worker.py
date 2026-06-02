import logging
import uuid

logger = logging.getLogger(__name__)


def process_analysis_job(analysis_id: str) -> None:
    parsed_analysis_id = uuid.UUID(analysis_id)
    db = create_worker_session()
    try:
        logger.info("Worker started analysis job", extra={"extra": {"analysis_id": analysis_id}})
        service = build_analysis_service(db)
        service.execute_analysis(parsed_analysis_id)
        logger.info("Worker finished analysis job", extra={"extra": {"analysis_id": analysis_id}})
    except Exception:
        logger.exception("Worker failed unexpectedly", extra={"extra": {"analysis_id": analysis_id}})
    finally:
        db.close()


def create_worker_session():
    from app.db.session import SessionLocal

    return SessionLocal()


def build_analysis_service(db):
    from app.core.settings import get_settings
    from app.services.analysis_service import AnalysisService
    from app.services.azure_advisor_service import AzureAdvisorService
    from app.services.azure_auth import AzureCredentialProvider
    from app.services.azure_cost_service import AzureCostService
    from app.services.azure_monitor_service import AzureMonitorService
    from app.services.azure_resource_service import AzureResourceService
    from app.services.finops_engine import FinOpsEngine
    from app.services.finops_score_service import FinOpsScoreService

    credential_provider = AzureCredentialProvider(get_settings())
    return AnalysisService(
        db,
        AzureResourceService(credential_provider),
        AzureCostService(credential_provider),
        AzureAdvisorService(credential_provider),
        AzureMonitorService(credential_provider),
        FinOpsEngine(),
        FinOpsScoreService(),
    )
