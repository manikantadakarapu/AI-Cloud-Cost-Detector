from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.core.auth import AuthenticatedUser
from app.schemas.user_schema import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
