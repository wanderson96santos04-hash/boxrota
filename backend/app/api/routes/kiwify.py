from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.settings import settings
from app.db.deps import get_db
from app.services.subscription_service import (
    activate_subscription_from_kiwify,
    cancel_subscription,
    resolve_workshop_id_from_payload,
)

router = APIRouter(prefix="/kiwify", tags=["kiwify"])


def _get_webhook_secret() -> str:
    secret = getattr(settings, "KIWIFY_WEBHOOK_SECRET", None)
    if not secret or not str(secret).strip():
        raise RuntimeError("KIWIFY_WEBHOOK_SECRET não configurado no settings/.env")
    return str(secret).strip()


def _is_cancel_event(payload: Dict[str, Any]) -> bool:
    """
    Heurística: identifica evento de cancelamento/estorno/chargeback.
    (Kiwify pode variar nomes, então fazemos tolerante.)
    """
    event = str(payload.get("event") or payload.get("type") or "").lower().strip()
    status = str(payload.get("status") or payload.get("payment_status") or "").lower().strip()

    cancel_words = [
        "cancel", "canceled", "cancelled",
        "refund", "refunded",
        "chargeback",
        "expired",
        "rejected",
        "failed",
    ]

    hay = f"{event} {status}"
    return any(w in hay for w in cancel_words)


@router.post("/webhook")
async def kiwify_webhook(
    request: Request,
    db: Session = Depends(get_db),
    # aceita alguns nomes comuns de header (você ajusta no painel da kiwify)
    x_kiwify_secret: Optional[str] = Header(default=None, alias="X-Kiwify-Secret"),
    x_webhook_secret: Optional[str] = Header(default=None, alias="X-Webhook-Secret"),
    x_api_key: Optional[str] = Header(default=None, alias="X-Api-Key"),
):
    # ---- Segurança do Webhook ----
    expected = _get_webhook_secret()
    provided = (x_kiwify_secret or x_webhook_secret or x_api_key or "").strip()

    if not provided or provided != expected:
        raise AppException(401, "invalid_webhook_secret", "Webhook secret inválido.")

    # ---- Payload ----
    try:
        payload = await request.json()
    except Exception:
        raise AppException(400, "invalid_payload", "JSON inválido.")

    if not isinstance(payload, dict):
        raise AppException(400, "invalid_payload", "Payload precisa ser um objeto JSON.")

    # ---- Descobrir workshop ----
    wid = resolve_workshop_id_from_payload(payload)
    if not wid:
        raise AppException(
            400,
            "missing_workshop_id",
            "Não encontrei workshop_id no payload (metadata/workshop_id).",
        )

    # wid pode vir como string UUID
    # a service já garante assinatura criada e atualiza
    if _is_cancel_event(payload):
        cancel_subscription(db, workshop_id=wid)
        return {"ok": True, "action": "canceled", "workshop_id": wid}

    activate_subscription_from_kiwify(db, workshop_id=wid, payload=payload)
    return {"ok": True, "action": "activated", "workshop_id": wid}


@router.get("/ping")
def ping():
    return {"ok": True}