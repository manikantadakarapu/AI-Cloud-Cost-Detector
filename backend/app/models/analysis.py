import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Analysis(TimestampMixin, Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    subscription_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    resource_group: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    job_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True, nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    resources: Mapped[list["Resource"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index('ix_analyses_tenant_subscription', 'tenant_id', 'subscription_id'),
    )
