from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    OrigemDocumentoFiscal,
    RegimeTributario,
    StatusDocumentoFiscal,
    TipoDocumentoFiscal,
)
from app.models.base import Base, IDMixin, TimestampMixin


class FiscalConfig(Base, IDMixin, TimestampMixin):
    __tablename__ = "fiscal_configs"
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_fiscal_configs_tenant"),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(180), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(30), nullable=True)
    inscricao_municipal: Mapped[str | None] = mapped_column(String(30), nullable=True)
    regime_tributario: Mapped[RegimeTributario] = mapped_column(Enum(RegimeTributario), default=RegimeTributario.SIMPLES_NACIONAL, nullable=False)
    serie_nfe: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    serie_nfse: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    nfe_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nfse_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    iss_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=2.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="fiscal_config")
    documents = relationship("FiscalDocument", back_populates="config", cascade="all, delete-orphan")


class FiscalDocument(Base, IDMixin, TimestampMixin):
    __tablename__ = "fiscal_documents"
    __table_args__ = (UniqueConstraint("tenant_id", "document_type", "series", "number", name="uq_fiscal_documents_number"),)

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    config_id: Mapped[int] = mapped_column(ForeignKey("fiscal_configs.id"), nullable=False, index=True)
    document_type: Mapped[TipoDocumentoFiscal] = mapped_column(Enum(TipoDocumentoFiscal), nullable=False, index=True)
    origin: Mapped[OrigemDocumentoFiscal] = mapped_column(Enum(OrigemDocumentoFiscal), nullable=False, default=OrigemDocumentoFiscal.MANUAL)
    receivable_id: Mapped[int | None] = mapped_column(ForeignKey("accounts_receivable.id"), nullable=True, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    series: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    access_key: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True, index=True)
    status: Mapped[StatusDocumentoFiscal] = mapped_column(Enum(StatusDocumentoFiscal), default=StatusDocumentoFiscal.RASCUNHO, nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    competence: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    recipient_name: Mapped[str] = mapped_column(String(180), nullable=False)
    recipient_document: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_base: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    tax_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    tax_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    xml_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    authorization_protocol: Mapped[str | None] = mapped_column(String(80), nullable=True)
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="fiscal_documents")
    config = relationship("FiscalConfig", back_populates="documents")
    receivable = relationship("AccountsReceivable")
    contract = relationship("Contract")
    client = relationship("Client")
