import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.settings import settings
from app.db.deps import get_db
from app.models.user import User
from app.schemas.quote import QuoteFromServiceResponse, QuoteOut, QuoteStatusUpdate
from app.services.quote_service import create_from_service, get_or_build_html, get_quote, update_status

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/from-service/{service_id}", response_model=QuoteFromServiceResponse)
def from_service(
    service_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sid = uuid.UUID(service_id)
    q = create_from_service(db, user=user, service_id=sid)
    db.commit()
    q = get_quote(db, user=user, quote_id=q.id)
    return QuoteFromServiceResponse(
        quote=QuoteOut(
            id=q.id,
            service_id=q.service_id,
            quote_number=q.quote_number,
            status=q.status,
            public_token=q.public_token,
            subtotal_amount=f"{q.subtotal_amount:.2f}",
            total_amount=f"{q.total_amount:.2f}",
            snapshot=q.snapshot or {},
            created_at=q.created_at,
            updated_at=q.updated_at,
        )
    )


@router.get("/{quote_id}", response_model=QuoteOut)
def get_one(
    quote_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    qid = uuid.UUID(quote_id)
    q = get_quote(db, user=user, quote_id=qid)
    return QuoteOut(
        id=q.id,
        service_id=q.service_id,
        quote_number=q.quote_number,
        status=q.status,
        public_token=q.public_token,
        subtotal_amount=f"{q.subtotal_amount:.2f}",
        total_amount=f"{q.total_amount:.2f}",
        snapshot=q.snapshot or {},
        created_at=q.created_at,
        updated_at=q.updated_at,
    )


@router.get("/{quote_id}/html")
def get_html(
    quote_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    qid = uuid.UUID(quote_id)
    html = get_or_build_html(db, user=user, quote_id=qid, app_public_base=settings.APP_URL)
    db.commit()
    return HTMLResponse(content=html, status_code=200)


@router.post("/{quote_id}/status", response_model=QuoteOut)
def set_status(
    quote_id: str,
    body: QuoteStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    qid = uuid.UUID(quote_id)
    q = update_status(db, user=user, quote_id=qid, status=body.status)
    db.commit()
    q = get_quote(db, user=user, quote_id=q.id)
    return QuoteOut(
        id=q.id,
        service_id=q.service_id,
        quote_number=q.quote_number,
        status=q.status,
        public_token=q.public_token,
        subtotal_amount=f"{q.subtotal_amount:.2f}",
        total_amount=f"{q.total_amount:.2f}",
        snapshot=q.snapshot or {},
        created_at=q.created_at,
        updated_at=q.updated_at,
    )