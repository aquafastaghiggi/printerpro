from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_flow import build_client


def test_full_fiscal_flow(tmp_path: Path) -> None:
    client: TestClient = build_client(tmp_path / "fiscal.db")

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

    client_response = client.post(
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
    client_id = client_response.json()["id"]

    plan_response = client.post(
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
    plan_id = plan_response.json()["id"]

    equipment_response = client.post(
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
    equipment_id = equipment_response.json()["id"]

    contract_response = client.post(
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
    contract_id = contract_response.json()["id"]

    client.post(
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
            "notes": "Leitura inicial",
        },
    )

    billing_response = client.post(
        "/api/v1/financeiro/faturamento/gerar",
        headers=headers,
        json={
            "competence": "2026-04",
            "bank_code": "001",
            "issue_date": "2026-04-27",
            "due_date": "2026-05-10",
            "description_prefix": "Faturamento",
            "generate_boleto": False,
        },
    )
    assert billing_response.status_code == 200, billing_response.text

    config_response = client.get("/api/v1/fiscal/configuracao", headers=headers)
    assert config_response.status_code == 200, config_response.text
    assert config_response.json()["company_name"] == "Empresa Demo"

    issue_response = client.post(
        "/api/v1/fiscal/documentos/gerar-recebiveis",
        headers=headers,
        json={
            "document_type": "nfse",
            "issue_date": "2026-04-27",
            "competence": "2026-04",
            "authorize": True,
        },
    )
    assert issue_response.status_code == 200, issue_response.text
    documents = issue_response.json()
    assert len(documents) == 1
    document_id = documents[0]["id"]

    dashboard_response = client.get("/api/v1/fiscal/dashboard", headers=headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    assert dashboard_response.json()["total_documents"] == 1

    update_response = client.put(
        f"/api/v1/fiscal/documentos/{document_id}",
        headers=headers,
        json={"notes": "Ajuste fiscal"},
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["notes"] == "Ajuste fiscal"

    cancel_response = client.post(f"/api/v1/fiscal/documentos/{document_id}/cancelar", headers=headers)
    assert cancel_response.status_code == 200, cancel_response.text
    assert cancel_response.json()["status"] == "cancelado"

