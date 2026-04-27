from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import IDResponse, ORMModel


class TenantCreate(BaseModel):
    name: str
    document: str | None = None


class TenantUpdate(BaseModel):
    name: str | None = None
    document: str | None = None
    is_active: bool | None = None


class TenantRead(IDResponse, ORMModel):
    name: str
    document: str | None = None
    is_active: bool

