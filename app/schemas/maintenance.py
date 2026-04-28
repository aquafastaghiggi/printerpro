from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from app.core.enums import PrioridadeChamado, StatusManutencao
from app.schemas.common import IDResponse, ORMModel


class MaintenanceTaskRead(IDResponse, ORMModel):
    tenant_id: int
    equipment_id: int | None = None
    contract_id: int | None = None
    client_id: int | None = None
    source_type: str
    source_key: str
    title: str
    description: str
    priority: PrioridadeChamado
    status: StatusManutencao
    scheduled_for: date | None = None
    technician_name: str | None = None
    due_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class MaintenanceTaskCreate(BaseModel):
    equipment_id: int | None = None
    contract_id: int | None = None
    client_id: int | None = None
    source_type: str
    source_key: str
    title: str
    description: str
    priority: PrioridadeChamado = PrioridadeChamado.MEDIA
    scheduled_for: date | None = None
    technician_name: str | None = None
    due_date: date | None = None
    notes: str | None = None


class MaintenanceTaskUpdate(BaseModel):
    status: StatusManutencao | None = None
    scheduled_for: date | None = None
    technician_name: str | None = None
    notes: str | None = None


class MaintenanceSyncResponse(BaseModel):
    created: int
    updated: int
    total: int
    generated_at: datetime


class MaintenanceDispatchResponse(BaseModel):
    task_id: int
    email_sent: bool
    whatsapp_sent: bool
    email_recipient: str | None = None
    whatsapp_recipient: str | None = None
    subject: str
    generated_at: datetime
