import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import QuoteStatus


class Quote(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "quotes"
    __table_args__ = (
        UniqueConstraint("workshop_id", "quote_number", name="uq_quotes_workshop_quote_number"),
        UniqueConstraint("public_token", name="uq_quotes_public_token"),
    )

    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)

    quote_number: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=QuoteStatus.draft.value)

    public_token: Mapped[str] = mapped_column(String(64), nullable=False)

    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    html_cache: Mapped[str | None] = mapped_column(Text, nullable=True)

    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    service = relationship("Service", back_populates="quotes")