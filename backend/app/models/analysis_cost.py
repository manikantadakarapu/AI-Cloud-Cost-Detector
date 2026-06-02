import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisCost(Base):
    __tablename__ = "analysis_costs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    resource_id: Mapped[str] = mapped_column(Text, index=True, nullable=False)
    service_name: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    resource_name: Mapped[str] = mapped_column(String(512), nullable=False)
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    billing_period: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    __table_args__ = (
        Index('ix_costs_tenant_analysis', 'tenant_id', 'analysis_id'),
    )
