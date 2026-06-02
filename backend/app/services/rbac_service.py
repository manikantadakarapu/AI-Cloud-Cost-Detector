import logging

from app.core.permissions import ROLE_PERMISSIONS, PermissionEnum, RoleEnum

logger = logging.getLogger(__name__)


class RBACService:
    def __init__(self) -> None:
        pass

    def has_permission(self, role_str: str, permission: PermissionEnum) -> bool:
        try:
            role = RoleEnum(role_str.lower())
        except ValueError:
            logger.warning(
                "Invalid role provided to RBAC service",
                extra={"extra": {"role": role_str, "permission": permission.value}},
            )
            return False

        allowed_permissions = ROLE_PERMISSIONS.get(role, set())
        has_perm = permission in allowed_permissions

        logger.debug(
            "Permission evaluation",
            extra={
                "extra": {
                    "role": role.value,
                    "permission": permission.value,
                    "granted": has_perm,
                }
            },
        )
        return has_perm
