import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_azure_object_id(self, tenant_id: str, azure_object_id: str) -> User | None:
        stmt = select(User).where(
            (User.tenant_id == tenant_id) & (User.azure_object_id == azure_object_id)
        )
        return self.db.scalars(stmt).first()

    def get_all(self, tenant_id: str, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).where(User.tenant_id == tenant_id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get(self, tenant_id: str, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(
            (User.tenant_id == tenant_id) & (User.id == user_id)
        )
        return self.db.scalars(stmt).first()

    def create(self, tenant_id: str, azure_object_id: str, email: str, display_name: str, role: str = "viewer") -> User:
        user = User(
            tenant_id=tenant_id,
            azure_object_id=azure_object_id,
            email=email,
            display_name=display_name,
            role=role,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def update_last_login(self, user_id: uuid.UUID) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            self.db.flush()

    def update_role(self, user_id: uuid.UUID, role: str) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.role = role
            self.db.flush()
