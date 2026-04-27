from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def build_client(db_path: Path) -> TestClient:
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["AUTO_CREATE_TABLES"] = "false"

    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=True)

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name, None)

    from app.main import app

    return TestClient(app)


def test_full_mvp_flow(tmp_path: Path) -> None:
    client = build_client(tmp_path / "flow.db")

    bootstrap = {
        "tenant_name": "Empresa Demo",
        "tenant_document": "12345678000199",
        "admin_name": "Admin Demo",
        "admin_email": "admin@demo.com",
        "admin_password": "123456",
    }
    response = client.post("/api/v1/auth/setup", json=bootstrap)
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    login = {
        "tenant_key": "12345678000199",
        "email": "admin@demo.com",
        "password": "123456",
    }
    response = client.post("/api/v1/auth/login", json=login)
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]

    response = client.post(
        "/api/v1/clientes",
        headers=headers,
        json={
            "person_type": "pj",
            "name": "Cliente Alfa",
            "document": "11222333000144",
            "email": "contato@alfa.com",
            "phone": "11999990000",
            "credit_score": 720,
            "credit_status": "ok",
        },
    )
    assert response.status_code == 200, response.text
    client_id = response.json()["id"]

    response = client.post(
        "/api/v1/planos",
        headers=headers,
        json={
            "name": "Franquia 5k",
            "type": "franquia",
            "monthly_fee": 499.9,
            "franchise_pb": 5000,
            "franchise_color": 1000,
            "extra_pb": 0.09,
            "extra_color": 0.25,
        },
    )
    assert response.status_code == 200, response.text
    plan_id = response.json()["id"]

    response = client.post(
        "/api/v1/equipamentos",
        headers=headers,
        json={
            "client_id": client_id,
            "serial_number": "SN-001",
            "brand": "HP",
            "model": "M428",
            "kind": "multifuncional",
            "status": "locado",
            "location": "Escritorio principal",
        },
    )
    assert response.status_code == 200, response.text
    equipment_id = response.json()["id"]

    response = client.post(
        "/api/v1/contratos",
        headers=headers,
        json={
            "client_id": client_id,
            "plan_id": plan_id,
            "number": "CON-2026-001",
            "start_date": "2026-04-27",
            "status": "vigente",
            "billing_day": 10,
            "monthly_value": 499.9,
            "franchise_pb": 5000,
            "franchise_color": 1000,
            "price_excess_pb": 0.09,
            "price_excess_color": 0.25,
            "equipment_ids": [equipment_id],
        },
    )
    assert response.status_code == 200, response.text
    contract_id = response.json()["id"]

    response = client.post(
        "/api/v1/leituras",
        headers=headers,
        json={
            "contract_id": contract_id,
            "equipment_id": equipment_id,
            "reference_date": "2026-04-27",
            "source": "manual",
            "counter_pb_current": 5250,
            "counter_pb_previous": 4800,
            "counter_color_current": 1130,
            "counter_color_previous": 1100,
            "validated": True,
            "photo_url": "https://example.com/counter.jpg",
            "notes": "Leitura inicial",
        },
    )
    assert response.status_code == 200, response.text
    reading_id = response.json()["id"]

    response = client.get("/api/v1/clientes?q=Cliente", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/api/v1/contratos?client_id={client_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/api/v1/leituras?contract_id={contract_id}&validated=true", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/api/v1/tenants", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    for path in [
        f"/api/v1/leituras/{reading_id}",
        f"/api/v1/contratos/{contract_id}",
        f"/api/v1/equipamentos/{equipment_id}",
        f"/api/v1/planos/{plan_id}",
        f"/api/v1/clientes/{client_id}",
    ]:
        response = client.delete(path, headers=headers)
        assert response.status_code == 200, (path, response.text)

