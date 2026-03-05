from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workshop_id: UUID
    name: str
    email: str
    role: str
    is_active: bool


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=6, max_length=128)