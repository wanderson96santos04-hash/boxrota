import uuid
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.enums import ServiceStatus
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceItemCreate, ServiceListOut, ServiceOut, ServiceUpdate
from app.services.service_service import add_service_item, create_service, get_service, list_services, update_service

router = APIRouter(prefix="/services", tags=["services"])


def _to_list_out(s) -> ServiceListOut:
    return ServiceListOut(
        id=s.id,
        status=s.status,
        total_amount=s.total_amount,
        created_at=s.created_at,
        vehicle_plate=s.vehicle.plate if s.vehicle else "",
        customer_name=s.customer.name if s.customer else None,
    )


def _to_out(s) -> ServiceOut:
    return ServiceOut(
        id=s.id,
        status=s.status,
        notes=s.notes,
        labor_amount=s.labor_amount,
        subtotal_amount=s.subtotal_amount,
        total_amount=s.total_amount,
        created_at=s.created_at,
        updated_at=s.updated_at,
        customer=(
            None
            if not s.customer
            else {
                "id": s.customer.id,
                "name": s.customer.name,
                "phone": s.customer.phone,
            }
        ),
        vehicle={"id": s.vehicle.id, "plate": s.vehicle.plate},
        items=[
            {
                "id": it.id,
                "part_id": it.part_id,
                "description": it.description,
                "qty": it.qty,
                "unit_price": it.unit_price,
                "total_price": it.total_price,
                "created_at": it.created_at,
                "updated_at": it.updated_at,
            }
            for it in (s.items or [])
        ],
    )


@router.get("", response_model=list[ServiceListOut])
def list_endpoint(
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=40, ge=1, le=60),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_services(db, user=user, query=q, status=status, limit=limit)
    return [_to_list_out(s) for s in rows]


@router.post("", response_model=ServiceOut)
def create_endpoint(
    body: ServiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = create_service(
        db,
        user=user,
        plate=body.plate,
        customer_name=body.customer_name,
        customer_phone=body.customer_phone,
        notes=body.notes,
        labor_amount=Decimal(body.labor_amount or 0),
    )
    db.commit()
    s = get_service(db, user=user, service_id=s.id)
    return _to_out(s)


@router.get("/{service_id}", response_model=ServiceOut)
def get_endpoint(
    service_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sid = uuid.UUID(service_id)
    s = get_service(db, user=user, service_id=sid)
    return _to_out(s)


@router.patch("/{service_id}", response_model=ServiceOut)
def patch_endpoint(
    service_id: str,
    body: ServiceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sid = uuid.UUID(service_id)
    s = update_service(
        db,
        user=user,
        service_id=sid,
        status=body.status,
        notes=body.notes,
        labor_amount=body.labor_amount,
    )
    db.commit()
    s = get_service(db, user=user, service_id=sid)
    return _to_out(s)


@router.post("/{service_id}/complete", response_model=ServiceOut)
def complete_endpoint(
    service_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sid = uuid.UUID(service_id)
    s = update_service(
        db,
        user=user,
        service_id=sid,
        status=ServiceStatus.completed.value,
        notes=None,
        labor_amount=None,
    )
    db.commit()
    s = get_service(db, user=user, service_id=sid)
    return _to_out(s)


@router.post("/{service_id}/items", response_model=ServiceOut)
def add_item_endpoint(
    service_id: str,
    body: ServiceItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sid = uuid.UUID(service_id)
    s = add_service_item(
        db,
        user=user,
        service_id=sid,
        description=body.description,
        qty=body.qty,
        unit_price=Decimal(body.unit_price or 0),
        part_id=body.part_id,
    )
    db.commit()
    s = get_service(db, user=user, service_id=sid)
    return _to_out(s)