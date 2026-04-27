from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import StatusContrato
from app.models.base import Base, IDMixin, TimestampMixin


class Contract(Base, IDMixin, TimestampMixin):
    __tablename__ = "contracts"
    __table_args__ = (UniqueConstraint("tenant_id", "number", name="uq_contract_tenant_number"),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(30), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[StatusContrato] = mapped_column(Enum(StatusContrato), default=StatusContrato.RASCUNHO, nullable=False)
    billing_day: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    monthly_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    franchise_pb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    franchise_color: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_excess_pb: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    price_excess_color: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    tenant = relationship("Tenant", back_populates="contracts")
    client = relationship("Client", back_populates="contracts")
    plan = relationship("Plan", back_populates="contracts")
    equipments = relationship("ContractEquipment", back_populates="contract", cascade="all, delete-orphan")
    readings = relationship("Reading", back_populates="contract", cascade="all, delete-orphan")


class ContractEquipment(Base, IDMixin, TimestampMixin):
    __tablename__ = "contract_equipments"

    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False, index=True)
    installed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    removed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    contract = relationship("Contract", back_populates="equipments")
    equipment = relationship("Equipment", back_populates="contracts")

