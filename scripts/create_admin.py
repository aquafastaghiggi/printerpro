from __future__ import annotations

import os
import sys
from pathlib import Path

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
    tenant_name = os.getenv("ADMIN_TENANT_NAME", "Empresa Demo")
    tenant_document = os.getenv("ADMIN_TENANT_DOCUMENT", "00000000000000")
    admin_name = os.getenv("ADMIN_NAME", "Administrador")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@demo.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    db: Session = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
        if not tenant:
            tenant = Tenant(name=tenant_name, document=tenant_document)
            db.add(tenant)
            db.flush()

        user = db.query(User).filter(User.email == admin_email, User.tenant_id == tenant.id).first()
        if not user:
            user = User(
                tenant_id=tenant.id,
                name=admin_name,
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=UserRole.ADMIN,
            )
            db.add(user)

        db.commit()
        print(f"Admin pronto. tenant_id={tenant.id}, user_id={user.id if user.id else 'novo'}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
