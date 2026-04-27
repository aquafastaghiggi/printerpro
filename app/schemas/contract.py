from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.core.enums import StatusContrato
from app.schemas.common import IDResponse, ORMModel


class ContractCreate(BaseModel):
    client_id: int
    plan_id: int
    number: str
    start_date: date
    end_date: date | None = None
    status: StatusContrato = StatusContrato.RASCUNHO
    billing_day: int = 10
    monthly_value: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    price_excess_pb: float | None = None
    price_excess_color: float | None = None
    notes: str | None = None
    equipment_ids: list[int] = Field(default_factory=list)


class ContractUpdate(BaseModel):
    client_id: int | None = None
    plan_id: int | None = None
    number: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: StatusContrato | None = None
    billing_day: int | None = None
    monthly_value: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    price_excess_pb: float | None = None
    price_excess_color: float | None = None
    notes: str | None = None
    equipment_ids: list[int] | None = None


class ContractRead(IDResponse, ORMModel):
    tenant_id: int
    client_id: int
    plan_id: int
    number: str
    start_date: date
    end_date: date | None = None
    status: StatusContrato
    billing_day: int
    monthly_value: float | None = None
    franchise_pb: int | None = None
    franchise_color: int | None = None
    price_excess_pb: float | None = None
    price_excess_color: float | None = None
    notes: str | None = None
    equipments: list[ContractEquipmentItem] = Field(default_factory=list)


class ContractEquipmentItem(BaseModel):
    equipment_id: int
    installed_at: date | None = None
    removed_at: date | None = None
