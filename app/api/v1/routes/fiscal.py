from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import StatusDocumentoFiscal, TipoDocumentoFiscal
from app.models.fiscal import FiscalConfig, FiscalDocument
from app.models.user import User
from app.schemas.fiscal import (
    FiscalBatchIssueRequest,
    FiscalConfigRead,
    FiscalConfigUpdate,
    FiscalDocumentIssueRequest,
    FiscalDocumentRead,
    FiscalDocumentUpdate,
    FiscalSummaryResponse,
)
from app.services.fiscal import (
    authorize_document,
    cancel_document,
    get_or_create_config,
    issue_document,
    issue_documents_from_receivables,
    update_config,
    update_document,
)

router = APIRouter()


@router.get("/configuracao", response_model=FiscalConfigRead)
def get_config(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> FiscalConfig:
    return get_or_create_config(db, current_user.tenant)


@router.put("/configuracao", response_model=FiscalConfigRead)
def put_config(
    payload: FiscalConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FiscalConfig:
    return update_config(db, current_user.tenant, payload)


@router.get("/dashboard", response_model=FiscalSummaryResponse)
def fiscal_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> FiscalSummaryResponse:
    query = db.query(FiscalDocument).filter(FiscalDocument.tenant_id == current_user.tenant_id)
    total_documents = query.count()
    draft_documents = query.filter(FiscalDocument.status == StatusDocumentoFiscal.RASCUNHO).count()
    authorized_documents = query.filter(FiscalDocument.status == StatusDocumentoFiscal.AUTORIZADO).count()
    cancelled_documents = query.filter(FiscalDocument.status == StatusDocumentoFiscal.CANCELADO).count()
    total_amount = query.with_entities(func.coalesce(func.sum(FiscalDocument.amount), 0)).scalar() or 0
    return FiscalSummaryResponse(
        total_documents=total_documents,
        draft_documents=draft_documents,
        authorized_documents=authorized_documents,
        cancelled_documents=cancelled_documents,
        total_amount=total_amount,
    )


@router.get("/documentos", response_model=list[FiscalDocumentRead])
def list_documents(
    document_type: TipoDocumentoFiscal | None = None,
    status_filter: StatusDocumentoFiscal | None = None,
    receivable_id: int | None = None,
    contract_id: int | None = None,
    client_id: int | None = None,
    competence: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FiscalDocument]:
    query = db.query(FiscalDocument).filter(FiscalDocument.tenant_id == current_user.tenant_id)
    if document_type is not None:
        query = query.filter(FiscalDocument.document_type == document_type)
    if status_filter is not None:
        query = query.filter(FiscalDocument.status == status_filter)
    if receivable_id is not None:
        query = query.filter(FiscalDocument.receivable_id == receivable_id)
    if contract_id is not None:
        query = query.filter(FiscalDocument.contract_id == contract_id)
    if client_id is not None:
        query = query.filter(FiscalDocument.client_id == client_id)
    if competence:
        query = query.filter(FiscalDocument.competence == competence)
    return query.order_by(FiscalDocument.id.desc()).offset(skip).limit(limit).all()


@router.post("/documentos", response_model=FiscalDocumentRead)
def create_document(
    payload: FiscalDocumentIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FiscalDocument:
    return issue_document(db, current_user.tenant, payload)


@router.put("/documentos/{document_id}", response_model=FiscalDocumentRead)
def edit_document(
    document_id: int,
    payload: FiscalDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FiscalDocument:
    try:
        return update_document(db, current_user.tenant, document_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/documentos/{document_id}/autorizar", response_model=FiscalDocumentRead)
def authorize_fiscal_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FiscalDocument:
    try:
        return authorize_document(db, current_user.tenant, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/documentos/{document_id}/cancelar", response_model=FiscalDocumentRead)
def cancel_fiscal_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FiscalDocument:
    try:
        return cancel_document(db, current_user.tenant, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/documentos/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    document = (
        db.query(FiscalDocument)
        .filter(FiscalDocument.tenant_id == current_user.tenant_id, FiscalDocument.id == document_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento fiscal nao encontrado")
    db.delete(document)
    db.commit()
    return {"detail": "Documento fiscal removido com sucesso"}


@router.post("/documentos/gerar-recebiveis", response_model=list[FiscalDocumentRead])
def batch_issue_from_receivables(
    payload: FiscalBatchIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FiscalDocument]:
    return issue_documents_from_receivables(db, current_user.tenant, payload)
