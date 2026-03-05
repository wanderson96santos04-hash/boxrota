import re
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.models.customer import Customer
from app.models.user import User


def _norm_phone(p: str) -> str:
    s = re.sub(r"\D", "", (p or "")).strip()
    if not s:
        raise AppException(400, "invalid_phone", "Telefone inválido.")
    if len(s) > 30:
        s = s[:30]
    if len(s) < 6:
        raise AppException(400, "invalid_phone", "Telefone inválido.")
    return s


def _norm_name(n: str) -> str:
    s = (n or "").strip()
    if len(s) < 2:
        raise AppException(400, "invalid_name", "Nome inválido.")
    if len(s) > 140:
        s = s[:140]
    return s


def list_customers(db: Session, *, user: User, query: str | None, limit: int = 40) -> list[Customer]:
    q = (
        db.query(Customer)
        .filter(Customer.workshop_id == user.workshop_id)
        .order_by(Customer.created_at.desc())
    )

    if query:
        term = query.strip()
        if term:
            name_like = f"%{term.lower()}%"
            phone_like = f"%{re.sub(r'\\D', '', term)}%"
            q = q.filter(
                func.lower(Customer.name).like(name_like)
                | func.coalesce(Customer.phone, "").like(phone_like)
            )

    return q.limit(max(1, min(int(limit), 60))).all()


def get_customer(db: Session, *, user: User, customer_id: uuid.UUID) -> Customer:
    c = (
        db.query(Customer)
        .filter(Customer.workshop_id == user.workshop_id, Customer.id == customer_id)
        .one_or_none()
    )
    if not c:
        raise AppException(404, "not_found", "Cliente não encontrado.")
    return c


def create_customer(db: Session, *, user: User, name: str, phone: str) -> Customer:
    name_n = _norm_name(name)
    phone_n = _norm_phone(phone)

    exists = (
        db.query(Customer.id)
        .filter(Customer.workshop_id == user.workshop_id, Customer.phone == phone_n)
        .first()
    )
    if exists:
        raise AppException(409, "phone_in_use", "Telefone já cadastrado nesta oficina.")

    c = Customer(workshop_id=user.workshop_id, name=name_n, phone=phone_n)
    db.add(c)
    db.flush()
    db.refresh(c)
    return c


def update_customer(
    db: Session,
    *,
    user: User,
    customer_id: uuid.UUID,
    name: str | None,
    phone: str | None,
) -> Customer:
    c = get_customer(db, user=user, customer_id=customer_id)

    if name is not None:
        c.name = _norm_name(name)

    if phone is not None:
        phone_n = _norm_phone(phone)
        exists = (
            db.query(Customer.id)
            .filter(
                Customer.workshop_id == user.workshop_id,
                Customer.phone == phone_n,
                Customer.id != c.id,
            )
            .first()
        )
        if exists:
            raise AppException(409, "phone_in_use", "Telefone já cadastrado nesta oficina.")
        c.phone = phone_n

    db.add(c)
    db.flush()
    db.refresh(c)
    return c