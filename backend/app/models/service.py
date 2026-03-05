import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Service(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "services"

    # se você já tem outros campos aqui no seu projeto, pode manter também.
    # estou colocando os essenciais para o relacionamento funcionar.

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Exemplo de campos comuns (ajuste se seu projeto tiver outros nomes)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    total: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # RELACIONAMENTOS (isso resolve o erro "Service has no property workshop")
    workshop = relationship("Workshop", back_populates="services")
    customer = relationship("Customer", back_populates="services")
    vehicle = relationship("Vehicle", back_populates="services")

    items = relationship("ServiceItem", back_populates="service", cascade="all, delete-orphan")


class ServiceItem(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "service_items"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    service = relationship("Service", back_populates="items")