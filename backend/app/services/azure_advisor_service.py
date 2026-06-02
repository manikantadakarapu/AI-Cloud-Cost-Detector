import logging
from decimal import Decimal
from typing import Any

from azure.core.exceptions import AzureError
from azure.mgmt.advisor import AdvisorManagementClient

from app.core.exceptions import AzureIntegrationError
from app.schemas.advisor_schema import AdvisorRecommendation
from app.services.azure_auth import AzureCredentialProvider

logger = logging.getLogger(__name__)


class AzureAdvisorService:
    _CATEGORIES = {"Cost", "HighAvailability", "Performance"}

    def __init__(self, credential_provider: AzureCredentialProvider) -> None:
        self.credential = credential_provider.get_credential()

    def get_recommendations(self, subscription_id: str) -> list[AdvisorRecommendation]:
        logger.info("Retrieving Azure Advisor recommendations", extra={"extra": {"subscription_id": subscription_id}})
        try:
            client = AdvisorManagementClient(self.credential, subscription_id)
            recommendations: list[AdvisorRecommendation] = []
            for item in client.recommendations.list():
                recommendation = self._to_schema(item)
                if recommendation.category in self._CATEGORIES:
                    recommendations.append(recommendation)
            return recommendations
        except AzureError as exc:
            logger.exception(
                "Failed to retrieve Azure Advisor recommendations",
                extra={"extra": {"subscription_id": subscription_id}},
            )
            raise AzureIntegrationError("Unable to retrieve Azure Advisor recommendations") from exc

    @staticmethod
    def _to_schema(item: Any) -> AdvisorRecommendation:
        extended_properties = getattr(item, "extended_properties", None) or {}
        short_description = getattr(item, "short_description", None)
        recommendation = ""
        if short_description is not None:
            recommendation = getattr(short_description, "problem", None) or getattr(short_description, "solution", None) or ""
        savings = (
            extended_properties.get("annualSavingsAmount")
            or extended_properties.get("savingsAmount")
            or extended_properties.get("monthlySavingsAmount")
            or 0
        )
        monthly_savings = Decimal(str(savings))
        if "annualSavingsAmount" in extended_properties:
            monthly_savings = monthly_savings / Decimal("12")
        return AdvisorRecommendation(
            resource_id=str(getattr(item, "impacted_value", None) or getattr(item, "id", "") or ""),
            recommendation=recommendation or str(getattr(item, "recommendation_type_id", "") or "Azure Advisor recommendation"),
            category=str(getattr(item, "category", "") or ""),
            estimated_savings=monthly_savings,
        )
