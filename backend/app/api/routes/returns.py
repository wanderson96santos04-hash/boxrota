import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.returns import (
    ReturnListOut,
    ReturnOut,
    ReturnRuleOut,
    ReturnRuleUpsert,
    ReturnStatusUpdate,
)
from app.services.returns_service import (
    enrich_return_rows,
    get_active_rule,
    get_return,
    list_returns,
    upsert_rule,
    update_return_status,
)

router = APIRouter(prefix="/returns", tags=["returns"])


@router.get("/rule", response_model=ReturnRuleOut)
def get_rule_endpoint(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = get_active_rule(db, workshop_id=user.workshop_id)
    return ReturnRuleOut(
        id=r.id,
        name=r.name,
        days_after=r.days_after,
        active=r.active,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.post("/rule", response_model=ReturnRuleOut)
def upsert_rule_endpoint(
    body: ReturnRuleUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = upsert_rule(db, user=user, name=body.name, days_after=body.days_after, active=body.active)
    db.commit()
    return ReturnRuleOut(
        id=r.id,
        name=r.name,
        days_after=r.days_after,
        active=r.active,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("", response_model=list[ReturnListOut])
def list_endpoint(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=60, ge=1, le=120),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_returns(db, user=user, date_from=date_from, date_to=date_to, status=status, limit=limit)
    enriched = enrich_return_rows(db, user=user, rows=rows)
    return [ReturnListOut(**e) for e in enriched]


@router.get("/{return_id}", response_model=ReturnOut)
def get_endpoint(
    return_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rid = uuid.UUID(return_id)
    r = get_return(db, user=user, return_id=rid)
    enriched = enrich_return_rows(db, user=user, rows=[r])[0]
    return ReturnOut(
        id=r.id,
        customer_id=r.customer_id,
        vehicle_id=r.vehicle_id,
        service_id=r.service_id,
        due_date=r.due_date,
        status=r.status,
        whatsapp_message=r.whatsapp_message,
        sent_at=r.sent_at,
        done_at=r.done_at,
        created_at=r.created_at,
        updated_at=r.updated_at,
        customer_name=enriched.get("customer_name"),
        customer_phone=enriched.get("customer_phone"),
        vehicle_plate=enriched.get("vehicle_plate"),
    )


@router.post("/{return_id}/status", response_model=ReturnOut)
def update_status_endpoint(
    return_id: str,
    body: ReturnStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rid = uuid.UUID(return_id)
    r = update_return_status(db, user=user, return_id=rid, status=body.status)
    db.commit()
    enriched = enrich_return_rows(db, user=user, rows=[r])[0]
    return ReturnOut(
        id=r.id,
        customer_id=r.customer_id,
        vehicle_id=r.vehicle_id,
        service_id=r.service_id,
        due_date=r.due_date,
        status=r.status,
        whatsapp_message=r.whatsapp_message,
        sent_at=r.sent_at,
        done_at=r.done_at,
        created_at=r.created_at,
        updated_at=r.updated_at,
        customer_name=enriched.get("customer_name"),
        customer_phone=enriched.get("customer_phone"),
        vehicle_plate=enriched.get("vehicle_plate"),
    )