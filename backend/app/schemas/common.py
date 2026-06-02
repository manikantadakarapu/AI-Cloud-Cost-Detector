from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, examples=[False])
    message: str = Field(examples=["Validation failed"])
    details: list[str] = Field(default_factory=list, examples=[["field: error message"]])


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
