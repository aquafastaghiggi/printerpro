from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Tenant(Base, IDMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    document: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="tenant", cascade="all, delete-orphan")
    equipments = relationship("Equipment", back_populates="tenant", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="tenant", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="tenant", cascade="all, delete-orphan")
    readings = relationship("Reading", back_populates="tenant", cascade="all, delete-orphan")
    fiscal_config = relationship("FiscalConfig", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    fiscal_documents = relationship("FiscalDocument", back_populates="tenant", cascade="all, delete-orphan")
    portal_tickets = relationship("PortalTicket", back_populates="tenant", cascade="all, delete-orphan")
