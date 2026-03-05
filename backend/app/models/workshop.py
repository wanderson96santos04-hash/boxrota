import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Workshop(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workshops"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)

    users = relationship("User", back_populates="workshop", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="workshop", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="workshop", cascade="all, delete-orphan")
    services = relationship("Service", backref="workshop")