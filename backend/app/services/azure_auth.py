from azure.core.credentials import TokenCredential
from azure.identity import ChainedTokenCredential, ClientSecretCredential, DefaultAzureCredential

from app.core.settings import Settings


class AzureCredentialProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_credential(self) -> TokenCredential:
        default_credential = DefaultAzureCredential(
            exclude_interactive_browser_credential=True,
        )
        if not self.settings.has_service_principal_config:
            return default_credential

        service_principal_credential = ClientSecretCredential(
            tenant_id=self.settings.azure_tenant_id or "",
            client_id=self.settings.azure_client_id or "",
            client_secret=self.settings.azure_client_secret or "",
        )
        return ChainedTokenCredential(default_credential, service_principal_credential)
