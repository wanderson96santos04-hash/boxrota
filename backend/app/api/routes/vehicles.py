import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleListOut, VehicleOut, VehicleUpdate
from app.services.vehicle_service import create_vehicle, get_vehicle, list_vehicles, update_vehicle

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleListOut])
def list_endpoint(
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=40, ge=1, le=60),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_vehicles(db, user=user, query=q, limit=limit)
    return [
        VehicleListOut(
            id=v.id,
            plate=v.plate,
            customer_name=(v.customer.name if getattr(v, "customer", None) else None),
            customer_phone=(v.customer.phone if getattr(v, "customer", None) else None),
            created_at=v.created_at,
        )
        for v in rows
    ]


@router.post("", response_model=VehicleOut)
def create_endpoint(
    body: VehicleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    v = create_vehicle(db, user=user, plate=body.plate, customer_id=body.customer_id)
    db.commit()
    v = get_vehicle(db, user=user, vehicle_id=v.id)
    return VehicleOut(
        id=v.id,
        plate=v.plate,
        customer_id=v.customer_id,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_endpoint(
    vehicle_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vid = uuid.UUID(vehicle_id)
    v = get_vehicle(db, user=user, vehicle_id=vid)
    return VehicleOut(
        id=v.id,
        plate=v.plate,
        customer_id=v.customer_id,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )


@router.patch("/{vehicle_id}", response_model=VehicleOut)
def patch_endpoint(
    vehicle_id: str,
    body: VehicleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vid = uuid.UUID(vehicle_id)
    v = update_vehicle(db, user=user, vehicle_id=vid, plate=body.plate, customer_id=body.customer_id)
    db.commit()
    v = get_vehicle(db, user=user, vehicle_id=vid)
    return VehicleOut(
        id=v.id,
        plate=v.plate,
        customer_id=v.customer_id,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )