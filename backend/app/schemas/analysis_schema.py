import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.common import ApiModel


class AnalysisCreateRequest(ApiModel):
    subscription_id: str = Field(examples=["00000000-0000-0000-0000-000000000000"], min_length=1)
    resource_group: str = Field(examples=["rg-production-eastus"], min_length=1)


class AnalysisCreateResponse(ApiModel):
    analysis_id: uuid.UUID = Field(examples=["4f32b798-6f56-4921-9f21-305a2f2a9477"])
    job_id: str | None = Field(default=None, examples=["analysis-4f32b7986f5649219f21305a2f2a9477"])
    status: str = Field(examples=["queued"])
    resource_count: int = Field(default=0, examples=[0])


class AnalysisStatusResponse(ApiModel):
    analysis_id: uuid.UUID = Field(examples=["4f32b798-6f56-4921-9f21-305a2f2a9477"])
    job_id: str | None = Field(default=None, examples=["analysis-4f32b7986f5649219f21305a2f2a9477"])
    status: str = Field(examples=["running"])
    progress_percentage: int = Field(examples=[65])
    current_stage: str | None = Field(default=None, examples=["cost-analysis"])
    error_message: str | None = Field(default=None, examples=["Azure rate limit exceeded"])


class AnalysisResponse(ApiModel):
    id: uuid.UUID
    subscription_id: str
    resource_group: str
    job_id: str | None = None
    status: str
    progress_percentage: int
    current_stage: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
