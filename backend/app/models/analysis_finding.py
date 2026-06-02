import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisFinding(Base):
    __tablename__ = "analysis_findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    resource_id: Mapped[str] = mapped_column(Text, index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_monthly_savings: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    __table_args__ = (
        Index('ix_findings_tenant_analysis', 'tenant_id', 'analysis_id'),
    )
