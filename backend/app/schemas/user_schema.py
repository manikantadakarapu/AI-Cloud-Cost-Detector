import uuid
from pydantic import BaseModel, ConfigDict
from app.core.permissions import RoleEnum


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class RoleUpdateRequest(BaseModel):
    role: RoleEnum
