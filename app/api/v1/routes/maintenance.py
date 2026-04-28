from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceDispatchResponse,
    MaintenanceSyncResponse,
    MaintenanceTaskCreate,
    MaintenanceTaskRead,
    MaintenanceTaskUpdate,
)
from app.services.maintenance import MaintenanceService

router = APIRouter()


@router.get("/fila", response_model=list[MaintenanceTaskRead])
def list_queue(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list:
    return MaintenanceService(db).list_tasks(current_user.tenant_id)


@router.post("/fila", response_model=MaintenanceTaskRead)
def create_task(
    payload: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MaintenanceTaskRead:
    task = MaintenanceService(db).create_task(current_user.tenant_id, payload)
    db.commit()
    db.refresh(task)
    return task


@router.post("/fila/sincronizar", response_model=MaintenanceSyncResponse)
def sync_queue(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MaintenanceSyncResponse:
    service = MaintenanceService(db)
    created, updated = service.sync_from_equipment(current_user.tenant_id)
    db.commit()
    return MaintenanceSyncResponse(
        created=created,
        updated=updated,
        total=created + updated,
        generated_at=datetime.now(timezone.utc),
    )


@router.patch("/fila/{task_id}", response_model=MaintenanceTaskRead)
def update_task(
    task_id: int,
    payload: MaintenanceTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MaintenanceTaskRead:
    task = MaintenanceService(db).update_task(task_id, current_user.tenant_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa nao encontrada")
    db.commit()
    db.refresh(task)
    return task


@router.post("/fila/{task_id}/iniciar", response_model=MaintenanceTaskRead)
def start_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MaintenanceTaskRead:
    task = MaintenanceService(db).start_task(task_id, current_user.tenant_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa nao encontrada")
    db.commit()
    db.refresh(task)
    return task


@router.post("/fila/{task_id}/concluir", response_model=MaintenanceTaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MaintenanceTaskRead:
    task = MaintenanceService(db).complete_task(task_id, current_user.tenant_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa nao encontrada")
    db.commit()
    db.refresh(task)
    return task


@router.post("/fila/{task_id}/enviar", response_model=MaintenanceDispatchResponse)
def dispatch_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MaintenanceDispatchResponse:
    service = MaintenanceService(db)
    task, email_sent, whatsapp_sent, email_recipient, whatsapp_recipient = service.dispatch_task(
        task_id,
        current_user.tenant_id,
        current_user.email,
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa nao encontrada")
    db.commit()
    return MaintenanceDispatchResponse(
        task_id=task.id,
        email_sent=email_sent,
        whatsapp_sent=whatsapp_sent,
        email_recipient=email_recipient,
        whatsapp_recipient=whatsapp_recipient,
        subject=f"Manutencao preventiva - {task.title}",
        generated_at=datetime.now(timezone.utc),
    )
