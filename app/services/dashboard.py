from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.core.enums import StatusChamado, StatusContrato, StatusEquipamento, StatusManutencao, StatusTitulo
from app.models.client import Client
from app.models.contract import Contract
from app.models.equipment import Equipment
from app.models.finance import AccountsPayable, AccountsReceivable
from app.models.maintenance import MaintenanceTask
from app.models.portal import PortalTicket
from app.models.reading import Reading
from app.schemas.dashboard import (
    DashboardAlertRead,
    DashboardBIRead,
    DashboardBreakdownPointRead,
    DashboardClientInsightRead,
    DashboardEquipmentIssueRead,
    DashboardMetricsRead,
    DashboardOverviewResponse,
    DashboardRenewalRead,
    DashboardSeriesPointRead,
)


def _money(value: Decimal | float | int | str | None) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def build_overview(self, tenant_id: int) -> DashboardOverviewResponse:
        today = date.today()
        month_start = today - timedelta(days=30)
        in_30_days = today + timedelta(days=30)
        month_labels = self._last_month_labels(today, 6)

        clients = self.db.query(Client).filter(Client.tenant_id == tenant_id).all()
        contracts = (
            self.db.query(Contract)
            .options(selectinload(Contract.client))
            .filter(Contract.tenant_id == tenant_id)
            .order_by(Contract.id.desc())
            .all()
        )
        equipment = (
            self.db.query(Equipment)
            .filter(Equipment.tenant_id == tenant_id)
            .order_by(Equipment.id.desc())
            .all()
        )
        receivables = (
            self.db.query(AccountsReceivable)
            .filter(AccountsReceivable.tenant_id == tenant_id)
            .order_by(AccountsReceivable.due_date.desc(), AccountsReceivable.id.desc())
            .all()
        )
        payables = (
            self.db.query(AccountsPayable)
            .filter(AccountsPayable.tenant_id == tenant_id)
            .order_by(AccountsPayable.due_date.desc(), AccountsPayable.id.desc())
            .all()
        )
        readings = (
            self.db.query(Reading)
            .filter(Reading.tenant_id == tenant_id)
            .order_by(Reading.reference_date.desc(), Reading.id.desc())
            .all()
        )
        maintenance_tasks = (
            self.db.query(MaintenanceTask)
            .filter(MaintenanceTask.tenant_id == tenant_id)
            .order_by(MaintenanceTask.due_date.asc(), MaintenanceTask.id.desc())
            .all()
        )
        tickets = (
            self.db.query(PortalTicket)
            .filter(PortalTicket.tenant_id == tenant_id)
            .order_by(PortalTicket.id.desc())
            .all()
        )

        open_receivables_total = Decimal("0.00")
        overdue_receivables_total = Decimal("0.00")
        overdue_payables_total = Decimal("0.00")
        client_stats: dict[int, dict[str, object]] = defaultdict(
            lambda: {
                "contracts": 0,
                "open_total": Decimal("0.00"),
                "overdue_total": Decimal("0.00"),
            }
        )

        for contract in contracts:
            if contract.client_id is not None:
                client_stats[contract.client_id]["contracts"] = int(client_stats[contract.client_id]["contracts"]) + 1

        for receivable in receivables:
            outstanding = _money(receivable.original_amount) - _money(receivable.paid_amount)
            outstanding += _money(receivable.interest_amount) + _money(receivable.penalty_amount) - _money(receivable.discount_amount)
            if receivable.status != StatusTitulo.PAGO:
                open_receivables_total += outstanding
                if receivable.client_id is not None:
                    client_stats[receivable.client_id]["open_total"] = _money(client_stats[receivable.client_id]["open_total"]) + outstanding
                if receivable.due_date < today:
                    overdue_receivables_total += outstanding
                    if receivable.client_id is not None:
                        client_stats[receivable.client_id]["overdue_total"] = _money(client_stats[receivable.client_id]["overdue_total"]) + outstanding

        for payable in payables:
            outstanding = _money(payable.original_amount) - _money(payable.paid_amount)
            if payable.status != StatusTitulo.PAGO and payable.due_date < today:
                overdue_payables_total += outstanding

        readings_last_30_days = sum(1 for reading in readings if reading.reference_date >= month_start)
        unvalidated_readings = sum(1 for reading in readings if not reading.validated)
        active_contracts = sum(1 for contract in contracts if contract.status == StatusContrato.VIGENTE)
        active_equipment = sum(1 for item in equipment if item.status != StatusEquipamento.BAIXADO)
        open_tickets = sum(1 for item in tickets if item.status in {StatusChamado.ABERTO, StatusChamado.EM_ATENDIMENTO})
        contracts_expiring_30_days = sum(
            1
            for contract in contracts
            if contract.status == StatusContrato.VIGENTE and contract.end_date is not None and today <= contract.end_date <= in_30_days
        )
        overdue_receivables_count = sum(1 for receivable in receivables if receivable.status != StatusTitulo.PAGO and receivable.due_date < today)
        maintenance_count = sum(1 for item in equipment if item.status == StatusEquipamento.MANUTENCAO)

        alerts: list[DashboardAlertRead] = []
        if overdue_receivables_count > 0:
            alerts.append(
                DashboardAlertRead(
                    severity="critical",
                    title="Cobranca exige acao",
                    detail=f"{overdue_receivables_count} titulos vencidos somam {overdue_receivables_total:.2f}.",
                    suggested_action="Disparar lembretes automaticos de cobranca.",
                    count=overdue_receivables_count,
                )
            )
        if contracts_expiring_30_days > 0:
            alerts.append(
                DashboardAlertRead(
                    severity="warning",
                    title="Renovacoes proximas",
                    detail=f"{contracts_expiring_30_days} contrato(s) vencem nos proximos 30 dias.",
                    suggested_action="Abrir fluxo de renovacao comercial.",
                    count=contracts_expiring_30_days,
                )
            )
        if unvalidated_readings > 0:
            alerts.append(
                DashboardAlertRead(
                    severity="warning",
                    title="Leituras pendentes de validacao",
                    detail=f"{unvalidated_readings} leitura(s) aguardam conferencia manual.",
                    suggested_action="Validar leituras antes do faturamento.",
                    count=unvalidated_readings,
                )
            )
        if maintenance_count > 0:
            alerts.append(
                DashboardAlertRead(
                    severity="info",
                    title="Operacao de campo ativa",
                    detail=f"{maintenance_count} equipamento(s) estao em manutencao.",
                    suggested_action="Agendar visita tecnica e atualizar os status.",
                    count=maintenance_count,
                )
            )
        if open_tickets > 0:
            alerts.append(
                DashboardAlertRead(
                    severity="info",
                    title="Suporte aberto",
                    detail=f"{open_tickets} chamado(s) seguem em atendimento.",
                    suggested_action="Priorizar o atendimento no portal e mobile.",
                    count=open_tickets,
                )
            )

        renewals = [
            DashboardRenewalRead(
                contract_id=contract.id,
                number=contract.number,
                client_name=contract.client.name if contract.client else f"Cliente #{contract.client_id}",
                end_date=contract.end_date,
                days_left=(contract.end_date - today).days if contract.end_date else 0,
                status=contract.status.value,
            )
            for contract in contracts
            if contract.status == StatusContrato.VIGENTE and contract.end_date is not None and today <= contract.end_date <= in_30_days
        ]
        renewals.sort(key=lambda item: item.days_left)

        top_clients = []
        for client in clients:
            stats = client_stats[client.id]
            if any((stats["contracts"], stats["open_total"], stats["overdue_total"])):
                top_clients.append(
                    DashboardClientInsightRead(
                        client_id=client.id,
                        client_name=client.name,
                        contracts=int(stats["contracts"]),
                        open_total=_money(stats["open_total"]),
                        overdue_total=_money(stats["overdue_total"]),
                    )
                )
        top_clients.sort(key=lambda item: (item.overdue_total, item.open_total), reverse=True)

        equipment_issues = []
        for item in equipment:
            issue: str | None = None
            if item.status == StatusEquipamento.MANUTENCAO:
                issue = "Em manutencao preventiva"
            elif item.status == StatusEquipamento.BAIXADO:
                issue = "Baixado do ativo"
            elif item.client_id is None:
                issue = "Sem cliente vinculado"
            if issue:
                equipment_issues.append(
                    DashboardEquipmentIssueRead(
                        equipment_id=item.id,
                        serial_number=item.serial_number,
                        brand=item.brand,
                        model=item.model,
                        client_name=self._resolve_client_name(clients, item.client_id),
                        location=item.location,
                        status=item.status,
                        issue=issue,
                    )
                )

        return DashboardOverviewResponse(
            generated_at=datetime.now(timezone.utc),
            metrics=DashboardMetricsRead(
                clients_total=len(clients),
                active_contracts=active_contracts,
                active_equipment=active_equipment,
                readings_last_30_days=readings_last_30_days,
                open_tickets=open_tickets,
                contracts_expiring_30_days=contracts_expiring_30_days,
                unvalidated_readings=unvalidated_readings,
                receivables_open_total=_money(open_receivables_total),
                receivables_overdue_total=_money(overdue_receivables_total),
                payables_overdue_total=_money(overdue_payables_total),
            ),
            alerts=alerts,
            renewals=renewals,
            top_clients=top_clients[:5],
            equipment_issues=equipment_issues[:6],
            bi=DashboardBIRead(
                revenue_by_month=[
                    DashboardSeriesPointRead(label=label, value=value)
                    for label, value in self._aggregate_series(receivables, month_labels, lambda item: item.competence, lambda item: _money(item.original_amount))
                ],
                readings_by_month=[
                    DashboardSeriesPointRead(label=label, value=value)
                    for label, value in self._aggregate_series(readings, month_labels, lambda item: item.reference_date.strftime("%Y-%m"), lambda _: Decimal("1"))
                ],
                equipment_status=[
                    DashboardBreakdownPointRead(label=self._status_label(status), count=sum(1 for item in equipment if item.status == status))
                    for status in (StatusEquipamento.DISPONIVEL, StatusEquipamento.LOCADO, StatusEquipamento.MANUTENCAO, StatusEquipamento.BAIXADO)
                ],
                maintenance_status=[
                    DashboardBreakdownPointRead(
                        label=self._maintenance_label(status),
                        count=sum(1 for item in maintenance_tasks if item.status.value == status),
                    )
                    for status in ("pendente", "agendada", "em_execucao", "concluida", "cancelada")
                ],
                maintenance_open_total=max(
                    maintenance_count,
                    sum(1 for task in maintenance_tasks if task.status in {StatusManutencao.PENDENTE, StatusManutencao.AGENDADA, StatusManutencao.EM_EXECUCAO}),
                ),
            ),
        )

    @staticmethod
    def _resolve_client_name(clients: list[Client], client_id: int | None) -> str | None:
        if client_id is None:
            return None
        for client in clients:
            if client.id == client_id:
                return client.name
        return None

    @staticmethod
    def _last_month_labels(today: date, count: int) -> list[str]:
        labels: list[str] = []
        year = today.year
        month = today.month
        for _ in range(count):
            labels.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return list(reversed(labels))

    @staticmethod
    def _aggregate_series(items, labels: list[str], key_fn, value_fn) -> list[tuple[str, Decimal]]:
        totals: dict[str, Decimal] = {label: Decimal("0.00") for label in labels}
        for item in items:
            label = key_fn(item)
            if label in totals:
                totals[label] += Decimal(str(value_fn(item)))
        return [(label, totals[label].quantize(Decimal("0.01"))) for label in labels]

    @staticmethod
    def _status_label(status: StatusEquipamento) -> str:
        labels = {
            StatusEquipamento.DISPONIVEL: "Disponivel",
            StatusEquipamento.LOCADO: "Locado",
            StatusEquipamento.MANUTENCAO: "Em manutencao",
            StatusEquipamento.BAIXADO: "Baixado",
        }
        return labels[status]

    @staticmethod
    def _maintenance_label(status: str) -> str:
        labels = {
            "pendente": "Pendente",
            "agendada": "Agendada",
            "em_execucao": "Em execucao",
            "concluida": "Concluida",
            "cancelada": "Cancelada",
        }
        return labels[status]
