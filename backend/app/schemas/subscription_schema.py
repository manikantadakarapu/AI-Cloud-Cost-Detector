from pydantic import Field

from app.schemas.common import ApiModel


class SubscriptionResponse(ApiModel):
    subscription_id: str = Field(examples=["00000000-0000-0000-0000-000000000000"])
    display_name: str = Field(examples=["Production Subscription"])


class ResourceGroupResponse(ApiModel):
    name: str = Field(examples=["rg-production-eastus"])
    location: str = Field(examples=["eastus"])
