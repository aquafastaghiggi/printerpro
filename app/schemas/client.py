from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.enums import PessoaTipo
from app.schemas.common import IDResponse, ORMModel


class ClientCreate(BaseModel):
    person_type: PessoaTipo
    name: str
    document: str
    email: EmailStr | None = None
    phone: str | None = None
    credit_score: int | None = None
    credit_status: str | None = None


class ClientUpdate(BaseModel):
    person_type: PessoaTipo | None = None
    name: str | None = None
    document: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    credit_score: int | None = None
    credit_status: str | None = None


class ClientRead(IDResponse, ORMModel):
    tenant_id: int
    person_type: PessoaTipo
    name: str
    document: str
    email: EmailStr | None = None
    phone: str | None = None
    credit_score: int | None = None
    credit_status: str | None = None

