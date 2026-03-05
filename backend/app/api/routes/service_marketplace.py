import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.core.errors import AppException
from app.services.marketplace_service import add_order_items_to_service

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/{service_id}/items/from-marketplace")
def items_from_marketplace(
    service_id: str,
    order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        sid = uuid.UUID(service_id)
        oid = uuid.UUID(order_id)
    except ValueError:
        raise AppException(400, "invalid_id", "ID inválido.")

    s = add_order_items_to_service(db, user=user, service_id=sid, order_id=oid)
    db.commit()
    return {"ok": True, "service_id": str(s.id)}