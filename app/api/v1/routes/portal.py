from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_portal_client
from app.core.enums import StatusTitulo, FonteLeitura, StatusChamado
from app.core.security import create_access_token, decode_access_token
from app.models.client import Client
from app.models.contract import Contract
from app.models.equipment import Equipment
from app.models.finance import AccountsReceivable, Boleto
from app.models.portal import PortalTicket
from app.models.reading import Reading
from app.models.tenant import Tenant
from app.schemas.client import ClientRead
from app.schemas.contract import ContractRead
from app.schemas.equipment import EquipmentRead
from app.schemas.finance import BoletoRead
from app.schemas.portal import (
    PortalLoginRequest,
    PortalReadingCreate,
    PortalReportResponse,
    PortalSummaryResponse,
    PortalTicketCreate,
    PortalTicketRead,
    PortalTokenResponse,
)
from app.schemas.reading import ReadingRead

router = APIRouter()


def _portal_token(client: Client) -> str:
    return create_access_token(
        data={
            "sub": str(client.id),
            "tenant_id": str(client.tenant_id),
            "client_id": str(client.id),
            "role": "portal",
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


@router.post("/login", response_model=PortalTokenResponse)
def login(payload: PortalLoginRequest, db: Session = Depends(get_db)) -> PortalTokenResponse:
    tenant = (
        db.query(Tenant)
        .filter(or_(Tenant.document == payload.tenant_key, Tenant.name == payload.tenant_key))
        .first()
    )
    if not tenant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant nao encontrado")

    client = (
        db.query(Client)
        .filter(Client.tenant_id == tenant.id, Client.document == payload.client_document)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cliente nao encontrado")

    return PortalTokenResponse(
        access_token=_portal_token(client),
        client_id=client.id,
        tenant_id=tenant.id,
        client_name=client.name,
    )


@router.get("/me", response_model=ClientRead)
def me(current_client: Client = Depends(get_current_portal_client)) -> Client:
    return current_client


@router.get("/dashboard", response_model=PortalSummaryResponse)
def dashboard(db: Session = Depends(get_db), current_client: Client = Depends(get_current_portal_client)) -> PortalSummaryResponse:
    contract_ids = [item.id for item in current_client.contracts]
    readings_query = db.query(Reading).filter(Reading.tenant_id == current_client.tenant_id, Reading.contract_id.in_(contract_ids))
    boletos_query = (
        db.query(Boleto)
        .join(AccountsReceivable, Boleto.receivable_id == AccountsReceivable.id)
        .filter(Boleto.tenant_id == current_client.tenant_id, AccountsReceivable.client_id == current_client.id)
    )
    last_reading = readings_query.order_by(Reading.reference_date.desc(), Reading.id.desc()).first()
    return PortalSummaryResponse(
        contracts=len(contract_ids),
        equipments=len(current_client.equipments),
        readings=readings_query.count(),
        boletos_open=boletos_query.filter(Boleto.status != StatusTitulo.PAGO).count(),
        tickets_open=db.query(PortalTicket).filter(
            PortalTicket.tenant_id == current_client.tenant_id,
            PortalTicket.client_id == current_client.id,
            PortalTicket.status == StatusChamado.ABERTO,
        ).count(),
        last_reading_at=getattr(last_reading, "created_at", None),
    )


@router.get("/contratos", response_model=list[ContractRead])
def list_contracts(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> list[Contract]:
    return (
        db.query(Contract)
        .options(selectinload(Contract.equipments))
        .filter(Contract.tenant_id == current_client.tenant_id, Contract.client_id == current_client.id)
        .order_by(Contract.id.desc())
        .all()
    )


@router.get("/equipamentos", response_model=list[EquipmentRead])
def list_equipment(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> list[Equipment]:
    return (
        db.query(Equipment)
        .filter(Equipment.tenant_id == current_client.tenant_id, Equipment.client_id == current_client.id)
        .order_by(Equipment.id.desc())
        .all()
    )


@router.get("/leituras", response_model=list[ReadingRead])
def list_readings(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> list[Reading]:
    contract_ids = [item.id for item in current_client.contracts]
    return (
        db.query(Reading)
        .filter(Reading.tenant_id == current_client.tenant_id, Reading.contract_id.in_(contract_ids))
        .order_by(Reading.reference_date.desc(), Reading.id.desc())
        .all()
    )


@router.post("/leituras", response_model=ReadingRead)
def create_reading(
    payload: PortalReadingCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> Reading:
    contract = (
        db.query(Contract)
        .filter(
            Contract.tenant_id == current_client.tenant_id,
            Contract.id == payload.contract_id,
            Contract.client_id == current_client.id,
        )
        .first()
    )
    equipment = (
        db.query(Equipment)
        .filter(
            Equipment.tenant_id == current_client.tenant_id,
            Equipment.id == payload.equipment_id,
            Equipment.client_id == current_client.id,
        )
        .first()
    )
    if not contract or not equipment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contrato ou equipamento invalido")

    reading = Reading(
        tenant_id=current_client.tenant_id,
        contract_id=payload.contract_id,
        equipment_id=payload.equipment_id,
        reference_date=payload.reference_date,
        source=FonteLeitura.PORTAL,
        counter_pb_current=payload.counter_pb_current,
        counter_pb_previous=payload.counter_pb_previous,
        counter_color_current=payload.counter_color_current,
        counter_color_previous=payload.counter_color_previous,
        validated=False,
        notes=payload.notes,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/boletos", response_model=list[BoletoRead])
def list_boletos(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> list[Boleto]:
    return (
        db.query(Boleto)
        .join(AccountsReceivable, Boleto.receivable_id == AccountsReceivable.id)
        .filter(Boleto.tenant_id == current_client.tenant_id, AccountsReceivable.client_id == current_client.id)
        .order_by(Boleto.due_date.desc(), Boleto.id.desc())
        .all()
    )


@router.get("/boletos/{boleto_id}/download")
def download_boleto(
    boleto_id: int,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> dict[str, str | None]:
    boleto = (
        db.query(Boleto)
        .join(AccountsReceivable, Boleto.receivable_id == AccountsReceivable.id)
        .filter(
            Boleto.tenant_id == current_client.tenant_id,
            Boleto.id == boleto_id,
            AccountsReceivable.client_id == current_client.id,
        )
        .first()
    )
    if not boleto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boleto nao encontrado")
    return {"download_url": boleto.pdf_url, "barcode": boleto.barcode}


@router.get("/relatorio", response_model=PortalReportResponse)
def report(db: Session = Depends(get_db), current_client: Client = Depends(get_current_portal_client)) -> PortalReportResponse:
    contract_ids = [item.id for item in current_client.contracts]
    boletos_query = (
        db.query(Boleto)
        .join(AccountsReceivable, Boleto.receivable_id == AccountsReceivable.id)
        .filter(Boleto.tenant_id == current_client.tenant_id, AccountsReceivable.client_id == current_client.id)
    )
    total_due = (
        db.query(func.coalesce(func.sum(AccountsReceivable.original_amount - AccountsReceivable.paid_amount), 0))
        .filter(AccountsReceivable.tenant_id == current_client.tenant_id, AccountsReceivable.client_id == current_client.id)
        .scalar()
        or 0
    )
    return PortalReportResponse(
        client_name=current_client.name,
        contracts=len(contract_ids),
        readings=db.query(Reading).filter(Reading.tenant_id == current_client.tenant_id, Reading.contract_id.in_(contract_ids)).count(),
        tickets_open=db.query(PortalTicket).filter(
            PortalTicket.tenant_id == current_client.tenant_id,
            PortalTicket.client_id == current_client.id,
            PortalTicket.status == StatusChamado.ABERTO,
        ).count(),
        boletos_open=boletos_query.filter(Boleto.status != StatusTitulo.PAGO).count(),
        total_due=total_due,
    )


@router.get("/chamados", response_model=list[PortalTicketRead])
def list_tickets(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> list[PortalTicket]:
    return (
        db.query(PortalTicket)
        .filter(PortalTicket.tenant_id == current_client.tenant_id, PortalTicket.client_id == current_client.id)
        .order_by(PortalTicket.id.desc())
        .all()
    )


@router.post("/chamados", response_model=PortalTicketRead)
def create_ticket(
    payload: PortalTicketCreate,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_portal_client),
) -> PortalTicket:
    if payload.contract_id is not None:
        contract = (
            db.query(Contract)
            .filter(
                Contract.tenant_id == current_client.tenant_id,
                Contract.client_id == current_client.id,
                Contract.id == payload.contract_id,
            )
            .first()
        )
        if not contract:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contrato invalido")
    if payload.equipment_id is not None:
        equipment = (
            db.query(Equipment)
            .filter(
                Equipment.tenant_id == current_client.tenant_id,
                Equipment.client_id == current_client.id,
                Equipment.id == payload.equipment_id,
            )
            .first()
        )
        if not equipment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Equipamento invalido")

    ticket = PortalTicket(
        tenant_id=current_client.tenant_id,
        client_id=current_client.id,
        contract_id=payload.contract_id,
        equipment_id=payload.equipment_id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
        status=StatusChamado.ABERTO,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
