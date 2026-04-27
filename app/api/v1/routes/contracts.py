from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import StatusContrato
from app.models.contract import Contract, ContractEquipment
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractRead, ContractUpdate

router = APIRouter()


def _sync_contract_equipment(contract: Contract, equipment_ids: list[int], db: Session, tenant_id: int) -> None:
    if equipment_ids is None:
        return

    if equipment_ids:
        equipments = (
            db.query(Equipment)
            .filter(Equipment.tenant_id == tenant_id, Equipment.id.in_(equipment_ids))
            .all()
        )
        found_ids = {equipment.id for equipment in equipments}
        missing = sorted(set(equipment_ids) - found_ids)
        if missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Equipamentos invalidos: {missing}")

    contract.equipments.clear()
    for equipment_id in equipment_ids:
        contract.equipments.append(ContractEquipment(equipment_id=equipment_id))


@router.get("", response_model=list[ContractRead])
def list_contracts(
    q: str | None = None,
    client_id: int | None = None,
    plan_id: int | None = None,
    status_filter: StatusContrato | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Contract]:
    query = db.query(Contract).options(selectinload(Contract.equipments)).filter(Contract.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Contract.number.ilike(term), Contract.notes.ilike(term)))
    if client_id is not None:
        query = query.filter(Contract.client_id == client_id)
    if plan_id is not None:
        query = query.filter(Contract.plan_id == plan_id)
    if status_filter is not None:
        query = query.filter(Contract.status == status_filter)
    return query.order_by(Contract.id.desc()).offset(skip).limit(limit).all()


@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    contract = db.query(Contract).options(selectinload(Contract.equipments)).filter(
        Contract.id == contract_id,
        Contract.tenant_id == current_user.tenant_id,
    ).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    return contract


@router.post("", response_model=ContractRead)
def create_contract(
    payload: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    contract_data = payload.model_dump(exclude={"equipment_ids"})
    contract = Contract(tenant_id=current_user.tenant_id, **contract_data)
    db.add(contract)
    db.flush()
    _sync_contract_equipment(contract, payload.equipment_ids, db, current_user.tenant_id)
    db.commit()
    db.refresh(contract)
    return contract


@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    contract = db.query(Contract).options(selectinload(Contract.equipments)).filter(
        Contract.id == contract_id,
        Contract.tenant_id == current_user.tenant_id,
    ).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")

    data = payload.model_dump(exclude_unset=True, exclude={"equipment_ids"})
    for field, value in data.items():
        setattr(contract, field, value)

    if payload.equipment_ids is not None:
        _sync_contract_equipment(contract, payload.equipment_ids, db, current_user.tenant_id)

    db.commit()
    db.refresh(contract)
    return contract


@router.delete("/{contract_id}")
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    contract = db.get(Contract, contract_id)
    if not contract or contract.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")
    db.delete(contract)
    db.commit()
    return {"detail": "Contrato removido com sucesso"}


@router.post("/{contract_id}/encerrar", response_model=ContractRead)
def close_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    contract = db.query(Contract).options(selectinload(Contract.equipments)).filter(
        Contract.id == contract_id,
        Contract.tenant_id == current_user.tenant_id,
    ).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")

    contract.status = StatusContrato.ENCERRADO
    contract.end_date = date.today()
    db.commit()
    db.refresh(contract)
    return contract


@router.post("/{contract_id}/duplicar", response_model=ContractRead)
def duplicate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    contract = db.query(Contract).options(selectinload(Contract.equipments)).filter(
        Contract.id == contract_id,
        Contract.tenant_id == current_user.tenant_id,
    ).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato nao encontrado")

    base_number = f"{contract.number}-COPY"
    next_number = base_number
    counter = 1
    while (
        db.query(Contract)
        .filter(Contract.tenant_id == current_user.tenant_id, Contract.number == next_number)
        .first()
    ):
        counter += 1
        next_number = f"{base_number}-{counter}"

    cloned = Contract(
        tenant_id=current_user.tenant_id,
        client_id=contract.client_id,
        plan_id=contract.plan_id,
        number=next_number,
        start_date=date.today(),
        end_date=None,
        status=StatusContrato.RASCUNHO,
        billing_day=contract.billing_day,
        monthly_value=contract.monthly_value,
        franchise_pb=contract.franchise_pb,
        franchise_color=contract.franchise_color,
        price_excess_pb=contract.price_excess_pb,
        price_excess_color=contract.price_excess_color,
        notes=contract.notes,
    )
    db.add(cloned)
    db.flush()
    _sync_contract_equipment(cloned, [item.equipment_id for item in contract.equipments], db, current_user.tenant_id)
    db.commit()
    db.refresh(cloned)
    return cloned
