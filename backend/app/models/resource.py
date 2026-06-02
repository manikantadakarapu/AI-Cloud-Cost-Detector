import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    resource_id: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tags: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    analysis: Mapped["Analysis"] = relationship(back_populates="resources")
    
    __table_args__ = (
        Index('ix_resources_tenant_analysis', 'tenant_id', 'analysis_id'),
    )
