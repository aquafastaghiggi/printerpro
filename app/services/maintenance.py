from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import PrioridadeChamado, StatusEquipamento, StatusManutencao
from app.models.equipment import Equipment
from app.models.maintenance import MaintenanceTask
from app.schemas.maintenance import MaintenanceTaskCreate, MaintenanceTaskUpdate
from app.services.alert_delivery import AlertDeliveryService


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db

    def list_tasks(self, tenant_id: int) -> list[MaintenanceTask]:
        return (
            self.db.query(MaintenanceTask)
            .filter(MaintenanceTask.tenant_id == tenant_id)
            .order_by(MaintenanceTask.status.asc(), MaintenanceTask.due_date.asc(), MaintenanceTask.id.desc())
            .all()
        )

    def create_task(self, tenant_id: int, payload: MaintenanceTaskCreate) -> MaintenanceTask:
        task = MaintenanceTask(tenant_id=tenant_id, **payload.model_dump())
        self.db.add(task)
        self.db.flush()
        return task

    def sync_from_equipment(self, tenant_id: int) -> tuple[int, int]:
        created = 0
        updated = 0
        today = date.today()
        equipments = (
            self.db.query(Equipment)
            .filter(Equipment.tenant_id == tenant_id, Equipment.status == StatusEquipamento.MANUTENCAO)
            .order_by(Equipment.id.desc())
            .all()
        )

        for equipment in equipments:
            source_key = f"equipment:{equipment.id}:maintenance"
            task = (
                self.db.query(MaintenanceTask)
                .filter(MaintenanceTask.tenant_id == tenant_id, MaintenanceTask.source_key == source_key)
                .first()
            )
            title = f"Manutencao preventiva - {equipment.brand} {equipment.model}"
            description = (
                f"Equipamento {equipment.serial_number} em manutencao. "
                "Verificar fila de atendimento, pecas e devolutiva ao cliente."
            )
            if task:
                task.title = title
                task.description = description
                task.priority = PrioridadeChamado.ALTA
                task.status = StatusManutencao.PENDENTE
                task.scheduled_for = task.scheduled_for or today
                task.due_date = today + timedelta(days=2)
                task.equipment_id = equipment.id
                task.client_id = equipment.client_id
                updated += 1
            else:
                task = MaintenanceTask(
                    tenant_id=tenant_id,
                    equipment_id=equipment.id,
                    client_id=equipment.client_id,
                    source_type="equipment_maintenance",
                    source_key=source_key,
                    title=title,
                    description=description,
                    priority=PrioridadeChamado.ALTA,
                    status=StatusManutencao.PENDENTE,
                    scheduled_for=today,
                    due_date=today + timedelta(days=2),
                )
                self.db.add(task)
                created += 1
        return created, updated

    def update_task(self, task_id: int, tenant_id: int, payload: MaintenanceTaskUpdate) -> MaintenanceTask | None:
        task = (
            self.db.query(MaintenanceTask)
            .filter(MaintenanceTask.id == task_id, MaintenanceTask.tenant_id == tenant_id)
            .first()
        )
        if not task:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        if task.status == StatusManutencao.EM_EXECUCAO and task.started_at is None:
            task.started_at = _now()
        if task.status == StatusManutencao.CONCLUIDA and task.completed_at is None:
            task.completed_at = _now()
        return task

    def start_task(self, task_id: int, tenant_id: int) -> MaintenanceTask | None:
        task = self.update_task(task_id, tenant_id, MaintenanceTaskUpdate(status=StatusManutencao.EM_EXECUCAO))
        return task

    def complete_task(self, task_id: int, tenant_id: int) -> MaintenanceTask | None:
        task = self.update_task(task_id, tenant_id, MaintenanceTaskUpdate(status=StatusManutencao.CONCLUIDA))
        return task

    def dispatch_task(
        self,
        task_id: int,
        tenant_id: int,
        fallback_email: str | None = None,
    ) -> tuple[MaintenanceTask | None, bool, bool, str | None, str | None]:
        task = (
            self.db.query(MaintenanceTask)
            .filter(MaintenanceTask.id == task_id, MaintenanceTask.tenant_id == tenant_id)
            .first()
        )
        if not task:
            return None, False, False, None, None

        email_recipient = task.client.email if task.client and task.client.email else fallback_email
        whatsapp_recipient = task.client.phone if task.client and task.client.phone else settings.whatsapp_default_to
        subject = f"Manutencao preventiva - {task.title}"
        body = AlertDeliveryService().format_summary(
            subject,
            [
                task.description,
                f"Prazo: {task.due_date.isoformat() if task.due_date else 'sem prazo'}",
                f"Tecnico: {task.technician_name or 'nao atribuido'}",
                f"Status: {task.status.value}",
            ],
        )
        delivery = AlertDeliveryService()
        email_sent = delivery.send_email(email_recipient, subject, body)
        whatsapp_sent = delivery.send_whatsapp(whatsapp_recipient, body)
        return task, email_sent, whatsapp_sent, email_recipient, whatsapp_recipient
