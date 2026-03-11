import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReturnRuleOut(BaseModel):
    id: uuid.UUID
    name: str
    days_after: int
    active: bool
    created_at: datetime
    updated_at: datetime


class ReturnRuleUpsert(BaseModel):
    name: str = Field(default="Retorno", min_length=2, max_length=80)
    days_after: int = Field(default=180, ge=0, le=3650)
    active: bool = Field(default=True)


class ReturnOut(BaseModel):
    id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    vehicle_id: Optional[uuid.UUID] = None
    service_id: Optional[uuid.UUID] = None
    due_date: datetime
    status: str
    whatsapp_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    done_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    vehicle_plate: Optional[str] = None


class ReturnListOut(BaseModel):
    id: uuid.UUID
    due_date: datetime
    status: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    vehicle_plate: Optional[str] = None
    service_id: Optional[uuid.UUID] = None


class ReturnStatusUpdate(BaseModel):
    status: str = Field(min_length=3, max_length=20)