"""Tenant context and multi-tenancy utilities."""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TenantContext:
    """Holds the current tenant context extracted from JWT claims."""
    
    tenant_id: str
    
    def __post_init__(self) -> None:
        if not self.tenant_id:
            logger.error("TenantContext initialized with empty tenant_id")
            raise ValueError("tenant_id cannot be empty")
