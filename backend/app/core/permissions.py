from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class PermissionEnum(str, Enum):
    VIEW_ANALYSIS = "VIEW_ANALYSIS"
    CREATE_ANALYSIS = "CREATE_ANALYSIS"
    VIEW_COSTS = "VIEW_COSTS"
    VIEW_FINDINGS = "VIEW_FINDINGS"
    VIEW_RESOURCE_INVENTORY = "VIEW_RESOURCE_INVENTORY"
    VIEW_FINOPS_SCORES = "VIEW_FINOPS_SCORES"
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_ROLES = "MANAGE_ROLES"


ROLE_PERMISSIONS: dict[RoleEnum, set[PermissionEnum]] = {
    RoleEnum.ADMIN: {
        PermissionEnum.VIEW_ANALYSIS,
        PermissionEnum.VIEW_FINDINGS,
        PermissionEnum.VIEW_COSTS,
        PermissionEnum.CREATE_ANALYSIS,
        PermissionEnum.VIEW_RESOURCE_INVENTORY,
        PermissionEnum.VIEW_FINOPS_SCORES,
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.MANAGE_ROLES,
    },
    RoleEnum.ANALYST: {
        PermissionEnum.VIEW_ANALYSIS,
        PermissionEnum.VIEW_FINDINGS,
        PermissionEnum.VIEW_COSTS,
        PermissionEnum.CREATE_ANALYSIS,
        PermissionEnum.VIEW_RESOURCE_INVENTORY,
        PermissionEnum.VIEW_FINOPS_SCORES,
    },
    RoleEnum.VIEWER: {
        PermissionEnum.VIEW_ANALYSIS,
        PermissionEnum.VIEW_FINDINGS,
        PermissionEnum.VIEW_COSTS,
        PermissionEnum.VIEW_RESOURCE_INVENTORY,
        PermissionEnum.VIEW_FINOPS_SCORES,
    },
}
