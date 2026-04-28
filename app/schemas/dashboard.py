from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.core.enums import StatusEquipamento


class DashboardMetricsRead(BaseModel):
    clients_total: int
    active_contracts: int
    active_equipment: int
    readings_last_30_days: int
    open_tickets: int
    contracts_expiring_30_days: int
    unvalidated_readings: int
    receivables_open_total: Decimal
    receivables_overdue_total: Decimal
    payables_overdue_total: Decimal


class DashboardAlertRead(BaseModel):
    severity: Literal["critical", "warning", "info"]
    title: str
    detail: str
    suggested_action: str
    count: int


class DashboardRenewalRead(BaseModel):
    contract_id: int
    number: str
    client_name: str
    end_date: date
    days_left: int
    status: str


class DashboardClientInsightRead(BaseModel):
    client_id: int
    client_name: str
    contracts: int
    open_total: Decimal
    overdue_total: Decimal


class DashboardEquipmentIssueRead(BaseModel):
    equipment_id: int
    serial_number: str
    brand: str
    model: str
    client_name: str | None = None
    location: str | None = None
    status: StatusEquipamento
    issue: str


class DashboardSeriesPointRead(BaseModel):
    label: str
    value: Decimal


class DashboardBreakdownPointRead(BaseModel):
    label: str
    count: int


class DashboardBIRead(BaseModel):
    revenue_by_month: list[DashboardSeriesPointRead] = Field(default_factory=list)
    readings_by_month: list[DashboardSeriesPointRead] = Field(default_factory=list)
    equipment_status: list[DashboardBreakdownPointRead] = Field(default_factory=list)
    maintenance_status: list[DashboardBreakdownPointRead] = Field(default_factory=list)
    maintenance_open_total: int = 0


class DashboardOverviewResponse(BaseModel):
    generated_at: datetime
    metrics: DashboardMetricsRead
    alerts: list[DashboardAlertRead] = Field(default_factory=list)
    renewals: list[DashboardRenewalRead] = Field(default_factory=list)
    top_clients: list[DashboardClientInsightRead] = Field(default_factory=list)
    equipment_issues: list[DashboardEquipmentIssueRead] = Field(default_factory=list)
    bi: DashboardBIRead = Field(default_factory=DashboardBIRead)
