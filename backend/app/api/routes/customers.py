import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerListOut, CustomerOut, CustomerUpdate
from app.services.customer_service import create_customer, get_customer, list_customers, update_customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerListOut])
def list_endpoint(
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=40, ge=1, le=60),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_customers(db, user=user, query=q, limit=limit)
    return [
        CustomerListOut(
            id=c.id,
            name=c.name,
            phone=c.phone,
            created_at=c.created_at,
        )
        for c in rows
    ]


@router.post("", response_model=CustomerOut)
def create_endpoint(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = create_customer(db, user=user, name=body.name, phone=body.phone)
    db.commit()
    c = get_customer(db, user=user, customer_id=c.id)
    return CustomerOut(
        id=c.id,
        name=c.name,
        phone=c.phone,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.get("/{customer_id}", response_model=CustomerOut)
def get_endpoint(
    customer_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cid = uuid.UUID(customer_id)
    c = get_customer(db, user=user, customer_id=cid)
    return CustomerOut(
        id=c.id,
        name=c.name,
        phone=c.phone,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.patch("/{customer_id}", response_model=CustomerOut)
def patch_endpoint(
    customer_id: str,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cid = uuid.UUID(customer_id)
    c = update_customer(db, user=user, customer_id=cid, name=body.name, phone=body.phone)
    db.commit()
    c = get_customer(db, user=user, customer_id=cid)
    return CustomerOut(
        id=c.id,
        name=c.name,
        phone=c.phone,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )