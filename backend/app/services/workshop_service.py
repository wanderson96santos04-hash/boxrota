import re
import unicodedata

from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.models.marketplace import MarketplaceSettings
from app.models.subscription import Subscription
from app.models.workshop import Workshop


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def _next_available_slug(db: Session, base_slug: str) -> str:
    slug = base_slug or "oficina"

    exists = db.query(Workshop.id).filter(Workshop.slug == slug).first()
    if not exists:
        return slug

    n = 2
    while True:
        candidate = f"{slug}-{n}"
        exists = db.query(Workshop.id).filter(Workshop.slug == candidate).first()
        if not exists:
            return candidate
        n += 1


def create_workshop(db: Session, *, name: str, phone: str | None = None, city: str | None = None) -> Workshop:
    clean_name = name.strip()
    base_slug = _slugify(clean_name)
    slug = _next_available_slug(db, base_slug)

    w = Workshop(
        name=clean_name,
        slug=slug,
        phone=phone.strip() if phone else None,
        city=city.strip() if city else None,
    )
    db.add(w)
    db.flush()

    sub = Subscription(
        workshop_id=w.id,
        plan="basic",
        status="expired",
    )
    db.add(sub)

    ms = MarketplaceSettings(
        workshop_id=w.id,
        allow_attendant_purchase=False,
        default_markup_percent=20,
        pricing_mode="markup",
        pro_feature_enabled=False,
    )
    db.add(ms)

    db.flush()
    return w


def assert_no_workshops_exist(db: Session) -> None:
    exists = db.query(Workshop.id).limit(1).first()
    if exists:
        raise AppException(409, "already_setup", "Sistema já foi configurado.")