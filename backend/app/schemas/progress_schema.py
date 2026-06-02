import uuid

from pydantic import Field

from app.schemas.common import ApiModel


class AnalysisProgressMessage(ApiModel):
    analysis_id: uuid.UUID = Field(examples=["4f32b798-6f56-4921-9f21-305a2f2a9477"])
    status: str = Field(examples=["running"])
    progress: int = Field(examples=[35])
    stage: str | None = Field(default=None, examples=["resource-discovery"])
    error: str | None = Field(default=None, examples=["Azure rate limit exceeded"])
