from typing import Any, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class TenantAwareRepository(Generic[ModelType]):
    """
    Base repository enforcing strict tenant_id boundaries on all queries.
    Any attempt to query cross-tenant resources inherently returns None or 404.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, tenant_id: str, id: Any) -> Optional[ModelType]:
        """
        Retrieves a record by ID ensuring it belongs to the tenant.
        """
        stmt = select(self.model).where(
            self.model.tenant_id == tenant_id,
            self.model.id == id
        )
        return db.execute(stmt).scalars().first()

    def get_or_404(self, db: Session, tenant_id: str, id: Any) -> ModelType:
        """
        Retrieves a record by ID or throws a secure 404 (preventing cross-tenant leakage).
        """
        obj = self.get(db=db, tenant_id=tenant_id, id=id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        return obj

    def get_all(self, db: Session, tenant_id: str, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieves all records for a specific tenant.
        """
        stmt = select(self.model).where(
            self.model.tenant_id == tenant_id
        ).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create_with_tenant(self, db: Session, tenant_id: str, obj_in: dict) -> ModelType:
        """
        Creates a record, safely enforcing the tenant context.
        """
        obj_in["tenant_id"] = tenant_id
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj