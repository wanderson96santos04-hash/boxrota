from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.db.deps import get_db
from app.models.quote import Quote

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/q/{token}", response_class=HTMLResponse)
def public_quote(token: str, db: Session = Depends(get_db)):
    if not token or len(token) < 8:
        raise AppException(404, "not_found", "Orçamento não encontrado.")

    q = db.query(Quote).filter(Quote.public_token == token).one_or_none()
    if not q:
        raise AppException(404, "not_found", "Orçamento não encontrado.")

    from app.services.quote_service import render_public_quote_html

    html = render_public_quote_html(q)
    return HTMLResponse(content=html)