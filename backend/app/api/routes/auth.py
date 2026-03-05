import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, SetupPayload, SetupResponse, TokenPair
from app.schemas.user import UserOut
from app.schemas.workshop import WorkshopOut
from app.services.auth_service import create_admin_user, login, logout, refresh
from app.services.workshop_service import assert_no_workshops_exist, create_workshop

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/setup", response_model=SetupResponse)
def setup(payload: SetupPayload, db: Session = Depends(get_db)):
    assert_no_workshops_exist(db)

    w = create_workshop(
        db,
        name=payload.workshop.name,
        phone=payload.workshop.phone,
        city=payload.workshop.city,
    )
    u = create_admin_user(
        db,
        workshop=w,
        name=payload.admin.name,
        email=payload.admin.email,
        password=payload.admin.password,
    )
    user, access, refresh_token = login(db, workshop_id=w.id, email=payload.admin.email, password=payload.admin.password)
    db.commit()

    return SetupResponse(
        workshop=WorkshopOut.model_validate(w),
        user=UserOut.model_validate(user),
        tokens=TokenPair(access_token=access, refresh_token=refresh_token),
    )


@router.post("/login")
def login_endpoint(workshop_id: str, body: LoginRequest, db: Session = Depends(get_db)):
    try:
        wid = uuid.UUID(workshop_id)
    except ValueError:
        raise AppException(400, "invalid_workshop_id", "workshop_id inválido.")
    user, access, refresh_token = login(db, workshop_id=wid, email=body.email, password=body.password)
    db.commit()
    return {
        "user": UserOut.model_validate(user),
        "tokens": TokenPair(access_token=access, refresh_token=refresh_token).model_dump(),
    }


@router.post("/refresh")
def refresh_endpoint(body: RefreshRequest, db: Session = Depends(get_db)):
    user, access, refresh_token = refresh(db, refresh_token=body.refresh_token)
    db.commit()
    return {
        "user": UserOut.model_validate(user),
        "tokens": TokenPair(access_token=access, refresh_token=refresh_token).model_dump(),
    }


@router.post("/logout")
def logout_endpoint(body: RefreshRequest, db: Session = Depends(get_db)):
    logout(db, refresh_token=body.refresh_token)
    db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)