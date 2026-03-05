from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.models.marketplace import MarketplaceSettings
from app.models.subscription import Subscription
from app.models.workshop import Workshop


def create_workshop(db: Session, *, name: str, phone: str | None = None, city: str | None = None) -> Workshop:
    w = Workshop(name=name, phone=phone, city=city)
    db.add(w)
    db.flush()

    sub = Subscription(workshop_id=w.id, plan="basic", status="expired")
    db.add(sub)

    ms = MarketplaceSettings(workshop_id=w.id, allow_attendant_purchase=False, default_markup_percent=20, pricing_mode="markup", pro_feature_enabled=False)
    db.add(ms)

    db.flush()
    return w


def assert_no_workshops_exist(db: Session) -> None:
    exists = db.query(Workshop.id).limit(1).first()
    if exists:
        raise AppException(409, "already_setup", "Sistema já foi configurado.")