import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workshop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workshops.id"),
        nullable=False,
        unique=True,
    )

    plan = Column(String, nullable=False, default="basic")
    status = Column(String, nullable=False, default="active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    workshop = relationship("Workshop")