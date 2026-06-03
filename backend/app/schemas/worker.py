from pydantic import BaseModel, Field
from uuid import UUID

class TenantAwareJobPayload(BaseModel):
    """
    Base schema ensuring all background jobs process within a strict tenant context.
    Redis/RQ workers must use this to initialize DB connections and API calls correctly.
    """
    tenant_id: str = Field(..., description="The Azure Entra ID tenant this job is running for.")

class AnalysisJobPayload(TenantAwareJobPayload):
    """
    Specific payload for the long-running FinOps analysis background worker.
    """
    analysis_id: UUID
    subscription_id: str
    resource_group: str