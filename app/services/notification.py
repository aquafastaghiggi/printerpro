from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import OperationalNotification
from app.schemas.dashboard import DashboardAlertRead
from app.services.alert_delivery import AlertDeliveryService


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_notifications(self, tenant_id: int) -> list[OperationalNotification]:
        return (
            self.db.query(OperationalNotification)
            .filter(OperationalNotification.tenant_id == tenant_id)
            .order_by(OperationalNotification.is_read.asc(), OperationalNotification.created_at.desc())
            .all()
        )

    def list_unread_notifications(self, tenant_id: int) -> list[OperationalNotification]:
        return (
            self.db.query(OperationalNotification)
            .filter(OperationalNotification.tenant_id == tenant_id, OperationalNotification.is_read.is_(False))
            .order_by(OperationalNotification.created_at.desc())
            .all()
        )

    def upsert_from_alerts(self, tenant_id: int, alerts: list[DashboardAlertRead]) -> tuple[int, int]:
        created = 0
        updated = 0
        for alert in alerts:
            source_key = f"dashboard:{alert.title.lower().replace(' ', '_')}"
            notification = (
                self.db.query(OperationalNotification)
                .filter(
                    OperationalNotification.tenant_id == tenant_id,
                    OperationalNotification.source_key == source_key,
                )
                .first()
            )
            if notification:
                notification.severity = alert.severity
                notification.title = alert.title
                notification.detail = alert.detail
                notification.suggested_action = alert.suggested_action
                updated += 1
            else:
                notification = OperationalNotification(
                    tenant_id=tenant_id,
                    source_type="dashboard_alert",
                    source_key=source_key,
                    severity=alert.severity,
                    title=alert.title,
                    detail=alert.detail,
                    suggested_action=alert.suggested_action,
                )
                self.db.add(notification)
                created += 1
        return created, updated

    def mark_as_read(self, notification_id: int, tenant_id: int) -> OperationalNotification | None:
        notification = (
            self.db.query(OperationalNotification)
            .filter(
                OperationalNotification.id == notification_id,
                OperationalNotification.tenant_id == tenant_id,
            )
            .first()
        )
        if notification:
            notification.is_read = True
        return notification

    def dispatch_notifications(self, tenant_id: int, recipient_email: str | None) -> tuple[int, bool, bool]:
        notifications = self.list_unread_notifications(tenant_id)
        if not notifications:
            return 0, False, False

        delivery = AlertDeliveryService()
        lines = [f"{notification.title} - {notification.detail}" for notification in notifications]
        subject = f"Alertas operacionais - {len(notifications)} pendentes"
        body = delivery.format_summary(subject, lines)
        email_sent = delivery.send_email(recipient_email, subject, body)
        whatsapp_sent = delivery.send_whatsapp(settings.whatsapp_default_to, body)
        return len(notifications), email_sent, whatsapp_sent
