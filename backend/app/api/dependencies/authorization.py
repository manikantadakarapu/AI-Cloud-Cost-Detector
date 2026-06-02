import logging
from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.auth import AuthenticatedUser
from app.core.permissions import PermissionEnum
from app.services.rbac_service import RBACService

logger = logging.getLogger(__name__)

rbac_service = RBACService()


def require_permission(permission: PermissionEnum) -> Callable[..., AuthenticatedUser]:
    def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not rbac_service.has_permission(current_user.role, permission):
            logger.warning(
                "Authorization failure",
                extra={
                    "extra": {
                        "user_id": str(current_user.id),
                        "role": current_user.role,
                        "required_permission": permission.value,
                    }
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"success": False, "message": "Permission denied"},
            )
        return current_user

    return dependency
