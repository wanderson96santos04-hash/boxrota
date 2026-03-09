import uuid
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.models.subscription import Subscription


def is_pro_active(db: Session, *, workshop_id: uuid.UUID) -> bool:
    from app.models.enums import SubscriptionPlan, SubscriptionStatus

    sub = (
        db.query(Subscription)
        .filter(Subscription.workshop_id == workshop_id)
        .one_or_none()
    )
    if not sub:
        return False
    return (
        sub.status == SubscriptionStatus.active.value
        and sub.plan == SubscriptionPlan.pro.value
    )


def require_pro(db: Session, *, workshop_id: uuid.UUID) -> None:
    if not is_pro_active(db, workshop_id=workshop_id):
        raise AppException(402, "pro_required", "Desbloqueie o Marketplace Pro para usar esta função.")