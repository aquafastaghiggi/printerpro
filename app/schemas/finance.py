from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import StatusBoleto, StatusConciliacao, StatusTitulo
from app.schemas.common import IDResponse, ORMModel


class AccountsReceivableCreate(BaseModel):
    contract_id: int | None = None
    client_id: int | None = None
    issue_date: date
    due_date: date
    competence: str
    description: str
    original_amount: Decimal
    notes: str | None = None


class AccountsReceivableUpdate(BaseModel):
    contract_id: int | None = None
    client_id: int | None = None
    issue_date: date | None = None
    due_date: date | None = None
    competence: str | None = None
    description: str | None = None
    original_amount: Decimal | None = None
    paid_amount: Decimal | None = None
    interest_amount: Decimal | None = None
    penalty_amount: Decimal | None = None
    discount_amount: Decimal | None = None
    status: StatusTitulo | None = None
    notes: str | None = None


class AccountsReceivableRead(IDResponse, ORMModel):
    tenant_id: int
    contract_id: int | None = None
    client_id: int | None = None
    issue_date: date
    due_date: date
    competence: str
    description: str
    original_amount: Decimal
    paid_amount: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    discount_amount: Decimal
    status: StatusTitulo
    notes: str | None = None


class SettlementRequest(BaseModel):
    paid_amount: Decimal | None = None
    payment_date: date | None = None
    notes: str | None = None


class AccountsPayableCreate(BaseModel):
    contract_id: int | None = None
    issue_date: date
    due_date: date
    description: str
    category: str
    supplier_name: str | None = None
    original_amount: Decimal
    notes: str | None = None


class AccountsPayableUpdate(BaseModel):
    contract_id: int | None = None
    issue_date: date | None = None
    due_date: date | None = None
    description: str | None = None
    category: str | None = None
    supplier_name: str | None = None
    original_amount: Decimal | None = None
    paid_amount: Decimal | None = None
    status: StatusTitulo | None = None
    notes: str | None = None


class AccountsPayableRead(IDResponse, ORMModel):
    tenant_id: int
    contract_id: int | None = None
    issue_date: date
    due_date: date
    description: str
    category: str
    supplier_name: str | None = None
    original_amount: Decimal
    paid_amount: Decimal
    status: StatusTitulo
    notes: str | None = None


class BoletoCreate(BaseModel):
    receivable_id: int | None = None
    payable_id: int | None = None
    bank_code: str
    due_date: date
    amount: Decimal


class BoletoUpdate(BaseModel):
    bank_code: str | None = None
    due_date: date | None = None
    amount: Decimal | None = None
    status: StatusBoleto | None = None
    notes: str | None = None


class BoletoRead(IDResponse, ORMModel):
    tenant_id: int
    receivable_id: int | None = None
    payable_id: int | None = None
    bank_code: str
    nosso_numero: str
    barcode: str
    pix_qr_code: str | None = None
    due_date: date
    amount: Decimal
    status: StatusBoleto
    issued_at: datetime
    sent_at: datetime | None = None
    remittance_id: int | None = None
    pdf_url: str | None = None
    notes: str | None = None


class RemittanceCreate(BaseModel):
    bank_code: str
    file_type: str = "cnab240"
    file_name: str
    boleto_ids: list[int] = Field(default_factory=list)


class RemittanceRead(IDResponse, ORMModel):
    tenant_id: int
    bank_code: str
    file_type: str
    file_name: str
    file_url: str | None = None
    generated_at: datetime
    sent_at: datetime | None = None
    status: str
    total_titles: int
    total_amount: Decimal


class BankStatementEntryCreate(BaseModel):
    statement_date: date
    description: str
    reference: str | None = None
    amount: Decimal
    source: str = "extrato"
    notes: str | None = None


class BankStatementImportRequest(BaseModel):
    entries: list[BankStatementEntryCreate] = Field(default_factory=list)
    auto_match: bool = True


class BankStatementEntryRead(IDResponse, ORMModel):
    tenant_id: int
    statement_date: date
    description: str
    reference: str | None = None
    amount: Decimal
    source: str
    status: StatusConciliacao
    receivable_id: int | None = None
    payable_id: int | None = None
    matched_at: datetime | None = None
    notes: str | None = None


class FinanceSummaryResponse(BaseModel):
    receivable_open_total: Decimal
    receivable_overdue_total: Decimal
    payable_open_total: Decimal
    payable_overdue_total: Decimal
    boletos_open: int
    boletos_paid: int
    receivables: int
    payables: int


class AgingBucketRead(BaseModel):
    label: str
    count: int
    total: Decimal


class AgingResponse(BaseModel):
    as_of: date
    receivable_buckets: list[AgingBucketRead] = Field(default_factory=list)
    payable_buckets: list[AgingBucketRead] = Field(default_factory=list)


class BillingGenerationRequest(BaseModel):
    competence: str
    bank_code: str = "001"
    issue_date: date
    due_date: date
    description_prefix: str = "Faturamento"
    generate_boleto: bool = True


class BillingGenerationItem(BaseModel):
    contract_id: int
    receivable_id: int
    boleto_id: int | None = None
    amount: Decimal
    description: str


class BillingGenerationResponse(BaseModel):
    competence: str
    total_amount: Decimal
    items: list[BillingGenerationItem] = Field(default_factory=list)
