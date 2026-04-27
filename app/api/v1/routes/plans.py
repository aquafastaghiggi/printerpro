from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import TipoPlano
from app.models.plan import Plan
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate

router = APIRouter()


@router.get("", response_model=list[PlanRead])
def list_plans(
    q: str | None = None,
    type_filter: TipoPlano | None = None,
    is_active: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Plan]:
    query = db.query(Plan).filter(Plan.tenant_id == current_user.tenant_id)
    if q:
        query = query.filter(Plan.name.ilike(f"%{q}%"))
    if type_filter is not None:
        query = query.filter(Plan.type == type_filter)
    if is_active is not None:
        query = query.filter(Plan.is_active == is_active)
    return query.order_by(Plan.id.desc()).offset(skip).limit(limit).all()


@router.get("/{plan_id}", response_model=PlanRead)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Plan:
    plan = db.get(Plan, plan_id)
    if not plan or plan.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano nao encontrado")
    return plan


@router.post("", response_model=PlanRead)
def create_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Plan:
    plan = Plan(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PlanRead)
def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Plan:
    plan = db.get(Plan, plan_id)
    if not plan or plan.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    plan = db.get(Plan, plan_id)
    if not plan or plan.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano nao encontrado")
    db.delete(plan)
    db.commit()
    return {"detail": "Plano removido com sucesso"}

