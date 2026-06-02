from typing import Any

from pydantic import Field

from app.schemas.common import ApiModel


class AzureResource(ApiModel):
    resource_id: str = Field(examples=["/subscriptions/.../resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm01"])
    name: str = Field(examples=["vm01"])
    type: str = Field(examples=["microsoft.compute/virtualmachines"])
    location: str | None = Field(default=None, examples=["eastus"])
    sku: str | None = Field(default=None, examples=["Standard_D2s_v5"])
    tags: dict[str, Any] = Field(default_factory=dict, examples=[{"owner": "finops"}])
    properties: dict[str, Any] = Field(default_factory=dict)
