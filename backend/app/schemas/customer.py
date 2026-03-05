import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CustomerOut(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    created_at: datetime
    updated_at: datetime


class CustomerListOut(BaseModel):
    id: uuid.UUID
    name: str
    phone: str
    created_at: datetime


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    phone: str = Field(min_length=6, max_length=30)


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    phone: str | None = Field(default=None, min_length=6, max_length=30)