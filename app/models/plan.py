from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TipoPlano
from app.models.base import Base, IDMixin, TimestampMixin


class Plan(Base, IDMixin, TimestampMixin):
    __tablename__ = "plans"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[TipoPlano] = mapped_column(Enum(TipoPlano), nullable=False)
    monthly_fee: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_pb: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    price_color: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    franchise_pb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    franchise_color: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_pb: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    extra_color: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant = relationship("Tenant", back_populates="plans")
    contracts = relationship("Contract", back_populates="plan")

