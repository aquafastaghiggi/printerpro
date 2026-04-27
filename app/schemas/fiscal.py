from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import (
    OrigemDocumentoFiscal,
    RegimeTributario,
    StatusDocumentoFiscal,
    TipoDocumentoFiscal,
)
from app.schemas.common import IDResponse, ORMModel


class FiscalConfigCreate(BaseModel):
    company_name: str
    cnpj: str | None = None
    inscricao_estadual: str | None = None
    inscricao_municipal: str | None = None
    regime_tributario: RegimeTributario = RegimeTributario.SIMPLES_NACIONAL
    serie_nfe: int = 1
    serie_nfse: int = 1
    nfe_enabled: bool = True
    nfse_enabled: bool = True
    iss_rate: Decimal = Decimal("2.00")
    notes: str | None = None


class FiscalConfigUpdate(BaseModel):
    company_name: str | None = None
    cnpj: str | None = None
    inscricao_estadual: str | None = None
    inscricao_municipal: str | None = None
    regime_tributario: RegimeTributario | None = None
    serie_nfe: int | None = None
    serie_nfse: int | None = None
    nfe_enabled: bool | None = None
    nfse_enabled: bool | None = None
    iss_rate: Decimal | None = None
    notes: str | None = None


class FiscalConfigRead(IDResponse, ORMModel):
    tenant_id: int
    company_name: str
    cnpj: str | None = None
    inscricao_estadual: str | None = None
    inscricao_municipal: str | None = None
    regime_tributario: RegimeTributario
    serie_nfe: int
    serie_nfse: int
    nfe_enabled: bool
    nfse_enabled: bool
    iss_rate: Decimal
    notes: str | None = None


class FiscalDocumentIssueRequest(BaseModel):
    document_type: TipoDocumentoFiscal
    origin: OrigemDocumentoFiscal = OrigemDocumentoFiscal.MANUAL
    receivable_id: int | None = None
    contract_id: int | None = None
    client_id: int | None = None
    series: int | None = None
    issue_date: date
    competence: str
    recipient_name: str | None = None
    recipient_document: str | None = None
    description: str | None = None
    amount: Decimal | None = None
    tax_base: Decimal | None = None
    tax_rate: Decimal | None = None
    tax_amount: Decimal | None = None
    authorize: bool = True
    notes: str | None = None


class FiscalDocumentUpdate(BaseModel):
    document_type: TipoDocumentoFiscal | None = None
    origin: OrigemDocumentoFiscal | None = None
    series: int | None = None
    issue_date: date | None = None
    competence: str | None = None
    recipient_name: str | None = None
    recipient_document: str | None = None
    description: str | None = None
    amount: Decimal | None = None
    tax_base: Decimal | None = None
    tax_rate: Decimal | None = None
    tax_amount: Decimal | None = None
    notes: str | None = None


class FiscalDocumentRead(IDResponse, ORMModel):
    tenant_id: int
    config_id: int
    document_type: TipoDocumentoFiscal
    origin: OrigemDocumentoFiscal
    receivable_id: int | None = None
    contract_id: int | None = None
    client_id: int | None = None
    number: int
    series: int
    access_key: str | None = None
    status: StatusDocumentoFiscal
    issue_date: date
    competence: str
    recipient_name: str
    recipient_document: str | None = None
    description: str
    amount: Decimal
    tax_base: Decimal | None = None
    tax_rate: Decimal | None = None
    tax_amount: Decimal | None = None
    xml_url: str | None = None
    pdf_url: str | None = None
    authorization_protocol: str | None = None
    authorized_at: datetime | None = None
    cancelled_at: datetime | None = None
    notes: str | None = None


class FiscalSummaryResponse(BaseModel):
    total_documents: int
    draft_documents: int
    authorized_documents: int
    cancelled_documents: int
    total_amount: Decimal


class FiscalBatchIssueRequest(BaseModel):
    document_type: TipoDocumentoFiscal = TipoDocumentoFiscal.NFSE
    receivable_ids: list[int] = Field(default_factory=list)
    authorize: bool = True
    issue_date: date
    competence: str
    series: int | None = None
