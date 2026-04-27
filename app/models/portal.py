from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PrioridadeChamado, StatusChamado
from app.models.base import Base, IDMixin, TimestampMixin


class PortalTicket(Base, IDMixin, TimestampMixin):
    __tablename__ = "portal_tickets"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True, index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipments.id"), nullable=True, index=True)
    subject: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[PrioridadeChamado] = mapped_column(Enum(PrioridadeChamado), default=PrioridadeChamado.MEDIA, nullable=False)
    status: Mapped[StatusChamado] = mapped_column(Enum(StatusChamado), default=StatusChamado.ABERTO, nullable=False)
    last_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="portal_tickets")
    client = relationship("Client", back_populates="portal_tickets")
    contract = relationship("Contract")
    equipment = relationship("Equipment")
