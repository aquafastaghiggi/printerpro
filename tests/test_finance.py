from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_flow import build_client


def test_full_finance_flow(tmp_path: Path) -> None:
    client: TestClient = build_client(tmp_path / "finance.db")

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

    client.post(
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
    client_id = client.get("/api/v1/clientes", headers=headers).json()[0]["id"]

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
            "generate_boleto": True,
        },
    )
    assert billing_response.status_code == 200, billing_response.text
    billing_payload = billing_response.json()
    assert billing_payload["items"]

    dashboard_response = client.get("/api/v1/financeiro/dashboard", headers=headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    assert dashboard_response.json()["receivables"] >= 1

    receivables_response = client.get("/api/v1/financeiro/contas-receber", headers=headers)
    assert receivables_response.status_code == 200
    receivable_id = receivables_response.json()[0]["id"]

    payables_response = client.post(
        "/api/v1/financeiro/contas-pagar",
        headers=headers,
        json={
            "contract_id": contract_id,
            "issue_date": "2026-04-27",
            "due_date": "2026-05-05",
            "description": "Compra de toner",
            "category": "suprimentos",
            "supplier_name": "Fornecedor Alfa",
            "original_amount": 120.0,
            "notes": "Pedido mensal",
        },
    )
    assert payables_response.status_code == 200
    payable_id = payables_response.json()["id"]

    boletos_response = client.get("/api/v1/financeiro/boletos", headers=headers)
    assert boletos_response.status_code == 200
    boleto_id = boletos_response.json()[0]["id"]

    remittance_response = client.post(
        "/api/v1/financeiro/remessas",
        headers=headers,
        json={
            "bank_code": "001",
            "file_type": "cnab240",
            "file_name": "remessa-teste.txt",
            "boleto_ids": [boleto_id],
        },
    )
    assert remittance_response.status_code == 200, remittance_response.text
    assert remittance_response.json()["total_titles"] == 1

    reconciliation_response = client.post(
        "/api/v1/financeiro/conciliacao/importar",
        headers=headers,
        json={
            "auto_match": True,
            "entries": [
                {
                    "statement_date": "2026-05-10",
                    "description": "Pagamento cliente",
                    "reference": "CON-2026-001",
                    "amount": billing_payload["total_amount"],
                    "source": "extrato",
                    "notes": "Conciliado automaticamente",
                }
            ],
        },
    )
    assert reconciliation_response.status_code == 200, reconciliation_response.text
    assert reconciliation_response.json()[0]["status"] == "casado"

    aging_response = client.get("/api/v1/financeiro/inadimplencia/aging", headers=headers)
    assert aging_response.status_code == 200
    assert len(aging_response.json()["receivable_buckets"]) == 4
    assert len(aging_response.json()["payable_buckets"]) == 4

    settle_receivable = client.post(
        f"/api/v1/financeiro/contas-receber/{receivable_id}/baixa",
        headers=headers,
        json={"notes": "Baixa manual"},
    )
    assert settle_receivable.status_code == 200

    settle_payable = client.post(
        f"/api/v1/financeiro/contas-pagar/{payable_id}/baixa",
        headers=headers,
        json={"notes": "Baixa manual"},
    )
    assert settle_payable.status_code == 200

