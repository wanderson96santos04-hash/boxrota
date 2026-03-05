from pydantic import BaseModel, Field

from app.schemas.user import UserOut
from app.schemas.workshop import WorkshopCreate, WorkshopOut


class SetupAdmin(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=6, max_length=128)


class SetupPayload(BaseModel):
    workshop: WorkshopCreate
    admin: SetupAdmin


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=6, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class SetupResponse(BaseModel):
    workshop: WorkshopOut
    user: UserOut
    tokens: TokenPair