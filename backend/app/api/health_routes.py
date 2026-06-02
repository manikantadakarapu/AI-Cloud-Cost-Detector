from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis import check_redis_health
from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.schemas.health_schema import HealthResponse
from app.services.azure_auth import AzureCredentialProvider

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Checks database, Redis, and Azure credential health.",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        database=_database_status(),
        redis=_redis_status(),
        azure=_azure_status(),
    )


def _database_status() -> str:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return "healthy"
    except Exception:
        return "unhealthy"
    finally:
        db.close()


def _redis_status() -> str:
    try:
        return "healthy" if check_redis_health() else "unhealthy"
    except Exception:
        return "unhealthy"


def _azure_status() -> str:
    try:
        credential = AzureCredentialProvider(get_settings()).get_credential()
        credential.get_token("https://management.azure.com/.default")
        return "healthy"
    except Exception:
        return "unhealthy"
