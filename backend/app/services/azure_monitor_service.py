import logging
from datetime import timedelta
from statistics import mean
from typing import Any

from azure.core.exceptions import AzureError
from azure.monitor.query import MetricsQueryClient

from app.core.exceptions import AzureIntegrationError
from app.schemas.metrics_schema import ResourceMetrics
from app.schemas.resource_schema import AzureResource
from app.services.azure_auth import AzureCredentialProvider

logger = logging.getLogger(__name__)


class AzureMonitorService:
    _METRICS_BY_TYPE = {
        "microsoft.compute/virtualmachines": ["Percentage CPU", "Available Memory Bytes", "Disk Read Bytes", "Disk Write Bytes", "Network In Total", "Network Out Total"],
        "microsoft.containerservice/managedclusters": ["node_cpu_usage_percentage", "node_memory_working_set_percentage"],
        "microsoft.sql/servers/databases": ["cpu_percent", "storage_percent"],
        "microsoft.dbforpostgresql/flexibleservers": ["cpu_percent", "memory_percent", "storage_percent"],
        "microsoft.dbformysql/flexibleservers": ["cpu_percent", "memory_percent", "storage_percent"],
    }

    def __init__(self, credential_provider: AzureCredentialProvider) -> None:
        self.credential = credential_provider.get_credential()

    def get_resource_metrics(self, resources: list[AzureResource]) -> list[ResourceMetrics]:
        logger.info("Retrieving Azure Monitor metrics", extra={"extra": {"resource_count": len(resources)}})
        client = MetricsQueryClient(self.credential)
        metrics: list[ResourceMetrics] = []
        try:
            for resource in resources:
                metric_names = self._METRICS_BY_TYPE.get(resource.type.lower())
                if not metric_names:
                    continue
                metrics.append(self._query_single_resource(client, resource.resource_id, metric_names))
            return metrics
        except AzureError as exc:
            logger.exception("Failed to retrieve Azure Monitor metrics")
            raise AzureIntegrationError("Unable to retrieve Azure Monitor metrics") from exc

    def _query_single_resource(
        self,
        client: MetricsQueryClient,
        resource_id: str,
        metric_names: list[str],
    ) -> ResourceMetrics:
        response = client.query_resource(
            resource_id,
            metric_names=metric_names,
            timespan=timedelta(days=30),
            granularity=timedelta(days=1),
            aggregations=["Average", "Maximum"],
        )
        values = {metric.name: self._metric_values(metric) for metric in response.metrics}
        cpu_values = self._first_available(values, ["Percentage CPU", "cpu_percent", "node_cpu_usage_percentage"])
        memory_values = self._first_available(values, ["memory_percent", "node_memory_working_set_percentage", "Available Memory Bytes"])
        disk_values = self._first_available(values, ["storage_percent", "Disk Read Bytes", "Disk Write Bytes"])
        network_values = self._first_available(values, ["Network In Total", "Network Out Total"])
        return ResourceMetrics(
            resource_id=resource_id.lower(),
            cpu_avg=self._average(cpu_values),
            cpu_peak=self._maximum(cpu_values),
            memory_avg=self._average(memory_values),
            disk_avg=self._average(disk_values),
            network_avg=self._average(network_values),
        )

    @staticmethod
    def _metric_values(metric: Any) -> list[float]:
        values: list[float] = []
        for timeseries in getattr(metric, "timeseries", []) or []:
            for data in getattr(timeseries, "data", []) or []:
                value = getattr(data, "average", None)
                if value is None:
                    value = getattr(data, "maximum", None)
                if value is not None:
                    values.append(float(value))
        return values

    @staticmethod
    def _first_available(values: dict[str, list[float]], names: list[str]) -> list[float]:
        merged: list[float] = []
        for name in names:
            merged.extend(values.get(name, []))
        return merged

    @staticmethod
    def _average(values: list[float]) -> float | None:
        return float(mean(values)) if values else None

    @staticmethod
    def _maximum(values: list[float]) -> float | None:
        return max(values) if values else None
