import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinOpsScore(Base):
    __tablename__ = "finops_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    compute_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    storage_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    network_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    __table_args__ = (
        Index('ix_scores_tenant_analysis', 'tenant_id', 'analysis_id'),
    )
