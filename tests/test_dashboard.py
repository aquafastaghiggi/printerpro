from __future__ import annotations

from pathlib import Path

from tests.test_flow import build_client


def test_executive_dashboard_overview(tmp_path: Path) -> None:
    client = build_client(tmp_path / "dashboard.db")

    bootstrap = {
        "tenant_name": "Empresa Demo",
        "tenant_document": "12345678000199",
        "admin_name": "Admin Demo",
        "admin_email": "admin@demo.com",
        "admin_password": "123456",
    }
    response = client.post("/api/v1/auth/setup", json=bootstrap)
    assert response.status_code == 200, response.text
    admin_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

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
            "status": "em_manutencao",
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
            "end_date": "2026-05-08",
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
            "validated": False,
            "notes": "Leitura inicial",
        },
    )

    receivable_response = client.post(
        "/api/v1/financeiro/contas-receber",
        headers=headers,
        json={
            "contract_id": contract_id,
            "client_id": client_id,
            "issue_date": "2026-04-01",
            "due_date": "2026-04-15",
            "competence": "2026-04",
            "description": "Faturamento abril",
            "original_amount": 899.9,
            "notes": "Titulo vencido",
        },
    )
    assert receivable_response.status_code == 200, receivable_response.text

    portal_login = client.post(
        "/api/v1/portal/login",
        json={"tenant_key": bootstrap["tenant_document"], "client_document": "11222333000144"},
    )
    assert portal_login.status_code == 200, portal_login.text
    portal_token = portal_login.json()["access_token"]
    portal_headers = {"Authorization": f"Bearer {portal_token}"}

    ticket_response = client.post(
        "/api/v1/portal/chamados",
        headers=portal_headers,
        json={
            "subject": "Suporte de impressao",
            "description": "O equipamento precisa de revisao",
            "priority": "alta",
            "contract_id": contract_id,
            "equipment_id": equipment_id,
        },
    )
    assert ticket_response.status_code == 200, ticket_response.text

    dashboard_response = client.get("/api/v1/dashboard/executivo", headers=headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    payload = dashboard_response.json()

    assert payload["metrics"]["clients_total"] == 1
    assert payload["metrics"]["active_contracts"] == 1
    assert payload["metrics"]["contracts_expiring_30_days"] == 1
    assert payload["metrics"]["unvalidated_readings"] == 1
    assert payload["metrics"]["open_tickets"] == 1
    assert payload["alerts"]
    assert payload["renewals"]
    assert payload["top_clients"][0]["client_name"] == "Cliente Alfa"
    assert payload["equipment_issues"][0]["issue"] in {"Em manutencao preventiva", "Sem cliente vinculado"}
    assert payload["bi"]["maintenance_open_total"] == 1
    assert payload["bi"]["equipment_status"]
    assert payload["bi"]["revenue_by_month"]

    sync_response = client.post("/api/v1/notificacoes/sincronizar", headers=headers)
    assert sync_response.status_code == 200, sync_response.text
    assert sync_response.json()["created"] >= 1

    notifications_response = client.get("/api/v1/notificacoes", headers=headers)
    assert notifications_response.status_code == 200, notifications_response.text
    notifications = notifications_response.json()
    assert notifications

    mark_read_response = client.post(f"/api/v1/notificacoes/{notifications[0]['id']}/lida", headers=headers)
    assert mark_read_response.status_code == 200, mark_read_response.text
    assert mark_read_response.json()["is_read"] is True


def test_maintenance_queue_and_dispatch(tmp_path: Path, monkeypatch) -> None:
    client = build_client(tmp_path / "maintenance.db")

    bootstrap = {
        "tenant_name": "Empresa Demo",
        "tenant_document": "12345678000199",
        "admin_name": "Admin Demo",
        "admin_email": "admin@demo.com",
        "admin_password": "123456",
    }
    response = client.post("/api/v1/auth/setup", json=bootstrap)
    assert response.status_code == 200, response.text
    admin_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(
        "/api/v1/clientes",
        headers=headers,
        json={
            "person_type": "pj",
            "name": "Cliente Beta",
            "document": "22345678000199",
            "email": "contato@beta.com",
            "phone": "11988887777",
            "credit_score": 680,
            "credit_status": "ok",
        },
    )
    client_id = client.get("/api/v1/clientes", headers=headers).json()[0]["id"]

    equipment_response = client.post(
        "/api/v1/equipamentos",
        headers=headers,
        json={
            "client_id": client_id,
            "serial_number": "SN-002",
            "brand": "Brother",
            "model": "DCP-L2540DW",
            "kind": "laser",
            "status": "em_manutencao",
            "location": "Sala tecnica",
        },
    )
    assert equipment_response.status_code == 200, equipment_response.text

    sync_response = client.post("/api/v1/manutencao/fila/sincronizar", headers=headers)
    assert sync_response.status_code == 200, sync_response.text
    assert sync_response.json()["created"] == 1

    tasks_response = client.get("/api/v1/manutencao/fila", headers=headers)
    assert tasks_response.status_code == 200, tasks_response.text
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "pendente"

    start_response = client.post(f"/api/v1/manutencao/fila/{tasks[0]['id']}/iniciar", headers=headers)
    assert start_response.status_code == 200, start_response.text
    assert start_response.json()["status"] == "em_execucao"

    complete_response = client.post(f"/api/v1/manutencao/fila/{tasks[0]['id']}/concluir", headers=headers)
    assert complete_response.status_code == 200, complete_response.text
    assert complete_response.json()["status"] == "concluida"

    monkeypatch.setattr("app.services.alert_delivery.AlertDeliveryService.send_email", lambda self, recipient_email, subject, body: True)
    monkeypatch.setattr("app.services.alert_delivery.AlertDeliveryService.send_whatsapp", lambda self, recipient_phone, body: True)

    dispatch_task_response = client.post(f"/api/v1/manutencao/fila/{tasks[0]['id']}/enviar", headers=headers)
    assert dispatch_task_response.status_code == 200, dispatch_task_response.text
    assert dispatch_task_response.json()["email_sent"] is True

    sync_notifications = client.post("/api/v1/notificacoes/sincronizar", headers=headers)
    assert sync_notifications.status_code == 200, sync_notifications.text

    dispatch_response = client.post("/api/v1/notificacoes/disparar", headers=headers)
    assert dispatch_response.status_code == 200, dispatch_response.text
    payload = dispatch_response.json()
    assert payload["notifications_count"] >= 1
    assert payload["email_sent"] is True
