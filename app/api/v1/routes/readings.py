from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import FonteLeitura
from app.models.contract import Contract
from app.models.equipment import Equipment
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate, ReadingRead, ReadingUpdate

router = APIRouter()


def _validate_tenant_relationships(db: Session, tenant_id: int, contract_id: int, equipment_id: int) -> None:
    contract = db.get(Contract, contract_id)
    equipment = db.get(Equipment, equipment_id)
    if not contract or not equipment or contract.tenant_id != tenant_id or equipment.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contrato ou equipamento invalido para o tenant")


@router.get("", response_model=list[ReadingRead])
def list_readings(
    contract_id: int | None = None,
    equipment_id: int | None = None,
    source: FonteLeitura | None = None,
    validated: bool | None = None,
    reference_date_from: date | None = None,
    reference_date_to: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Reading]:
    query = db.query(Reading).filter(Reading.tenant_id == current_user.tenant_id)
    if contract_id is not None:
        query = query.filter(Reading.contract_id == contract_id)
    if equipment_id is not None:
        query = query.filter(Reading.equipment_id == equipment_id)
    if source is not None:
        query = query.filter(Reading.source == source)
    if validated is not None:
        query = query.filter(Reading.validated == validated)
    if reference_date_from is not None:
        query = query.filter(Reading.reference_date >= reference_date_from)
    if reference_date_to is not None:
        query = query.filter(Reading.reference_date <= reference_date_to)
    return query.order_by(Reading.reference_date.desc(), Reading.id.desc()).offset(skip).limit(limit).all()


@router.get("/{reading_id}", response_model=ReadingRead)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Reading:
    reading = db.get(Reading, reading_id)
    if not reading or reading.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leitura nao encontrada")
    return reading


@router.post("", response_model=ReadingRead)
def create_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Reading:
    _validate_tenant_relationships(db, current_user.tenant_id, payload.contract_id, payload.equipment_id)
    reading = Reading(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.put("/{reading_id}", response_model=ReadingRead)
def update_reading(
    reading_id: int,
    payload: ReadingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Reading:
    reading = db.get(Reading, reading_id)
    if not reading or reading.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leitura nao encontrada")

    data = payload.model_dump(exclude_unset=True)
    if "contract_id" in data or "equipment_id" in data:
        contract_id = data.get("contract_id", reading.contract_id)
        equipment_id = data.get("equipment_id", reading.equipment_id)
        _validate_tenant_relationships(db, current_user.tenant_id, contract_id, equipment_id)

    for field, value in data.items():
        setattr(reading, field, value)

    db.commit()
    db.refresh(reading)
    return reading


@router.delete("/{reading_id}")
def delete_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    reading = db.get(Reading, reading_id)
    if not reading or reading.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leitura nao encontrada")
    db.delete(reading)
    db.commit()
    return {"detail": "Leitura removida com sucesso"}

