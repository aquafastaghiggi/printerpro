from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from app.core.enums import PrioridadeChamado, StatusChamado
from app.schemas.common import IDResponse, ORMModel


class PortalLoginRequest(BaseModel):
    tenant_key: str
    client_document: str


class PortalTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    client_id: int
    tenant_id: int
    client_name: str


class PortalSummaryResponse(BaseModel):
    contracts: int
    equipments: int
    readings: int
    boletos_open: int
    tickets_open: int
    last_reading_at: datetime | None = None


class PortalReadingCreate(BaseModel):
    contract_id: int
    equipment_id: int
    reference_date: date
    counter_pb_current: int
    counter_pb_previous: int = 0
    counter_color_current: int
    counter_color_previous: int = 0
    notes: str | None = None


class PortalTicketCreate(BaseModel):
    subject: str
    description: str
    contract_id: int | None = None
    equipment_id: int | None = None
    priority: PrioridadeChamado = PrioridadeChamado.MEDIA


class PortalTicketRead(IDResponse, ORMModel):
    tenant_id: int
    client_id: int
    contract_id: int | None = None
    equipment_id: int | None = None
    subject: str
    description: str
    priority: PrioridadeChamado
    status: StatusChamado
    last_response_at: datetime | None = None
    resolved_at: datetime | None = None


class PortalReportResponse(BaseModel):
    client_name: str
    contracts: int
    readings: int
    tickets_open: int
    boletos_open: int
    total_due: Decimal

