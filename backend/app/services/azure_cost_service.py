import logging
from datetime import date, datetime, timedelta, timezone

from azure.core.exceptions import AzureError
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryAggregation,
    QueryDataset,
    QueryDefinition,
    QueryGrouping,
    QueryTimePeriod,
)

from app.core.exceptions import AzureIntegrationError
from app.schemas.cost_schema import ResourceCostBreakdown
from app.services.azure_auth import AzureCredentialProvider
from app.services.cost_result_parser import parse_cost_query_result

logger = logging.getLogger(__name__)


class AzureCostService:
    def __init__(self, credential_provider: AzureCredentialProvider) -> None:
        self.credential = credential_provider.get_credential()

    def get_subscription_costs(self, subscription_id: str) -> list[ResourceCostBreakdown]:
        scope = f"/subscriptions/{subscription_id}"
        return self._query_cost_breakdown(scope)

    def get_resource_group_costs(self, subscription_id: str, resource_group: str) -> list[ResourceCostBreakdown]:
        scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
        return self._query_cost_breakdown(scope)

    def get_resource_cost_breakdown(
        self,
        *,
        subscription_id: str,
        resource_group: str | None = None,
    ) -> list[ResourceCostBreakdown]:
        if resource_group:
            return self.get_resource_group_costs(subscription_id, resource_group)
        return self.get_subscription_costs(subscription_id)

    def _query_cost_breakdown(self, scope: str) -> list[ResourceCostBreakdown]:
        logger.info("Retrieving Azure cost data", extra={"extra": {"scope": scope}})
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=30)
        parameters = QueryDefinition(
            type="Usage",
            timeframe="Custom",
            time_period=QueryTimePeriod(from_property=start_date, to=end_date),
            dataset=QueryDataset(
                granularity="Daily",
                aggregation={"totalCost": QueryAggregation(name="PreTaxCost", function="Sum")},
                grouping=[
                    QueryGrouping(type="Dimension", name="ResourceId"),
                    QueryGrouping(type="Dimension", name="ResourceName"),
                    QueryGrouping(type="Dimension", name="ServiceName"),
                ],
            ),
        )

        try:
            client = CostManagementClient(self.credential)
            result = client.query.usage(scope=scope, parameters=parameters)
            return parse_cost_query_result(result, end_date.replace(day=1))
        except AzureError as exc:
            logger.exception("Failed to retrieve Azure cost data", extra={"extra": {"scope": scope}})
            raise AzureIntegrationError("Unable to retrieve Azure cost data") from exc
