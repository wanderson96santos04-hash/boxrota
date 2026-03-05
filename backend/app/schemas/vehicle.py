import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VehicleOut(BaseModel):
    id: uuid.UUID
    plate: str
    customer_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class VehicleListOut(BaseModel):
    id: uuid.UUID
    plate: str
    customer_name: str | None = None
    customer_phone: str | None = None
    created_at: datetime


class VehicleCreate(BaseModel):
    plate: str = Field(min_length=4, max_length=16)
    customer_id: uuid.UUID | None = None


class VehicleUpdate(BaseModel):
    plate: str | None = Field(default=None, min_length=4, max_length=16)
    customer_id: uuid.UUID | None = None