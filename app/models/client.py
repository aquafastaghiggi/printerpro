from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PessoaTipo
from app.models.base import Base, IDMixin, TimestampMixin


class Client(Base, IDMixin, TimestampMixin):
    __tablename__ = "clients"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    person_type: Mapped[PessoaTipo] = mapped_column(Enum(PessoaTipo), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    document: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    credit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    credit_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    tenant = relationship("Tenant", back_populates="clients")
    equipments = relationship("Equipment", back_populates="client")
    contracts = relationship("Contract", back_populates="client")
    portal_tickets = relationship("PortalTicket", back_populates="client", cascade="all, delete-orphan")
