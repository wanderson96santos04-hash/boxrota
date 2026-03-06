import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Service(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "services"

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    # ✅ isso aqui resolve: "Service has no property workshop"
    workshop = relationship("Workshop", back_populates="services")

    # ✅ isso mantém Customer/Vehicle ok
    customer = relationship("Customer", back_populates="services")
    vehicle = relationship("Vehicle", back_populates="services")

    # ✅ isso resolve: "Service has no property quotes"
    quotes = relationship("Quote", back_populates="service", cascade="all, delete-orphan")

    # ✅ itens do serviço
    items = relationship("ServiceItem", back_populates="service", cascade="all, delete-orphan")


class ServiceItem(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "service_items"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(140), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    # relacionamento
    service = relationship("Service", back_populates="items")