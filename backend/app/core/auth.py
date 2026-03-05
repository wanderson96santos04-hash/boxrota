import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.security import decode_token
from app.db.deps import get_db
from app.models.enums import UserRole
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def _get_user(db: Session, user_id: uuid.UUID, workshop_id: uuid.UUID) -> User:
    user = (
        db.query(User)
        .filter(User.id == user_id, User.workshop_id == workshop_id, User.is_active.is_(True))
        .one_or_none()
    )
    if not user:
        raise AppException(401, "auth_required", "Autenticação necessária.")
    return user


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if not creds or not creds.credentials:
        raise AppException(401, "auth_required", "Autenticação necessária.")
    payload = decode_token(creds.credentials)
    if payload.get("type") != "access":
        raise AppException(401, "invalid_token", "Token inválido.")
    sub = payload.get("sub")
    wid = payload.get("workshop_id")
    if not sub or not wid:
        raise AppException(401, "invalid_token", "Token inválido.")
    try:
        user_id = uuid.UUID(str(sub))
        workshop_id = uuid.UUID(str(wid))
    except ValueError:
        raise AppException(401, "invalid_token", "Token inválido.")
    return _get_user(db, user_id, workshop_id)


def require_role(*allowed: UserRole):
    allowed_set = {a.value for a in allowed}

    def _dep(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed_set:
            raise AppException(403, "forbidden", "Sem permissão para esta ação.")
        return user

    return _dep