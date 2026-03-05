import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Customer(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("workshop_id", "phone", name="uq_customers_workshop_phone"),
    )

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)

    # RELACIONAMENTO COM WORKSHOP (resolve o erro do mapper)
    workshop = relationship("Workshop", back_populates="customers")

    vehicles = relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="customer", cascade="all, delete-orphan")


class Vehicle(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("workshop_id", "plate", name="uq_vehicles_workshop_plate"),
    )

    plate: Mapped[str] = mapped_column(String(16), nullable=False)

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # RELACIONAMENTO COM WORKSHOP (resolve o erro do mapper)
    workshop = relationship("Workshop", back_populates="vehicles")

    customer = relationship("Customer", back_populates="vehicles")
    services = relationship("Service", back_populates="vehicle", cascade="all, delete-orphan")