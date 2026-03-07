from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.marketplace import Part
from app.models.user import User

router = APIRouter(prefix="/parts", tags=["parts"])


class PartCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    sku: Optional[str] = Field(default=None, max_length=80)
    price: Decimal = Field(default=Decimal("0"), ge=0)
    stock_qty: int = Field(default=0, ge=0)


class PartOut(BaseModel):
    id: str
    name: str
    sku: Optional[str] = None
    price: float
    stock_qty: int

    @classmethod
    def from_model(cls, part: Part) -> "PartOut":
        return cls(
            id=str(part.id),
            name=part.name,
            sku=part.sku,
            price=float(part.price or 0),
            stock_qty=int(part.stock_qty or 0),
        )


@router.get("", response_model=list[PartOut])
def list_parts(
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=60, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = (
        db.query(Part)
        .filter(Part.workshop_id == user.workshop_id)
        .order_by(Part.name.asc())
    )

    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Part.name).like(term),
                func.lower(func.coalesce(Part.sku, "")).like(term),
            )
        )

    rows = query.limit(limit).all()
    return [PartOut.from_model(part) for part in rows]


@router.post("", response_model=PartOut)
def create_part(
    data: PartCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    part = Part(
        workshop_id=user.workshop_id,
        name=data.name.strip(),
        sku=(data.sku.strip().upper() if data.sku and data.sku.strip() else None),
        price=Decimal(data.price or 0),
        stock_qty=int(data.stock_qty or 0),
    )

    db.add(part)
    db.commit()
    db.refresh(part)

    return PartOut.from_model(part)