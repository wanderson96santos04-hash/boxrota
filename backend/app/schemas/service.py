import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ServiceStatus


class CustomerMini(BaseModel):
    id: uuid.UUID
    name: str
    phone: str


class VehicleMini(BaseModel):
    id: uuid.UUID
    plate: str


class ServiceItemOut(BaseModel):
    id: uuid.UUID
    part_id: Optional[uuid.UUID] = None
    description: str
    qty: int
    unit_price: Decimal
    total_price: Decimal
    created_at: datetime
    updated_at: datetime


class ServiceOut(BaseModel):
    id: uuid.UUID
    status: str
    notes: Optional[str] = None
    labor_amount: Decimal
    subtotal_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    customer: Optional[CustomerMini] = None
    vehicle: VehicleMini
    items: list[ServiceItemOut] = []


class ServiceListOut(BaseModel):
    id: uuid.UUID
    status: str
    total_amount: Decimal
    created_at: datetime
    vehicle_plate: str
    customer_name: Optional[str] = None


class ServiceCreate(BaseModel):
    plate: str = Field(min_length=4, max_length=16)
    customer_name: Optional[str] = Field(default=None, min_length=2, max_length=140)
    customer_phone: Optional[str] = Field(default=None, min_length=6, max_length=30)
    notes: Optional[str] = Field(default=None, max_length=5000)
    labor_amount: Decimal = Field(default=Decimal("0"))


class ServiceUpdate(BaseModel):
    status: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=5000)
    labor_amount: Optional[Decimal] = Field(default=None)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        s = str(value).strip().lower()
        allowed = {
            ServiceStatus.open.value,
            ServiceStatus.in_progress.value,
            ServiceStatus.waiting_parts.value,
            ServiceStatus.completed.value,
            ServiceStatus.delivered.value,
            ServiceStatus.canceled.value,
        }

        if s not in allowed:
            raise ValueError("status inválido")

        return s


class ServiceItemCreate(BaseModel):
    description: str = Field(min_length=2, max_length=160)
    qty: int = Field(default=1, ge=1, le=999)
    unit_price: Decimal = Field(default=Decimal("0"))
    part_id: Optional[uuid.UUID] = None