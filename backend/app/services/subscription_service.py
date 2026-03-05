from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.enums import SubscriptionPlan, SubscriptionStatus


# =========================
# BASE
# =========================

def get_subscription(db: Session, workshop_id) -> Optional[Subscription]:
    return (
        db.query(Subscription)
        .filter(Subscription.workshop_id == workshop_id)
        .one_or_none()
    )


def ensure_subscription(db: Session, workshop_id) -> Subscription:
    sub = get_subscription(db, workshop_id)

    if sub:
        if not sub.status:
            sub.status = SubscriptionStatus.active.value
            db.add(sub)
            db.commit()
            db.refresh(sub)
        return sub

    sub = Subscription(
        workshop_id=workshop_id,
        plan=SubscriptionPlan.basic.value,
        status=SubscriptionStatus.active.value,
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)

    return sub


# =========================
# KIWIFY HELPERS
# =========================

def resolve_workshop_id_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extrai o workshop_id do payload da Kiwify.
    Aceita campos comuns e também estruturas aninhadas.
    Retorna string UUID (ou None).
    """
    keys = [
        "workshop_id",
        "tenant_id",
        "workspace_id",
        "account_id",
        "external_id",
        "reference",
        "ref",
        "custom_id",
        "metadata_workshop_id",
    ]

    # 1) topo
    for k in keys:
        v = payload.get(k)
        if v:
            return str(v).strip()

    # 2) metadata (bem comum)
    meta = payload.get("metadata")
    if isinstance(meta, dict):
        for k in keys + ["workshop_id"]:
            v = meta.get(k)
            if v:
                return str(v).strip()

    # 3) data / order / sale / customer
    for obj_key in ["data", "order", "sale", "customer", "subscription", "payment"]:
        obj = payload.get(obj_key)
        if isinstance(obj, dict):
            for k in keys + ["workshop_id"]:
                v = obj.get(k)
                if v:
                    return str(v).strip()

    return None


def resolve_plan_from_payload(payload: Dict[str, Any]) -> str:
    raw = (
        payload.get("plan")
        or payload.get("plano")
        or payload.get("plan_name")
        or payload.get("product_name")
        or payload.get("produto")
        or ""
    )

    raw_s = str(raw).strip().lower()

    if "pro" in raw_s:
        return SubscriptionPlan.pro.value

    return SubscriptionPlan.basic.value


def resolve_transaction_id(payload: Dict[str, Any]) -> Optional[str]:
    keys = [
        "transaction_id",
        "kiwify_transaction_id",
        "order_id",
        "sale_id",
        "payment_id",
        "charge_id",
        "id",
    ]

    for k in keys:
        value = payload.get(k)
        if value:
            return str(value)

    for obj_key in ["order", "sale", "payment", "subscription", "data"]:
        obj = payload.get(obj_key)
        if isinstance(obj, dict):
            for k in keys:
                value = obj.get(k)
                if value:
                    return str(value)

    return None


def resolve_period_end(payload: Dict[str, Any]) -> Optional[datetime]:
    candidates = [
        payload.get("current_period_end"),
        payload.get("current_period_end_at"),
        payload.get("next_charge_at"),
        payload.get("next_payment_at"),
        payload.get("next_payment_date"),
        payload.get("next_billing_date"),
        payload.get("expires_at"),
        payload.get("expiration_date"),
    ]

    value = next((c for c in candidates if c not in (None, "", 0)), None)

    if value is None:
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None

    s = str(value).strip()

    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"

        dt = datetime.fromisoformat(s)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    except Exception:
        return None


# ---- Aliases de compatibilidade (caso seu kiwify.py importe esses nomes) ----
resolve_plan_from_payload = resolve_plan_from_payload
resolve_transaction_id = resolve_transaction_id
resolve_period_end = resolve_period_end
resolve_workshop_id_from_payload = resolve_workshop_id_from_payload


# =========================
# WEBHOOK HANDLERS
# =========================

def activate_subscription_from_kiwify(
    db: Session,
    *,
    workshop_id,
    payload: Dict[str, Any],
) -> Subscription:
    sub = ensure_subscription(db, workshop_id)

    sub.plan = resolve_plan_from_payload(payload)
    sub.status = SubscriptionStatus.active.value

    tx = resolve_transaction_id(payload)
    if tx:
        sub.kiwify_transaction_id = tx

    period_end = resolve_period_end(payload)
    if period_end:
        sub.current_period_end = period_end

    db.add(sub)
    db.commit()
    db.refresh(sub)

    return sub


def cancel_subscription(
    db: Session,
    *,
    workshop_id,
) -> Subscription:
    sub = ensure_subscription(db, workshop_id)

    sub.status = SubscriptionStatus.canceled.value

    db.add(sub)
    db.commit()
    db.refresh(sub)

    return sub