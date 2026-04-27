from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import StatusEquipamento
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate

router = APIRouter()


@router.get("", response_model=list[EquipmentRead])
def list_equipment(
    q: str | None = None,
    status_filter: StatusEquipamento | None = None,
    client_id: int | None = None,
    serial_number: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Equipment]:
    query = db.query(Equipment).filter(Equipment.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Equipment.brand.ilike(term), Equipment.model.ilike(term), Equipment.kind.ilike(term)))
    if status_filter is not None:
        query = query.filter(Equipment.status == status_filter)
    if client_id is not None:
        query = query.filter(Equipment.client_id == client_id)
    if serial_number:
        query = query.filter(Equipment.serial_number.ilike(f"%{serial_number}%"))
    return query.order_by(Equipment.id.desc()).offset(skip).limit(limit).all()


@router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if not equipment or equipment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    return equipment


@router.post("", response_model=EquipmentRead)
def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Equipment:
    equipment = Equipment(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentRead)
def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if not equipment or equipment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    equipment = db.get(Equipment, equipment_id)
    if not equipment or equipment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipamento nao encontrado")
    db.delete(equipment)
    db.commit()
    return {"detail": "Equipamento removido com sucesso"}

