from fastapi import APIRouter, Depends, Path

from app.api.dependencies import get_azure_resource_service
from app.api.dependencies.authorization import require_permission
from app.core.permissions import PermissionEnum
from app.schemas.subscription_schema import ResourceGroupResponse, SubscriptionResponse
from app.services.azure_resource_service import AzureResourceService

router = APIRouter(tags=["Azure Discovery"])


@router.get(
    "/subscriptions",
    response_model=list[SubscriptionResponse],
    summary="Get Azure subscriptions",
    description="Retrieves subscriptions available to the configured Azure SDK credential.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_RESOURCE_INVENTORY))],
    responses={403: {"description": "Permission denied"}, 502: {"description": "Azure integration error"}},
)
def get_subscriptions(
    service: AzureResourceService = Depends(get_azure_resource_service),
) -> list[SubscriptionResponse]:
    return service.list_subscriptions()


@router.get(
    "/resource-groups/{subscription_id}",
    response_model=list[ResourceGroupResponse],
    summary="Get Azure resource groups",
    description="Retrieves resource groups for a subscription using Azure Resource Management SDK.",
    dependencies=[Depends(require_permission(PermissionEnum.VIEW_RESOURCE_INVENTORY))],
    responses={403: {"description": "Permission denied"}, 502: {"description": "Azure integration error"}},
)
def get_resource_groups(
    subscription_id: str = Path(
        ...,
        description="Azure subscription identifier.",
        examples=["00000000-0000-0000-0000-000000000000"],
    ),
    service: AzureResourceService = Depends(get_azure_resource_service),
) -> list[ResourceGroupResponse]:
    return service.list_resource_groups(subscription_id)
