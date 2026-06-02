import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.dependencies.authorization import require_permission
from app.core.auth import AuthenticatedUser
from app.core.permissions import PermissionEnum, RoleEnum
from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserResponse, RoleUpdateRequest
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List users",
    description="Requires MANAGE_USERS permission. Admin role required.",
    dependencies=[Depends(require_permission(PermissionEnum.MANAGE_USERS))],
    responses={403: {"description": "Permission denied"}},
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[UserResponse]:
    repo = UserRepository(db)
    return repo.get_all(tenant_id=current_user.tenant_id, skip=skip, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    dependencies=[Depends(require_permission(PermissionEnum.MANAGE_USERS))],
)
def get_user(
    user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    repo = UserRepository(db)
    user = repo.get(tenant_id=current_user.tenant_id, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="Update user role",
    dependencies=[Depends(require_permission(PermissionEnum.MANAGE_ROLES))],
)
def update_user_role(
    user_id: uuid.UUID,
    payload: RoleUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    repo = UserRepository(db)
    audit = AuditService(db)
    
    target_user = repo.get(tenant_id=current_user.tenant_id, user_id=user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
         
    old_role = target_user.role
    
    if current_user.role != RoleEnum.ADMIN.value and payload.role.value == RoleEnum.ADMIN.value:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "message": "Permission denied: Only admins can assign the admin role"}
        )

    # Update role
    repo.update_role(user_id, payload.role.value)
    db.commit()
    
    # Refetch updated user
    updated_user = repo.get(tenant_id=current_user.tenant_id, user_id=user_id)
    
    # Audit log
    audit.log_action(
        actor_user_id=str(current_user.id),
        action="UPDATE_USER_ROLE",
        target_user_id=str(user_id),
        details=f"Changed role from {old_role} to {payload.role.value}",
        tenant_id=current_user.tenant_id
    )
    
    return updated_user
