from pydantic import Field

from app.schemas.common import ApiModel


class ResourceMetrics(ApiModel):
    resource_id: str = Field(examples=["/subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm01"])
    cpu_avg: float | None = Field(default=None, examples=[7.5])
    cpu_peak: float | None = Field(default=None, examples=[21.2])
    memory_avg: float | None = Field(default=None, examples=[42.0])
    disk_avg: float | None = Field(default=None, examples=[63.0])
    network_avg: float | None = Field(default=None, examples=[18.5])
