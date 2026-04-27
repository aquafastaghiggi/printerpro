from __future__ import annotations

from pydantic import BaseModel

from app.core.enums import StatusEquipamento
from app.schemas.common import IDResponse, ORMModel


class EquipmentCreate(BaseModel):
    client_id: int | None = None
    serial_number: str
    brand: str
    model: str
    kind: str
    status: StatusEquipamento = StatusEquipamento.DISPONIVEL
    location: str | None = None


class EquipmentUpdate(BaseModel):
    client_id: int | None = None
    serial_number: str | None = None
    brand: str | None = None
    model: str | None = None
    kind: str | None = None
    status: StatusEquipamento | None = None
    location: str | None = None


class EquipmentRead(IDResponse, ORMModel):
    tenant_id: int
    client_id: int | None = None
    serial_number: str
    brand: str
    model: str
    kind: str
    status: StatusEquipamento
    location: str | None = None
    last_counter_pb: int
    last_counter_color: int

