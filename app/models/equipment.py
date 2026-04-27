from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import StatusEquipamento
from app.models.base import Base, IDMixin, TimestampMixin


class Equipment(Base, IDMixin, TimestampMixin):
    __tablename__ = "equipments"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    serial_number: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[StatusEquipamento] = mapped_column(Enum(StatusEquipamento), default=StatusEquipamento.DISPONIVEL, nullable=False)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    last_counter_pb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_counter_color: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tenant = relationship("Tenant", back_populates="equipments")
    client = relationship("Client", back_populates="equipments")
    contracts = relationship("ContractEquipment", back_populates="equipment")

