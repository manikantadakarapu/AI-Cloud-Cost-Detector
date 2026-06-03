import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.resource import Resource
from app.schemas.resource_schema import AzureResource


class ResourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_create(self, *, tenant_id: str, analysis_id: uuid.UUID, resources: list[AzureResource]) -> list[Resource]:
        entities = [
            Resource(
                tenant_id=tenant_id,
                analysis_id=analysis_id,
                resource_id=resource.resource_id,
                name=resource.name,
                type=resource.type,
                location=resource.location,
                sku=resource.sku,
                tags=resource.tags,
            )
            for resource in resources
        ]
        self.db.add_all(entities)
        self.db.flush()
        return entities

    def count_by_analysis(self, tenant_id: str, analysis_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(Resource).where(
            (Resource.tenant_id == tenant_id) & (Resource.analysis_id == analysis_id)
        )
        return int(self.db.scalar(statement) or 0)
