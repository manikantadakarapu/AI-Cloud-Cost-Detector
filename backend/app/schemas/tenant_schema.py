from pydantic import Field

from app.schemas.common import ApiModel


class TenantMeResponse(ApiModel):
    tenant_id: str = Field(examples=["12345678-abcd-1234-abcd-1234567890ab"])

class TenantStatsResponse(ApiModel):
    tenant_id: str = Field(examples=["12345678-abcd-1234-abcd-1234567890ab"])
    user_count: int = Field(examples=[5])
    analysis_count: int = Field(examples=[12])
    resource_count: int = Field(examples=[1540])