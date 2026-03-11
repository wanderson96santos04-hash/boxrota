import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppException
from app.models.customer import Customer, Vehicle
from app.models.enums import ReturnStatus
from app.models.returns import Return, ReturnRule
from app.models.service import Service
from app.models.user import User


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_default_rule(db: Session, *, workshop_id: uuid.UUID) -> ReturnRule:
    rule = (
        db.query(ReturnRule)
        .filter(ReturnRule.workshop_id == workshop_id)
        .order_by(ReturnRule.created_at.asc())
        .first()
    )
    if rule:
        return rule

    rule = ReturnRule(
        workshop_id=workshop_id,
        name="Retorno",
        days_after=180,
        active=True,
    )
    db.add(rule)
    db.flush()
    db.refresh(rule)
    return rule


def get_active_rule(db: Session, *, workshop_id: uuid.UUID) -> ReturnRule:
    rule = (
        db.query(ReturnRule)
        .filter(ReturnRule.workshop_id == workshop_id, ReturnRule.active.is_(True))
        .order_by(ReturnRule.updated_at.desc())
        .first()
    )
    if rule:
        return rule
    return get_or_create_default_rule(db, workshop_id=workshop_id)


def upsert_rule(db: Session, *, user: User, name: str, days_after: int, active: bool) -> ReturnRule:
    r = (
        db.query(ReturnRule)
        .filter(ReturnRule.workshop_id == user.workshop_id)
        .order_by(ReturnRule.created_at.asc())
        .first()
    )
    if not r:
        r = ReturnRule(workshop_id=user.workshop_id)

    r.name = (name or "Retorno").strip()[:80] or "Retorno"
    r.days_after = int(days_after)
    if r.days_after < 0 or r.days_after > 3650:
        raise AppException(400, "invalid_days_after", "days_after inválido.")
    r.active = bool(active)

    db.add(r)
    db.flush()
    db.refresh(r)
    return r


def _build_whatsapp_message(
    *,
    customer_name: str | None,
    vehicle_plate: str | None,
    due_date: datetime,
) -> str:
    dn = due_date.astimezone(timezone.utc).date().strftime("%d/%m/%Y")
    name = (customer_name or "Tudo bem").strip()
    plate = (vehicle_plate or "").strip().upper()
    plate_txt = f" do veículo {plate}" if plate else ""
    return (
        f"Olá, {name}! 👋\n"
        f"Passando pra lembrar do retorno{plate_txt}.\n"
        f"Posso agendar pra você? (Previsto: {dn})"
    )


def ensure_return_for_finalized_service(db: Session, *, user: User, service: Service) -> Return | None:
    if service.workshop_id != user.workshop_id:
        raise AppException(403, "forbidden", "Sem permissão para esta ação.")
    if service.status not in {"completed", "finalized"}:
        return None

    existing = (
        db.query(Return)
        .filter(Return.workshop_id == user.workshop_id, Return.service_id == service.id)
        .one_or_none()
    )
    if existing:
        return existing

    rule = get_active_rule(db, workshop_id=user.workshop_id)
    days_after = 180 if rule.days_after is None else int(rule.days_after)
    due = _now() + timedelta(days=days_after)

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.workshop_id == user.workshop_id, Vehicle.id == service.vehicle_id)
        .one_or_none()
    )
    customer = None
    if service.customer_id:
        customer = (
            db.query(Customer)
            .filter(Customer.workshop_id == user.workshop_id, Customer.id == service.customer_id)
            .one_or_none()
        )

    msg = _build_whatsapp_message(
        customer_name=(customer.name if customer else None),
        vehicle_plate=(vehicle.plate if vehicle else None),
        due_date=due,
    )

    r = Return(
        workshop_id=user.workshop_id,
        customer_id=customer.id if customer else None,
        vehicle_id=vehicle.id if vehicle else None,
        service_id=service.id,
        due_date=due,
        status=ReturnStatus.pending.value,
        whatsapp_message=msg,
        sent_at=None,
        done_at=None,
    )
    db.add(r)
    db.flush()
    db.refresh(r)
    return r


def list_returns(
    db: Session,
    *,
    user: User,
    date_from: datetime | None,
    date_to: datetime | None,
    status: str | None,
    limit: int = 60,
) -> list[Return]:
    q = (
        db.query(Return)
        .options(joinedload(ReturnRule, innerjoin=False))
        .filter(Return.workshop_id == user.workshop_id)
        .order_by(Return.due_date.asc())
    )

    if status:
        st = str(status).strip().lower()
        allowed = {ReturnStatus.pending.value, ReturnStatus.sent.value, ReturnStatus.done.value}
        if st not in allowed:
            raise AppException(400, "invalid_status", "Status inválido.")
        q = q.filter(Return.status == st)

    if date_from:
        q = q.filter(Return.due_date >= date_from)
    if date_to:
        q = q.filter(Return.due_date <= date_to)

    return q.limit(max(1, min(int(limit), 120))).all()


def get_return(db: Session, *, user: User, return_id: uuid.UUID) -> Return:
    r = (
        db.query(Return)
        .filter(Return.workshop_id == user.workshop_id, Return.id == return_id)
        .one_or_none()
    )
    if not r:
        raise AppException(404, "not_found", "Retorno não encontrado.")
    return r


def update_return_status(db: Session, *, user: User, return_id: uuid.UUID, status: str) -> Return:
    r = get_return(db, user=user, return_id=return_id)

    st = str(status).strip().lower()
    allowed = {ReturnStatus.pending.value, ReturnStatus.sent.value, ReturnStatus.done.value}
    if st not in allowed:
        raise AppException(400, "invalid_status", "Status inválido.")

    now = _now()
    r.status = st
    if st == ReturnStatus.sent.value:
        r.sent_at = now
    if st == ReturnStatus.done.value:
        r.done_at = now

    db.add(r)
    db.flush()
    db.refresh(r)
    return r


def enrich_return_rows(db: Session, *, user: User, rows: list[Return]) -> list[dict]:
    if not rows:
        return []

    customer_ids = {r.customer_id for r in rows if r.customer_id}
    vehicle_ids = {r.vehicle_id for r in rows if r.vehicle_id}

    customers = {}
    if customer_ids:
        for c in (
            db.query(Customer)
            .filter(Customer.workshop_id == user.workshop_id, Customer.id.in_(list(customer_ids)))
            .all()
        ):
            customers[c.id] = c

    vehicles = {}
    if vehicle_ids:
        for v in (
            db.query(Vehicle)
            .filter(Vehicle.workshop_id == user.workshop_id, Vehicle.id.in_(list(vehicle_ids)))
            .all()
        ):
            vehicles[v.id] = v

    out = []
    for r in rows:
        c = customers.get(r.customer_id) if r.customer_id else None
        v = vehicles.get(r.vehicle_id) if r.vehicle_id else None
        out.append(
            {
                "id": r.id,
                "due_date": r.due_date,
                "status": r.status,
                "customer_name": (c.name if c else None),
                "customer_phone": (c.phone if c else None),
                "vehicle_plate": (v.plate if v else None),
                "service_id": r.service_id,
            }
        )
    return out