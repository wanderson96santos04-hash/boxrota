import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "payments"

    service_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=True, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    method: Mapped[str] = mapped_column(String(30), nullable=False, default="cash")
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)