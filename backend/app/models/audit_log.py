import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    actor_user_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    target_user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    __table_args__ = (
        Index('ix_audit_logs_tenant_action', 'tenant_id', 'action'),
    )
