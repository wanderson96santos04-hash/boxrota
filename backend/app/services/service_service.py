import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppException
from app.models.customer import Customer, Vehicle
from app.models.enums import ServiceStatus
from app.models.service import Service, ServiceItem
from app.models.user import User
from app.services.returns_service import ensure_return_for_finalized_service


def _q2(v: Decimal) -> Decimal:
    return (v or Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _norm_plate(p: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]", "", (p or "")).upper().strip()
    if not s:
        raise AppException(400, "invalid_plate", "Placa inválida.")
    if len(s) > 16:
        s = s[:16]
    return s


def _norm_phone(p: str) -> str:
    s = re.sub(r"\D", "", (p or "")).strip()
    if not s:
        raise AppException(400, "invalid_phone", "Telefone inválido.")
    if len(s) > 30:
        s = s[:30]
    return s


def _recalc_service_totals(db: Session, service: Service) -> None:
    subtotal = (
        db.query(func.coalesce(func.sum(ServiceItem.total_price), 0))
        .filter(ServiceItem.service_id == service.id, ServiceItem.workshop_id == service.workshop_id)
        .scalar()
    )
    service.subtotal_amount = _q2(Decimal(subtotal or 0))
    service.total_amount = _q2(Decimal(service.subtotal_amount or 0) + Decimal(service.labor_amount or 0))


def _get_or_create_customer(
    db: Session,
    *,
    workshop_id: uuid.UUID,
    customer_name: str | None,
    customer_phone: str | None,
) -> Customer | None:
    if not customer_name and not customer_phone:
        return None

    if customer_phone:
        phone = _norm_phone(customer_phone)
        existing = (
            db.query(Customer)
            .filter(Customer.workshop_id == workshop_id, Customer.phone == phone)
            .one_or_none()
        )
        if existing:
            if customer_name and existing.name.strip().lower() != customer_name.strip().lower():
                existing.name = customer_name.strip()
                db.add(existing)
                db.flush()
            return existing

        if not customer_name:
            raise AppException(400, "missing_customer_name", "Informe o nome do cliente.")
        c = Customer(workshop_id=workshop_id, name=customer_name.strip(), phone=phone)
        db.add(c)
        db.flush()
        return c

    raise AppException(400, "missing_customer_phone", "Informe o telefone do cliente.")


def _get_or_create_vehicle(
    db: Session,
    *,
    workshop_id: uuid.UUID,
    plate: str,
    customer_id: uuid.UUID | None,
) -> Vehicle:
    plate_n = _norm_plate(plate)
    v = (
        db.query(Vehicle)
        .filter(Vehicle.workshop_id == workshop_id, Vehicle.plate == plate_n)
        .one_or_none()
    )
    if v:
        if customer_id and v.customer_id != customer_id:
            v.customer_id = customer_id
            db.add(v)
            db.flush()
        return v

    v = Vehicle(workshop_id=workshop_id, plate=plate_n, customer_id=customer_id)
    db.add(v)
    db.flush()
    return v


def list_services(
    db: Session,
    *,
    user: User,
    query: str | None = None,
    status: str | None = None,
    limit: int = 40,
) -> list[Service]:
    q = (
        db.query(Service)
        .options(joinedload(Service.vehicle), joinedload(Service.customer))
        .filter(Service.workshop_id == user.workshop_id)
        .order_by(Service.created_at.desc())
    )

    if status:
        s = str(status).strip().lower()
        allowed = {ServiceStatus.in_progress.value, ServiceStatus.finalized.value}
        if s not in allowed:
            raise AppException(400, "invalid_status", "Status inválido.")
        q = q.filter(Service.status == s)

    if query:
        term = query.strip()
        if term:
            plate_like = f"%{re.sub(r'[^A-Za-z0-9]', '', term).upper()}%"
            name_like = f"%{term.lower()}%"
            phone_like = f"%{re.sub(r'\\D', '', term)}%"
            q = q.join(Vehicle, Vehicle.id == Service.vehicle_id).outerjoin(Customer, Customer.id == Service.customer_id)
            q = q.filter(
                func.upper(Vehicle.plate).like(plate_like)
                | func.lower(func.coalesce(Customer.name, "")).like(name_like)
                | func.coalesce(Customer.phone, "").like(phone_like)
            )

    return q.limit(max(1, min(int(limit), 60))).all()


def get_service(db: Session, *, user: User, service_id: uuid.UUID) -> Service:
    s = (
        db.query(Service)
        .options(joinedload(Service.vehicle), joinedload(Service.customer), joinedload(Service.items))
        .filter(Service.workshop_id == user.workshop_id, Service.id == service_id)
        .one_or_none()
    )
    if not s:
        raise AppException(404, "not_found", "Serviço não encontrado.")
    return s


def create_service(
    db: Session,
    *,
    user: User,
    plate: str,
    customer_name: str | None,
    customer_phone: str | None,
    notes: str | None,
    labor_amount: Decimal,
) -> Service:
    workshop_id = user.workshop_id

    customer = _get_or_create_customer(
        db,
        workshop_id=workshop_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
    )
    vehicle = _get_or_create_vehicle(
        db,
        workshop_id=workshop_id,
        plate=plate,
        customer_id=customer.id if customer else None,
    )

    s = Service(
        workshop_id=workshop_id,
        vehicle_id=vehicle.id,
        customer_id=customer.id if customer else None,
        status=ServiceStatus.in_progress.value,
        notes=(notes or "").strip() or None,
        labor_amount=_q2(Decimal(labor_amount or 0)),
        subtotal_amount=Decimal("0"),
        total_amount=Decimal("0"),
        created_by_user_id=user.id,
    )
    db.add(s)
    db.flush()

    _recalc_service_totals(db, s)
    db.add(s)
    db.flush()
    db.refresh(s)
    return s


def update_service(
    db: Session,
    *,
    user: User,
    service_id: uuid.UUID,
    status: str | None,
    notes: str | None,
    labor_amount: Decimal | None,
) -> Service:
    s = get_service(db, user=user, service_id=service_id)
    prev_status = s.status

    if status is not None:
        st = str(status).strip().lower()
        allowed = {ServiceStatus.in_progress.value, ServiceStatus.finalized.value}
        if st not in allowed:
            raise AppException(400, "invalid_status", "Status inválido.")
        s.status = st

    if notes is not None:
        s.notes = notes.strip() or None

    if labor_amount is not None:
        s.labor_amount = _q2(Decimal(labor_amount or 0))

    _recalc_service_totals(db, s)
    db.add(s)
    db.flush()

    if prev_status != "finalized" and s.status == "finalized":
        ensure_return_for_finalized_service(db, user=user, service=s)

    db.add(s)
    db.flush()
    db.refresh(s)
    return s


def add_service_item(
    db: Session,
    *,
    user: User,
    service_id: uuid.UUID,
    description: str,
    qty: int,
    unit_price: Decimal,
    part_id: uuid.UUID | None = None,
) -> Service:
    s = get_service(db, user=user, service_id=service_id)

    q = int(qty or 1)
    if q < 1:
        raise AppException(400, "invalid_qty", "Quantidade inválida.")

    unit = _q2(Decimal(unit_price or 0))
    total = _q2(unit * Decimal(q))

    it = ServiceItem(
        workshop_id=user.workshop_id,
        service_id=s.id,
        part_id=part_id,
        description=description.strip()[:160],
        qty=q,
        unit_price=unit,
        total_price=total,
    )
    db.add(it)
    db.flush()

    _recalc_service_totals(db, s)
    db.add(s)
    db.flush()
    db.refresh(s)
    return s