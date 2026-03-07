from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter(prefix="/parts", tags=["parts"])


class PartCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    price: Optional[float] = 0
    stock_qty: Optional[int] = 0


class Part(BaseModel):
    id: str
    name: str
    sku: Optional[str]
    price: float
    stock_qty: int


# memória simples (depois vira banco)
PARTS_DB: List[Part] = []


@router.get("")
def list_parts():
    return PARTS_DB


@router.post("")
def create_part(data: PartCreate):
    part = Part(
        id=str(uuid.uuid4()),
        name=data.name,
        sku=data.sku,
        price=data.price,
        stock_qty=data.stock_qty,
    )

    PARTS_DB.append(part)
    return part