from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class WorkshopBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=80)


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=80)


class WorkshopOut(WorkshopBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str