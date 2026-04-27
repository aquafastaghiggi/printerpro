from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.enums import UserRole
from app.schemas.common import ORMModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    tenant_key: str
    email: EmailStr
    password: str


class UserMeResponse(ORMModel):
    id: int
    tenant_id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool


class BootstrapRequest(BaseModel):
    tenant_name: str
    tenant_document: str
    admin_name: str
    admin_email: EmailStr
    admin_password: str


class BootstrapResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: int
    user_id: int
