import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class QuoteOut(BaseModel):
    id: uuid.UUID
    service_id: uuid.UUID
    quote_number: str
    status: str
    public_token: str
    subtotal_amount: str
    total_amount: str
    snapshot: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class QuoteStatusUpdate(BaseModel):
    status: str = Field(min_length=3, max_length=20)


class QuoteFromServiceResponse(BaseModel):
    quote: QuoteOut