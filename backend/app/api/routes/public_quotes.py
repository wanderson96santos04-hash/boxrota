from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.deps import get_db
from app.services.quote_service import get_public_html

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/q/{token}")
def public_quote(token: str, db: Session = Depends(get_db)):
    html = get_public_html(db, token=token, app_public_base=settings.APP_URL)
    db.commit()
    return HTMLResponse(content=html, status_code=200)