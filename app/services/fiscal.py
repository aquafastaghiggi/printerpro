from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.enums import (
    OrigemDocumentoFiscal,
    StatusDocumentoFiscal,
    TipoDocumentoFiscal,
)
from app.models.client import Client
from app.models.contract import Contract
from app.models.finance import AccountsReceivable
from app.models.fiscal import FiscalConfig, FiscalDocument
from app.models.tenant import Tenant
from app.schemas.fiscal import (
    FiscalBatchIssueRequest,
    FiscalConfigUpdate,
    FiscalDocumentIssueRequest,
    FiscalDocumentUpdate,
)


def get_or_create_config(db: Session, tenant: Tenant) -> FiscalConfig:
    config = db.query(FiscalConfig).filter(FiscalConfig.tenant_id == tenant.id).first()
    if config:
        return config

    config = FiscalConfig(
        tenant_id=tenant.id,
        company_name=tenant.name,
        cnpj=tenant.document,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_config(db: Session, tenant: Tenant, payload: FiscalConfigUpdate) -> FiscalConfig:
    config = get_or_create_config(db, tenant)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return config


def _next_number(db: Session, tenant_id: int, document_type: TipoDocumentoFiscal, series: int) -> int:
    max_number = (
        db.query(func.max(FiscalDocument.number))
        .filter(
            FiscalDocument.tenant_id == tenant_id,
            FiscalDocument.document_type == document_type,
            FiscalDocument.series == series,
        )
        .scalar()
    )
    return int(max_number or 0) + 1


def _access_key(tenant_id: int, document_type: TipoDocumentoFiscal, series: int, number: int, issue_date: date) -> str:
    return f"{document_type.value.upper()}{tenant_id:04d}{series:04d}{number:09d}{issue_date:%Y%m%d}"


def _decimal_or_zero(value: Decimal | float | int | None) -> Decimal:
    if value is None:
        return Decimal("0")
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _load_document_targets(db: Session, tenant_id: int, payload: FiscalDocumentIssueRequest) -> tuple[Client | None, Contract | None, AccountsReceivable | None]:
    receivable = None
    contract = None
    client = None

    if payload.receivable_id is not None:
        receivable = (
            db.query(AccountsReceivable)
            .options(selectinload(AccountsReceivable.client), selectinload(AccountsReceivable.contract))
            .filter(AccountsReceivable.tenant_id == tenant_id, AccountsReceivable.id == payload.receivable_id)
            .first()
        )
        if receivable:
            contract = receivable.contract
            client = receivable.client

    if contract is None and payload.contract_id is not None:
        contract = (
            db.query(Contract)
            .options(selectinload(Contract.client))
            .filter(Contract.tenant_id == tenant_id, Contract.id == payload.contract_id)
            .first()
        )
        if contract:
            client = contract.client

    if client is None and payload.client_id is not None:
        client = db.query(Client).filter(Client.tenant_id == tenant_id, Client.id == payload.client_id).first()

    return client, contract, receivable


def issue_document(db: Session, tenant: Tenant, payload: FiscalDocumentIssueRequest) -> FiscalDocument:
    config = get_or_create_config(db, tenant)
    client, contract, receivable = _load_document_targets(db, tenant.id, payload)

    series = payload.series
    if series is None:
        series = config.serie_nfse if payload.document_type == TipoDocumentoFiscal.NFSE else config.serie_nfe

    number = _next_number(db, tenant.id, payload.document_type, series)

    amount = _decimal_or_zero(payload.amount)
    description = payload.description
    recipient_name = payload.recipient_name
    recipient_document = payload.recipient_document
    tax_base = _decimal_or_zero(payload.tax_base) if payload.tax_base is not None else None
    tax_rate = _decimal_or_zero(payload.tax_rate) if payload.tax_rate is not None else None
    tax_amount = _decimal_or_zero(payload.tax_amount) if payload.tax_amount is not None else None

    if receivable is not None:
        amount = _decimal_or_zero(
            receivable.original_amount + receivable.interest_amount + receivable.penalty_amount - receivable.discount_amount - receivable.paid_amount
        )
        description = description or receivable.description
        recipient_name = recipient_name or (client.name if client else None)
        recipient_document = recipient_document or (client.document if client else None)
        tax_base = tax_base if tax_base is not None else amount

    if contract is not None:
        description = description or f"Contrato {contract.number} - {payload.competence}"
        if recipient_name is None and client is not None:
            recipient_name = client.name
        if recipient_document is None and client is not None:
            recipient_document = client.document
        if amount == Decimal("0") and contract.monthly_value is not None:
            amount = _decimal_or_zero(contract.monthly_value)
        tax_base = tax_base if tax_base is not None else amount

    if client is not None and recipient_name is None:
        recipient_name = client.name
    if client is not None and recipient_document is None:
        recipient_document = client.document

    document = FiscalDocument(
        tenant_id=tenant.id,
        config_id=config.id,
        document_type=payload.document_type,
        origin=payload.origin,
        receivable_id=payload.receivable_id,
        contract_id=payload.contract_id,
        client_id=payload.client_id or (client.id if client else None),
        number=number,
        series=series,
        issue_date=payload.issue_date,
        competence=payload.competence,
        recipient_name=recipient_name or tenant.name,
        recipient_document=recipient_document,
        description=description or f"Documento fiscal {payload.document_type.value.upper()} {number}",
        amount=amount,
        tax_base=tax_base,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        status=StatusDocumentoFiscal.AUTORIZADO if payload.authorize else StatusDocumentoFiscal.RASCUNHO,
        notes=payload.notes,
    )
    db.add(document)
    db.flush()
    document.access_key = _access_key(tenant.id, payload.document_type, series, number, payload.issue_date)
    if payload.authorize:
        document.authorization_protocol = f"{payload.document_type.value.upper()}-{tenant.id}-{number:09d}"
        document.authorized_at = datetime.now(timezone.utc)
        document.xml_url = f"/fiscal/documentos/{document.id}.xml"
        document.pdf_url = f"/fiscal/documentos/{document.id}.pdf"
    db.commit()
    db.refresh(document)
    return document


def update_document(db: Session, tenant: Tenant, document_id: int, payload: FiscalDocumentUpdate) -> FiscalDocument:
    document = (
        db.query(FiscalDocument)
        .filter(FiscalDocument.tenant_id == tenant.id, FiscalDocument.id == document_id)
        .first()
    )
    if not document:
        raise ValueError("Documento fiscal nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)
    return document


def authorize_document(db: Session, tenant: Tenant, document_id: int) -> FiscalDocument:
    document = (
        db.query(FiscalDocument)
        .filter(FiscalDocument.tenant_id == tenant.id, FiscalDocument.id == document_id)
        .first()
    )
    if not document:
        raise ValueError("Documento fiscal nao encontrado")

    document.status = StatusDocumentoFiscal.AUTORIZADO
    document.authorization_protocol = document.authorization_protocol or f"{document.document_type.value.upper()}-{tenant.id}-{document.number:09d}"
    document.authorized_at = datetime.now(timezone.utc)
    document.xml_url = document.xml_url or f"/fiscal/documentos/{document.id}.xml"
    document.pdf_url = document.pdf_url or f"/fiscal/documentos/{document.id}.pdf"
    db.commit()
    db.refresh(document)
    return document


def cancel_document(db: Session, tenant: Tenant, document_id: int) -> FiscalDocument:
    document = (
        db.query(FiscalDocument)
        .filter(FiscalDocument.tenant_id == tenant.id, FiscalDocument.id == document_id)
        .first()
    )
    if not document:
        raise ValueError("Documento fiscal nao encontrado")

    document.status = StatusDocumentoFiscal.CANCELADO
    document.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(document)
    return document


def issue_documents_from_receivables(db: Session, tenant: Tenant, payload: FiscalBatchIssueRequest) -> list[FiscalDocument]:
    if payload.receivable_ids:
        receivables = (
            db.query(AccountsReceivable)
            .filter(AccountsReceivable.tenant_id == tenant.id, AccountsReceivable.id.in_(payload.receivable_ids))
            .order_by(AccountsReceivable.id.asc())
            .all()
        )
    else:
        receivables = (
            db.query(AccountsReceivable)
            .filter(AccountsReceivable.tenant_id == tenant.id, AccountsReceivable.competence == payload.competence)
            .order_by(AccountsReceivable.id.asc())
            .all()
        )

    documents: list[FiscalDocument] = []
    for receivable in receivables:
        documents.append(
            issue_document(
                db,
                tenant,
                FiscalDocumentIssueRequest(
                    document_type=payload.document_type,
                    origin=OrigemDocumentoFiscal.RECEIVABLE,
                    receivable_id=receivable.id,
                    issue_date=payload.issue_date,
                    competence=payload.competence,
                    authorize=payload.authorize,
                    series=payload.series,
                    amount=_decimal_or_zero(receivable.original_amount),
                    description=receivable.description,
                    recipient_name=receivable.client.name if receivable.client else None,
                    recipient_document=receivable.client.document if receivable.client else None,
                ),
            )
        )
    return documents
