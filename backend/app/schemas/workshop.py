from uuid import UUID
from pydantic import BaseModel, ConfigDict


class WorkshopBase(BaseModel):
    name: str
    phone: str
    city: str


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    city: str | None = None


class WorkshopOut(WorkshopBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID