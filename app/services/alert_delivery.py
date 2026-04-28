from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from urllib import error, request

from app.core.config import settings


class AlertDeliveryService:
    def __init__(self) -> None:
        self.settings = settings

    def send_email(self, recipient_email: str | None, subject: str, body: str) -> bool:
        if not recipient_email or not self.settings.smtp_host:
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.smtp_from_email or self.settings.smtp_username or "noreply@localhost"
        message["To"] = recipient_email
        message.set_content(body)

        try:
            if self.settings.smtp_use_ssl:
                client = smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port, timeout=15)
            else:
                client = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15)

            with client as smtp:
                if self.settings.smtp_use_tls and not self.settings.smtp_use_ssl:
                    smtp.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                smtp.send_message(message)
            return True
        except (OSError, smtplib.SMTPException):
            return False

    def send_whatsapp(self, recipient_phone: str | None, body: str) -> bool:
        if not recipient_phone:
            return False

        payload: dict[str, object]
        headers = {"Content-Type": "application/json"}
        url = self.settings.whatsapp_api_url

        if url:
            payload = {"to": recipient_phone, "message": body}
            if self.settings.whatsapp_access_token:
                headers["Authorization"] = f"Bearer {self.settings.whatsapp_access_token}"
        elif self.settings.whatsapp_phone_number_id and self.settings.whatsapp_access_token:
            url = f"https://graph.facebook.com/v19.0/{self.settings.whatsapp_phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "text",
                "text": {"body": body},
            }
            headers["Authorization"] = f"Bearer {self.settings.whatsapp_access_token}"
        else:
            return False

        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=15) as response:
                return 200 <= response.status < 300
        except (error.URLError, OSError):
            return False

    @staticmethod
    def format_summary(subject: str, lines: list[str]) -> str:
        body_lines = [subject, ""]
        body_lines.extend(f"- {line}" for line in lines)
        return "\n".join(body_lines)
