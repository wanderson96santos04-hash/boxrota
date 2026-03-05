import re
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppException
from app.models.customer import Customer, Vehicle
from app.models.user import User


def _norm_plate(p: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]", "", (p or "")).upper().strip()
    if not s:
        raise AppException(400, "invalid_plate", "Placa inválida.")
    if len(s) < 4:
        raise AppException(400, "invalid_plate", "Placa inválida.")
    if len(s) > 16:
        s = s[:16]
    return s


def list_vehicles(db: Session, *, user: User, query: str | None, limit: int = 40) -> list[Vehicle]:
    q = (
        db.query(Vehicle)
        .options(joinedload(Vehicle.customer))
        .filter(Vehicle.workshop_id == user.workshop_id)
        .order_by(Vehicle.created_at.desc())
    )

    if query:
        term = query.strip()
        if term:
            plate_like = f"%{re.sub(r'[^A-Za-z0-9]', '', term).upper()}%"
            name_like = f"%{term.lower()}%"
            phone_like = f"%{re.sub(r'\\D', '', term)}%"
            q = q.outerjoin(Customer, Customer.id == Vehicle.customer_id)
            q = q.filter(
                func.upper(Vehicle.plate).like(plate_like)
                | func.lower(func.coalesce(Customer.name, "")).like(name_like)
                | func.coalesce(Customer.phone, "").like(phone_like)
            )

    return q.limit(max(1, min(int(limit), 60))).all()


def get_vehicle(db: Session, *, user: User, vehicle_id: uuid.UUID) -> Vehicle:
    v = (
        db.query(Vehicle)
        .options(joinedload(Vehicle.customer))
        .filter(Vehicle.workshop_id == user.workshop_id, Vehicle.id == vehicle_id)
        .one_or_none()
    )
    if not v:
        raise AppException(404, "not_found", "Veículo não encontrado.")
    return v


def create_vehicle(db: Session, *, user: User, plate: str, customer_id: uuid.UUID | None) -> Vehicle:
    plate_n = _norm_plate(plate)

    exists = (
        db.query(Vehicle.id)
        .filter(Vehicle.workshop_id == user.workshop_id, Vehicle.plate == plate_n)
        .first()
    )
    if exists:
        raise AppException(409, "plate_in_use", "Placa já cadastrada nesta oficina.")

    if customer_id is not None:
        c = (
            db.query(Customer.id)
            .filter(Customer.workshop_id == user.workshop_id, Customer.id == customer_id)
            .first()
        )
        if not c:
            raise AppException(404, "not_found", "Cliente não encontrado.")

    v = Vehicle(workshop_id=user.workshop_id, plate=plate_n, customer_id=customer_id)
    db.add(v)
    db.flush()
    db.refresh(v)
    return v


def update_vehicle(
    db: Session,
    *,
    user: User,
    vehicle_id: uuid.UUID,
    plate: str | None,
    customer_id: uuid.UUID | None,
) -> Vehicle:
    v = get_vehicle(db, user=user, vehicle_id=vehicle_id)

    if plate is not None:
        plate_n = _norm_plate(plate)
        exists = (
            db.query(Vehicle.id)
            .filter(
                Vehicle.workshop_id == user.workshop_id,
                Vehicle.plate == plate_n,
                Vehicle.id != v.id,
            )
            .first()
        )
        if exists:
            raise AppException(409, "plate_in_use", "Placa já cadastrada nesta oficina.")
        v.plate = plate_n

    if customer_id is not None:
        c = (
            db.query(Customer.id)
            .filter(Customer.workshop_id == user.workshop_id, Customer.id == customer_id)
            .first()
        )
        if not c:
            raise AppException(404, "not_found", "Cliente não encontrado.")
        v.customer_id = customer_id

    db.add(v)
    db.flush()
    db.refresh(v)
    return v