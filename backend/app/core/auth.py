import logging
import uuid
from dataclasses import dataclass

from fastapi import Depends
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User as AzureUser

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class AuthenticatedUser:
    id: uuid.UUID
    email: str
    display_name: str
    role: str
    tenant_id: str

# Configured to use SingleTenant, assuming single tenant based on AZURE_TENANT_ID. 
# It could be MultiTenant, but the prompt says AZURE_TENANT_ID is provided.
azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.azure_client_id or "",
    tenant_id=settings.azure_tenant_id or "",
    scopes={
        f"api://{settings.azure_client_id}/user_impersonation": "User Impersonation",
    },
)
