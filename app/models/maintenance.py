from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PrioridadeChamado, StatusManutencao
from app.models.base import Base, IDMixin, TimestampMixin


class MaintenanceTask(Base, IDMixin, TimestampMixin):
    __tablename__ = "maintenance_tasks"
    __table_args__ = (UniqueConstraint("tenant_id", "source_key", name="uq_maintenance_tenant_source_key"),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipments.id"), nullable=True, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[PrioridadeChamado] = mapped_column(Enum(PrioridadeChamado), default=PrioridadeChamado.MEDIA, nullable=False)
    status: Mapped[StatusManutencao] = mapped_column(Enum(StatusManutencao), default=StatusManutencao.PENDENTE, nullable=False)
    scheduled_for: Mapped[date | None] = mapped_column(Date, nullable=True)
    technician_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    equipment = relationship("Equipment")
    contract = relationship("Contract")
    client = relationship("Client")
