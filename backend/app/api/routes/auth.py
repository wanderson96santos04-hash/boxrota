import uuid

from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.models.workshop import Workshop
from app.schemas.auth import LoginRequest, RefreshRequest, SetupPayload, SetupResponse, TokenPair
from app.schemas.user import UserOut
from app.schemas.workshop import WorkshopOut
from app.services.auth_service import create_admin_user, login, logout, refresh
from app.services.workshop_service import assert_no_workshops_exist, create_workshop

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/setup", response_model=SetupResponse)
def setup(payload: SetupPayload, db: Session = Depends(get_db)):
    assert_no_workshops_exist(db)

    workshop = create_workshop(
        db,
        name=payload.workshop.name,
        phone=payload.workshop.phone,
        city=payload.workshop.city,
    )

    create_admin_user(
        db,
        workshop=workshop,
        name=payload.admin.name,
        email=payload.admin.email,
        password=payload.admin.password,
    )

    user, access_token, refresh_token = login(
        db,
        workshop_id=workshop.id,
        email=payload.admin.email,
        password=payload.admin.password,
    )

    db.commit()

    return SetupResponse(
        workshop=WorkshopOut.model_validate(workshop),
        user=UserOut.model_validate(user),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/login")
def login_endpoint(
    body: LoginRequest,
    db: Session = Depends(get_db),
    workshop_id: str | None = None,
    slug: str | None = None,
):
    workshop = None

    if slug:
        slug_norm = slug.strip().lower()
        workshop = (
            db.query(Workshop)
            .filter(Workshop.slug == slug_norm)
            .one_or_none()
        )
        if not workshop:
            raise AppException(404, "workshop_not_found", "Oficina não encontrada.")

    elif workshop_id:
        try:
            wid = uuid.UUID(workshop_id)
        except ValueError:
            raise AppException(400, "invalid_workshop_id", "workshop_id inválido.")

        workshop = (
            db.query(Workshop)
            .filter(Workshop.id == wid)
            .one_or_none()
        )
        if not workshop:
            raise AppException(404, "workshop_not_found", "Oficina não encontrada.")

    else:
        raise AppException(
            400,
            "missing_login_scope",
            "Informe slug ou workshop_id para realizar o login.",
        )

    user, access_token, refresh_token = login(
        db,
        workshop_id=workshop.id,
        email=body.email,
        password=body.password,
    )

    db.commit()

    return {
        "user": UserOut.model_validate(user),
        "workshop": WorkshopOut.model_validate(workshop),
        "tokens": TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        ).model_dump(),
    }


@router.post("/refresh")
def refresh_endpoint(body: RefreshRequest, db: Session = Depends(get_db)):
    user, access_token, refresh_token = refresh(db, refresh_token=body.refresh_token)
    db.commit()

    return {
        "user": UserOut.model_validate(user),
        "tokens": TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        ).model_dump(),
    }


@router.post("/logout")
def logout_endpoint(body: RefreshRequest, db: Session = Depends(get_db)):
    logout(db, refresh_token=body.refresh_token)
    db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


# TEMPORÁRIO: manter só durante desenvolvimento
@router.post("/dev-reset-password")
def dev_reset_password(
    workshop_id: str,
    email: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    try:
        wid = uuid.UUID(workshop_id)
    except ValueError:
        raise AppException(400, "invalid_workshop_id", "workshop_id inválido.")

    user = (
        db.query(User)
        .filter(
            User.workshop_id == wid,
            User.email == email.strip().lower(),
        )
        .one_or_none()
    )

    if not user:
        raise AppException(404, "user_not_found", "Usuário não encontrado.")

    user.password_hash = pwd_context.hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "ok": True,
        "message": "Senha redefinida com sucesso.",
        "email": user.email,
        "workshop_id": str(user.workshop_id),
        "user_id": str(user.id),
    }