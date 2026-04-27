from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.core.enums import FonteLeitura
from app.schemas.common import IDResponse, ORMModel


class ReadingCreate(BaseModel):
    contract_id: int
    equipment_id: int
    reference_date: date
    source: FonteLeitura = FonteLeitura.MANUAL
    counter_pb_current: int
    counter_pb_previous: int = 0
    counter_color_current: int
    counter_color_previous: int = 0
    validated: bool = False
    photo_url: str | None = None
    notes: str | None = None


class ReadingUpdate(BaseModel):
    contract_id: int | None = None
    equipment_id: int | None = None
    reference_date: date | None = None
    source: FonteLeitura | None = None
    counter_pb_current: int | None = None
    counter_pb_previous: int | None = None
    counter_color_current: int | None = None
    counter_color_previous: int | None = None
    validated: bool | None = None
    photo_url: str | None = None
    notes: str | None = None


class ReadingRead(IDResponse, ORMModel):
    tenant_id: int
    contract_id: int
    equipment_id: int
    reference_date: date
    source: FonteLeitura
    counter_pb_current: int
    counter_pb_previous: int
    counter_color_current: int
    counter_color_previous: int
    validated: bool
    photo_url: str | None = None
    notes: str | None = None
