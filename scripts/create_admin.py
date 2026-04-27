from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import or_
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.enums import UserRole
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User


def main() -> None:
    if settings.auto_create_tables:
        init_db()
    tenant_name = os.getenv("ADMIN_TENANT_NAME", "Empresa Modelo")
    tenant_document = os.getenv("ADMIN_TENANT_DOCUMENT", "00000000000000")
    admin_name = os.getenv("ADMIN_NAME", "Usuario Modelo")
    admin_email = os.getenv("ADMIN_EMAIL", "demo@printerpro.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "123456")

    db: Session = SessionLocal()
    try:
        tenant = (
            db.query(Tenant)
            .filter(or_(Tenant.document == tenant_document, Tenant.name == tenant_name))
            .first()
        )
        if not tenant:
            tenant = Tenant(name=tenant_name, document=tenant_document)
            db.add(tenant)
        else:
            tenant.name = tenant_name
            tenant.document = tenant_document
        db.flush()

        user = db.query(User).filter(User.tenant_id == tenant.id, User.email == admin_email).first()
        if not user:
            user = (
                db.query(User)
                .filter(User.tenant_id == tenant.id, User.role == UserRole.ADMIN)
                .order_by(User.id.asc())
                .first()
            )
        if not user:
            user = User(
                tenant_id=tenant.id,
                name=admin_name,
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=UserRole.ADMIN,
            )
            db.add(user)
        else:
            user.name = admin_name
            user.email = admin_email
            user.password_hash = hash_password(admin_password)
            user.role = UserRole.ADMIN

        db.commit()
        print(
            "Empresa modelo pronta. "
            f"tenant_id={tenant.id}, user_id={user.id if user.id else 'novo'}, "
            f"tenant={tenant_name}, login={admin_email}, senha={admin_password}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
