from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import IDResponse, ORMModel


class OperationalNotificationRead(IDResponse, ORMModel):
    tenant_id: int
    source_type: str
    source_key: str
    severity: Literal["critical", "warning", "info"]
    title: str
    detail: str
    suggested_action: str
    is_read: bool


class OperationalNotificationCreate(BaseModel):
    source_type: str
    source_key: str
    severity: Literal["critical", "warning", "info"]
    title: str
    detail: str
    suggested_action: str


class NotificationSyncResponse(BaseModel):
    created: int
    updated: int
    total: int
    generated_at: datetime


class NotificationDispatchResponse(BaseModel):
    notifications_count: int
    email_sent: bool
    whatsapp_sent: bool
    email_recipient: str | None = None
    whatsapp_recipient: str | None = None
    subject: str
    generated_at: datetime
