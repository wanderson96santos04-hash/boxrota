import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.settings import settings
from app.db.deps import get_db
from app.models.enums import SubscriptionPlan, SubscriptionStatus
from app.models.subscription import Subscription

router = APIRouter(prefix="/webhooks/kiwify", tags=["kiwify"])


def _parse_uuid(value: Any) -> Optional[uuid.UUID]:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except Exception:
        return None


def _get_nested(d: Any, *keys: str) -> Any:
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _extract_workshop_id(payload: dict) -> Optional[uuid.UUID]:
    candidates = [
        payload.get("s1"),
        payload.get("workshop_id"),
        _get_nested(payload, "tracking", "s1"),
        _get_nested(payload, "tracking_parameters", "s1"),
        _get_nested(payload, "order", "tracking", "s1"),
        _get_nested(payload, "order", "tracking_parameters", "s1"),
        _get_nested(payload, "data", "tracking", "s1"),
        _get_nested(payload, "data", "tracking_parameters", "s1"),
        _get_nested(payload, "custom", "s1"),
        _get_nested(payload, "metadata", "s1"),
        _get_nested(payload, "metadata", "workshop_id"),
    ]
    for c in candidates:
        wid = _parse_uuid(c)
        if wid:
            return wid
    return None


def _extract_transaction_id(payload: dict) -> Optional[str]:
    candidates = [
        payload.get("transaction_id"),
        payload.get("kiwify_transaction_id"),
        _get_nested(payload, "order", "transaction_id"),
        _get_nested(payload, "order", "id"),
        _get_nested(payload, "data", "transaction_id"),
        _get_nested(payload, "data", "id"),
        _get_nested(payload, "payment", "transaction_id"),
        _get_nested(payload, "payment", "id"),
    ]
    for c in candidates:
        if c and str(c).strip():
            return str(c).strip()
    return None


def _extract_current_period_end(payload: dict) -> Optional[datetime]:
    candidates = [
        payload.get("current_period_end"),
        _get_nested(payload, "subscription", "current_period_end"),
        _get_nested(payload, "data", "current_period_end"),
        _get_nested(payload, "subscription", "next_charge_date"),
        _get_nested(payload, "data", "next_charge_date"),
    ]
    for c in candidates:
        if not c:
            continue
        try:
            if isinstance(c, (int, float)):
                return datetime.fromtimestamp(int(c), tz=timezone.utc)
            s = str(c).strip()
            if s.isdigit():
                return datetime.fromtimestamp(int(s), tz=timezone.utc)
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None


def _validate_secret(
    x_kiwify_secret: Optional[str],
    authorization: Optional[str],
    payload: dict,
) -> None:
    expected = (settings.KIWIFY_WEBHOOK_SECRET or "").strip()
    if not expected:
        raise AppException(500, "kiwify_secret_missing", "KIWIFY_WEBHOOK_SECRET não configurado no servidor.")

    provided = None

    if x_kiwify_secret and x_kiwify_secret.strip():
        provided = x_kiwify_secret.strip()

    if not provided and authorization and authorization.strip():
        a = authorization.strip()
        if a.lower().startswith("bearer "):
            provided = a.split(" ", 1)[1].strip()
        else:
            provided = a

    if not provided:
        provided = str(payload.get("secret") or payload.get("webhook_secret") or "").strip() or None

    if not provided or provided != expected:
        raise AppException(401, "invalid_webhook_secret", "Webhook não autorizado.")


def _get_event(payload: dict) -> str:
    for k in ("event", "type", "name"):
        v = payload.get(k)
        if v and str(v).strip():
            return str(v).strip()
    v = _get_nested(payload, "data", "event")
    if v and str(v).strip():
        return str(v).strip()
    return ""


def _find_subscription(db: Session, *, workshop_id: Optional[uuid.UUID], transaction_id: Optional[str]) -> Optional[Subscription]:
    if workshop_id:
        sub = db.query(Subscription).filter(Subscription.workshop_id == workshop_id).one_or_none()
        if sub:
            return sub
    if transaction_id:
        sub = db.query(Subscription).filter(Subscription.kiwify_transaction_id == transaction_id).one_or_none()
        if sub:
            return sub
    return None


def _activate_pro(sub: Subscription, transaction_id: Optional[str], current_period_end: Optional[datetime]) -> None:
    sub.plan = SubscriptionPlan.pro.value
    sub.status = SubscriptionStatus.active.value
    if transaction_id:
        sub.kiwify_transaction_id = transaction_id
    if current_period_end:
        sub.current_period_end = current_period_end


def _expire(sub: Subscription) -> None:
    sub.plan = SubscriptionPlan.basic.value
    sub.status = SubscriptionStatus.expired.value
    sub.current_period_end = None


@router.post("")
async def kiwify_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_kiwify_secret: Optional[str] = Header(default=None, convert_underscores=False),
    authorization: Optional[str] = Header(default=None),
):
    payload = await request.json()

    _validate_secret(x_kiwify_secret, authorization, payload)

    event = _get_event(payload).lower()
    transaction_id = _extract_transaction_id(payload)
    workshop_id = _extract_workshop_id(payload)
    current_period_end = _extract_current_period_end(payload)

    sub = _find_subscription(db, workshop_id=workshop_id, transaction_id=transaction_id)
    if not sub:
        return {"ok": True}

    activate_events = {
        "order.approved",
        "order.paid",
        "order.paid_approved",
        "payment.approved",
        "payment.paid",
        "subscription.renewed",
        "subscription.active",
        "subscription.activated",
    }
    expire_events = {
        "subscription.canceled",
        "subscription.cancelled",
        "subscription.expired",
        "subscription.failed",
        "payment.failed",
        "order.refunded",
        "order.chargeback",
    }

    if event in activate_events:
        _activate_pro(sub, transaction_id, current_period_end)
    elif event in expire_events:
        _expire(sub)
    else:
        return {"ok": True}

    db.add(sub)
    db.commit()
    return {"ok": True}