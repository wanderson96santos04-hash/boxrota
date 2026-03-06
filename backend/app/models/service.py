import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Service(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "services"

    # Relacionamentos principais (batem com Customer.services e Vehicle.services)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )

    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id"),
        nullable=True,
        index=True,
    )

    # Campos comuns de serviço (se você já tiver outros, pode adicionar depois)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)

    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    # ✅ IMPORTANTÍSSIMO: isso resolve o erro do log
    # Alguém no projeto está usando back_populates="quotes" apontando pra Service.quotes
    quotes = relationship("Quote", back_populates="service", cascade="all, delete-orphan")

    # ✅ IMPORTANTÍSSIMO: isso resolve o erro de import do ServiceItem
    items = relationship("ServiceItem", back_populates="service", cascade="all, delete-orphan")

    customer = relationship("Customer", back_populates="services")
    vehicle = relationship("Vehicle", back_populates="services")


class ServiceItem(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "service_items"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    service = relationship("Service", back_populates="items")