import logging
from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.mgmt.resource.subscriptions.models import Subscription
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

from app.core.exceptions import AzureIntegrationError
from app.schemas.resource_schema import AzureResource
from app.schemas.subscription_schema import ResourceGroupResponse, SubscriptionResponse
from app.services.azure_auth import AzureCredentialProvider

logger = logging.getLogger(__name__)


class AzureResourceService:
    def __init__(self, credential_provider: AzureCredentialProvider) -> None:
        self.credential = credential_provider.get_credential()

    def list_subscriptions(self) -> list[SubscriptionResponse]:
        try:
            client = SubscriptionClient(self.credential)
            subscriptions: list[SubscriptionResponse] = []
            for subscription in client.subscriptions.list():
                subscriptions.append(self._subscription_to_schema(subscription))
            return subscriptions
        except AzureError as exc:
            logger.exception("Failed to list Azure subscriptions")
            raise AzureIntegrationError("Unable to retrieve Azure subscriptions", details=[str(exc)]) from exc

    def list_resource_groups(self, subscription_id: str) -> list[ResourceGroupResponse]:
        try:
            client = ResourceManagementClient(self.credential, subscription_id)
            return [self._resource_group_to_schema(group) for group in client.resource_groups.list()]
        except AzureError as exc:
            logger.exception("Failed to list Azure resource groups")
            raise AzureIntegrationError("Unable to retrieve Azure resource groups", details=[str(exc)]) from exc

    def discover_resources(self, *, subscription_id: str, resource_group: str) -> list[AzureResource]:
        query = """
Resources
| where subscriptionId =~ '{subscription_id}'
| where resourceGroup =~ '{resource_group}'
| where type in~ (
    'microsoft.compute/virtualmachines',
    'microsoft.storage/storageaccounts',
    'microsoft.containerservice/managedclusters',
    'microsoft.sql/servers/databases',
    'microsoft.dbforpostgresql/flexibleservers',
    'microsoft.dbformysql/flexibleservers',
    'microsoft.documentdb/databaseaccounts',
    'microsoft.network/loadbalancers',
    'microsoft.network/publicipaddresses',
    'microsoft.compute/disks'
)
| project id, name, type, location, sku, tags, properties
""".format(
            subscription_id=subscription_id.replace("'", "''"),
            resource_group=resource_group.replace("'", "''"),
        )
        request = QueryRequest(subscriptions=[subscription_id], query=query)

        try:
            client = ResourceGraphClient(self.credential)
            response = client.resources(request)
            rows = response.data or []
            return [self._resource_graph_row_to_schema(row) for row in rows]
        except AzureError as exc:
            logger.exception("Failed to discover Azure resources")
            raise AzureIntegrationError("Unable to discover Azure resources", details=[str(exc)]) from exc

    @staticmethod
    def _subscription_to_schema(subscription: Subscription) -> SubscriptionResponse:
        return SubscriptionResponse(
            subscription_id=subscription.subscription_id or "",
            display_name=subscription.display_name or "",
        )

    @staticmethod
    def _resource_group_to_schema(group: ResourceGroup) -> ResourceGroupResponse:
        return ResourceGroupResponse(
            name=group.name or "",
            location=group.location or "",
        )

    @staticmethod
    def _resource_graph_row_to_schema(row: Any) -> AzureResource:
        data = dict(row) if isinstance(row, dict) else row.as_dict()
        sku = data.get("sku")
        sku_name = None
        if isinstance(sku, dict):
            sku_name = sku.get("name") or sku.get("tier")
        elif sku is not None:
            sku_name = str(sku)

        tags = data.get("tags") or {}
        if not isinstance(tags, dict):
            tags = {}
        properties = data.get("properties") or {}
        if not isinstance(properties, dict):
            properties = {}

        return AzureResource(
            resource_id=data.get("id") or "",
            name=data.get("name") or "",
            type=data.get("type") or "",
            location=data.get("location"),
            sku=sku_name,
            tags=tags,
            properties=properties,
        )
