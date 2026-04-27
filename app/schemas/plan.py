from __future__ import annotations

from pydantic import BaseModel

from app.core.enums import TipoPlano
from app.schemas.common import IDResponse, ORMModel


class PlanCreate(BaseModel):
    name: str
    type: TipoPlano
    monthly_fee: float | None = None
    price_pb: float | None = None
    price_color: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    extra_pb: float | None = None
    extra_color: float | None = None


class PlanUpdate(BaseModel):
    name: str | None = None
    type: TipoPlano | None = None
    monthly_fee: float | None = None
    price_pb: float | None = None
    price_color: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    extra_pb: float | None = None
    extra_color: float | None = None
    is_active: bool | None = None


class PlanRead(IDResponse, ORMModel):
    tenant_id: int
    name: str
    type: TipoPlano
    monthly_fee: float | None = None
    price_pb: float | None = None
    price_color: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    extra_pb: float | None = None
    extra_color: float | None = None
    is_active: bool

