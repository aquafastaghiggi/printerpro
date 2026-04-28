from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationDispatchResponse, NotificationSyncResponse, OperationalNotificationRead
from app.services.dashboard import DashboardService
from app.services.notification import NotificationService

router = APIRouter()


@router.get("", response_model=list[OperationalNotificationRead])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list:
    return NotificationService(db).list_notifications(current_user.tenant_id)


@router.post("/sincronizar", response_model=NotificationSyncResponse)
def sync_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> NotificationSyncResponse:
    dashboard = DashboardService(db).build_overview(current_user.tenant_id)
    service = NotificationService(db)
    created, updated = service.upsert_from_alerts(current_user.tenant_id, dashboard.alerts)
    db.commit()
    return NotificationSyncResponse(
        created=created,
        updated=updated,
        total=created + updated,
        generated_at=datetime.now(timezone.utc),
    )


@router.post("/{notification_id}/lida", response_model=OperationalNotificationRead)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> OperationalNotificationRead:
    service = NotificationService(db)
    notification = service.mark_as_read(notification_id, current_user.tenant_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificacao nao encontrada")
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/disparar", response_model=NotificationDispatchResponse)
def dispatch_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> NotificationDispatchResponse:
    service = NotificationService(db)
    notifications_count, email_sent, whatsapp_sent = service.dispatch_notifications(current_user.tenant_id, current_user.email)
    if notifications_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nao ha notificacoes pendentes")
    db.commit()
    return NotificationDispatchResponse(
        notifications_count=notifications_count,
        email_sent=email_sent,
        whatsapp_sent=whatsapp_sent,
        email_recipient=current_user.email,
        whatsapp_recipient=None,
        subject=f"Alertas operacionais - {notifications_count} pendentes",
        generated_at=datetime.now(timezone.utc),
    )
