from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import UserRole
from app.core.security import create_access_token, hash_password, verify_password
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import BootstrapRequest, BootstrapResponse, LoginRequest, TokenResponse, UserMeResponse

router = APIRouter()


def _build_token(user: User) -> str:
    return create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role.value},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


@router.post("/setup", response_model=BootstrapResponse)
def setup_system(payload: BootstrapRequest, db: Session = Depends(get_db)) -> BootstrapResponse:
    if db.query(User).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sistema ja inicializado")

    tenant = Tenant(name=payload.tenant_name, document=payload.tenant_document)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        name=payload.admin_name,
        email=payload.admin_email,
        password_hash=hash_password(payload.admin_password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(tenant)
    db.refresh(user)
    return BootstrapResponse(access_token=_build_token(user), tenant_id=tenant.id, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    tenant = (
        db.query(Tenant)
        .filter(or_(Tenant.document == payload.tenant_key, Tenant.name == payload.tenant_key))
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant nao encontrado")

    user = (
        db.query(User)
        .filter(User.tenant_id == tenant.id, User.email == payload.email)
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    return TokenResponse(access_token=_build_token(user))


@router.get("/me", response_model=UserMeResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

