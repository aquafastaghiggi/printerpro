from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.enums import UserRole
from app.models.client import Client
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
portal_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/portal/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        if payload.get("role") == "portal":
            raise ValueError("Token portal invalido para este recurso")
        user_id = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido ou inativo")
    return user


def get_current_portal_client(token: str = Depends(portal_oauth2_scheme), db: Session = Depends(get_db)) -> Client:
    try:
        payload = decode_access_token(token)
        if payload.get("role") != "portal":
            raise ValueError("Token nao e de portal")
        client_id = int(payload.get("client_id", 0))
        tenant_id = int(payload.get("tenant_id", 0))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado")

    client = db.get(Client, client_id)
    if not client or client.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cliente portal invalido")
    return client
