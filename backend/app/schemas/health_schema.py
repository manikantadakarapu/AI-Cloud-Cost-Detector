from pydantic import Field

from app.schemas.common import ApiModel


class HealthResponse(ApiModel):
    database: str = Field(examples=["healthy"])
    redis: str = Field(examples=["healthy"])
    azure: str = Field(examples=["healthy"])
