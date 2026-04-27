from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import StatusBoleto, StatusConciliacao, StatusRemessa, StatusTitulo
from app.models.base import Base, IDMixin, TimestampMixin


class AccountsReceivable(Base, IDMixin, TimestampMixin):
    __tablename__ = "accounts_receivable"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    competence: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(180), nullable=False)
    original_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    interest_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    penalty_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[StatusTitulo] = mapped_column(Enum(StatusTitulo), default=StatusTitulo.ABERTO, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract = relationship("Contract")
    client = relationship("Client")
    boletos = relationship("Boleto", back_populates="receivable", cascade="all, delete-orphan")


class AccountsPayable(Base, IDMixin, TimestampMixin):
    __tablename__ = "accounts_payable"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    supplier_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    original_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[StatusTitulo] = mapped_column(Enum(StatusTitulo), default=StatusTitulo.ABERTO, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract = relationship("Contract")
    boletos = relationship("Boleto", back_populates="payable", cascade="all, delete-orphan")


class Boleto(Base, IDMixin, TimestampMixin):
    __tablename__ = "boletos"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    receivable_id: Mapped[int | None] = mapped_column(ForeignKey("accounts_receivable.id"), nullable=True, index=True)
    payable_id: Mapped[int | None] = mapped_column(ForeignKey("accounts_payable.id"), nullable=True, index=True)
    bank_code: Mapped[str] = mapped_column(String(10), nullable=False)
    nosso_numero: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pix_qr_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[StatusBoleto] = mapped_column(Enum(StatusBoleto), default=StatusBoleto.GERADO, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    remittance_id: Mapped[int | None] = mapped_column(ForeignKey("remessas.id"), nullable=True, index=True)
    pdf_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    receivable = relationship("AccountsReceivable", back_populates="boletos")
    payable = relationship("AccountsPayable", back_populates="boletos")
    remittance = relationship("Remittance", back_populates="boletos")


class Remittance(Base, IDMixin, TimestampMixin):
    __tablename__ = "remessas"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    bank_code: Mapped[str] = mapped_column(String(10), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_name: Mapped[str] = mapped_column(String(180), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[StatusRemessa] = mapped_column(Enum(StatusRemessa), default=StatusRemessa.CRIADA, nullable=False)
    total_titles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    boletos = relationship("Boleto", back_populates="remittance")


class BankReconciliationEntry(Base, IDMixin, TimestampMixin):
    __tablename__ = "bank_reconciliation_entries"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    statement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(180), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(80), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="extrato")
    status: Mapped[StatusConciliacao] = mapped_column(Enum(StatusConciliacao), default=StatusConciliacao.PENDENTE, nullable=False)
    receivable_id: Mapped[int | None] = mapped_column(ForeignKey("accounts_receivable.id"), nullable=True, index=True)
    payable_id: Mapped[int | None] = mapped_column(ForeignKey("accounts_payable.id"), nullable=True, index=True)
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    receivable = relationship("AccountsReceivable")
    payable = relationship("AccountsPayable")
