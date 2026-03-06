import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_secret,
    new_jti,
    verify_password,
    verify_refresh_secret,
)
from app.models.enums import UserRole
from app.models.user import RefreshToken, User
from app.models.workshop import Workshop
from app.services.subscription_service import ensure_subscription


def create_admin_user(db: Session, *, workshop: Workshop, name: str, email: str, password: str) -> User:
    email_norm = email.strip().lower()

    exists = (
        db.query(User.id)
        .filter(
            User.workshop_id == workshop.id,
            User.email == email_norm,
        )
        .first()
    )
    if exists:
        raise AppException(409, "email_in_use", "E-mail já cadastrado nesta oficina.")

    user = User(
        workshop_id=workshop.id,
        name=name.strip(),
        email=email_norm,
        role=UserRole.admin.value,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _issue_tokens(db: Session, *, user: User) -> tuple[str, str]:
    jti = new_jti()
    secret = str(uuid.uuid4())
    token_hash = hash_refresh_secret(secret)

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    refresh_row = RefreshToken(
        workshop_id=user.workshop_id,
        user_id=user.id,
        jti=jti,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=None,
    )
    db.add(refresh_row)
    db.flush()

    refresh_jwt = create_refresh_token(
        subject=str(user.id),
        workshop_id=str(user.workshop_id),
        role=user.role,
        jti=jti,
    )

    refresh_token = f"{refresh_jwt}.{secret}"

    access_token = create_access_token(
        subject=str(user.id),
        workshop_id=str(user.workshop_id),
        role=user.role,
    )

    return access_token, refresh_token


def login(db: Session, *, workshop_id: uuid.UUID, email: str, password: str) -> tuple[User, str, str]:
    email_norm = email.strip().lower()

    user = (
        db.query(User)
        .filter(
            User.workshop_id == workshop_id,
            User.email == email_norm,
            User.is_active.is_(True),
        )
        .one_or_none()
    )

    if user is None:
        raise AppException(401, "invalid_credentials", "E-mail ou senha inválidos.")

    if not verify_password(password, user.password_hash):
        raise AppException(401, "invalid_credentials", "E-mail ou senha inválidos.")

    access_token, refresh_token = _issue_tokens(db, user=user)
    return user, access_token, refresh_token


def refresh(db: Session, *, refresh_token: str) -> tuple[User, str, str]:
    if "." not in refresh_token:
        raise AppException(401, "invalid_token", "Token inválido.")

    refresh_jwt, secret = refresh_token.rsplit(".", 1)

    try:
        payload = decode_token(refresh_jwt)
    except Exception:
        raise AppException(401, "invalid_token", "Token inválido.")

    if payload.get("type") != "refresh":
        raise AppException(401, "invalid_token", "Token inválido.")

    sub = payload.get("sub")
    wid = payload.get("workshop_id")
    jti = payload.get("jti")

    if not sub or not wid or not jti:
        raise AppException(401, "invalid_token", "Token inválido.")

    try:
        user_id = uuid.UUID(str(sub))
        workshop_id = uuid.UUID(str(wid))
    except ValueError:
        raise AppException(401, "invalid_token", "Token inválido.")

    token_row = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.workshop_id == workshop_id,
            RefreshToken.user_id == user_id,
            RefreshToken.jti == str(jti),
        )
        .one_or_none()
    )

    if not token_row or token_row.revoked_at is not None:
        raise AppException(401, "invalid_token", "Token inválido.")

    now = datetime.now(timezone.utc)

    if token_row.expires_at <= now:
        raise AppException(401, "expired_token", "Sessão expirada.")

    if not verify_refresh_secret(secret, token_row.token_hash):
        raise AppException(401, "invalid_token", "Token inválido.")

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.workshop_id == workshop_id,
            User.is_active.is_(True),
        )
        .one_or_none()
    )
    if not user:
        raise AppException(401, "auth_required", "Autenticação necessária.")

    token_row.revoked_at = now
    db.add(token_row)
    db.flush()

    access_token, new_refresh_token = _issue_tokens(db, user=user)
    return user, access_token, new_refresh_token


def logout(db: Session, *, refresh_token: str) -> None:
    if "." not in refresh_token:
        return

    refresh_jwt, secret = refresh_token.rsplit(".", 1)

    try:
        payload = decode_token(refresh_jwt)
    except Exception:
        return

    if payload.get("type") != "refresh":
        return

    sub = payload.get("sub")
    wid = payload.get("workshop_id")
    jti = payload.get("jti")

    if not sub or not wid or not jti:
        return

    try:
        user_id = uuid.UUID(str(sub))
        workshop_id = uuid.UUID(str(wid))
    except ValueError:
        return

    token_row = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.workshop_id == workshop_id,
            RefreshToken.user_id == user_id,
            RefreshToken.jti == str(jti),
        )
        .one_or_none()
    )

    if not token_row or token_row.revoked_at is not None:
        return

    if not verify_refresh_secret(secret, token_row.token_hash):
        return

    token_row.revoked_at = datetime.now(timezone.utc)
    db.add(token_row)
    db.flush()


def setup_subscription_for_workshop(db: Session, *, workshop: Workshop) -> None:
    ensure_subscription(db, workshop.id)