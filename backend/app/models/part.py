from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)

    sku = Column(String, nullable=True)

    price = Column(Numeric(10, 2), default=0)

    stock_qty = Column(Integer, default=0)