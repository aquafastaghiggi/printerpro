from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import FonteLeitura
from app.models.base import Base, IDMixin, TimestampMixin


class Reading(Base, IDMixin, TimestampMixin):
    __tablename__ = "readings"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False, index=True)
    reference_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[FonteLeitura] = mapped_column(Enum(FonteLeitura), default=FonteLeitura.MANUAL, nullable=False)
    counter_pb_current: Mapped[int] = mapped_column(Integer, nullable=False)
    counter_pb_previous: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    counter_color_current: Mapped[int] = mapped_column(Integer, nullable=False)
    counter_color_previous: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    tenant = relationship("Tenant", back_populates="readings")
    contract = relationship("Contract", back_populates="readings")
    equipment = relationship("Equipment")

