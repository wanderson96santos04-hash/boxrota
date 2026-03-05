import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")
ALGORITHM = settings.JWT_ALGORITHM


def _jwt_secret_key() -> str:
    secret = (
        getattr(settings, "JWT_SECRET_KEY", None)
        or getattr(settings, "JWT_SECRET", None)
        or getattr(settings, "SECRET_KEY", None)
        or os.getenv("JWT_SECRET_KEY")
        or os.getenv("JWT_SECRET")
        or os.getenv("SECRET_KEY")
    )
    if not secret or not str(secret).strip():
        raise RuntimeError(
            "JWT secret key não configurada (JWT_SECRET_KEY ou JWT_SECRET ou SECRET_KEY)."
        )
    return str(secret)


def new_jti() -> str:
    return str(uuid.uuid4())


def hash_refresh_secret(secret: str) -> str:
    return pwd_context.hash(secret)


def verify_refresh_secret(secret: str, token_hash: str) -> bool:
    try:
        return pwd_context.verify(secret, token_hash)
    except Exception:
        return False


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password, password_hash)
    except Exception:
        return False


def _create_jwt(payload: Dict[str, Any], *, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode = dict(payload)
    to_encode["iat"] = int(now.timestamp())
    to_encode["exp"] = int((now + expires_delta).timestamp())
    return jwt.encode(to_encode, _jwt_secret_key(), algorithm=ALGORITHM)


def create_access_token(*, subject: str, workshop_id: str, role: str) -> str:
    payload = {
        "type": "access",
        "sub": subject,
        "workshop_id": workshop_id,
        "role": role,
    }
    return _create_jwt(payload, expires_delta=timedelta(minutes=settings.JWT_ACCESS_EXPIRES_MIN))


def create_refresh_token(*, subject: str, workshop_id: str, role: str, jti: str) -> str:
    payload = {
        "type": "refresh",
        "sub": subject,
        "workshop_id": workshop_id,
        "role": role,
        "jti": jti,
    }
    return _create_jwt(payload, expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRES_DAYS))


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, _jwt_secret_key(), algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        return {"type": "invalid", "error": "expired"}
    except JWTError:
        return {"type": "invalid", "error": "invalid"}