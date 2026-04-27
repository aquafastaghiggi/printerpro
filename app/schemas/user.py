from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.enums import UserRole
from app.schemas.common import IDResponse, ORMModel


class UserCreate(BaseModel):
    tenant_id: int
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.LEITURA


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserRead(IDResponse, ORMModel):
    tenant_id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

