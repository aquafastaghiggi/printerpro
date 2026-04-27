from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.core.enums import StatusBoleto, StatusConciliacao, StatusRemessa, StatusTitulo
from app.models.contract import Contract
from app.models.finance import AccountsPayable, AccountsReceivable, BankReconciliationEntry, Boleto, Remittance
from app.models.reading import Reading
from app.core.enums import StatusContrato
from app.services.faturamento import FaturamentoService


def _money(value: Decimal | float | int | str | None) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class GeneratedBillingItem:
    contract_id: int
    receivable_id: int
    boleto_id: int | None
    amount: Decimal
    description: str


class FinanceService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_nosso_numero(self, tenant_id: int, title_id: int) -> str:
        return f"{tenant_id:04d}{title_id:012d}"

    def _build_barcode(self, bank_code: str, title_id: int, due_date: date, amount: Decimal) -> str:
        return f"{bank_code}{due_date:%Y%m%d}{title_id:010d}{int(amount * 100):010d}"

    def _update_receivable_status(self, receivable: AccountsReceivable) -> None:
        paid_total = _money(receivable.paid_amount)
        original = _money(receivable.original_amount)
        if paid_total <= 0:
            receivable.status = StatusTitulo.ABERTO
        elif paid_total < original:
            receivable.status = StatusTitulo.PARCIAL
        else:
            receivable.status = StatusTitulo.PAGO

    def _update_payable_status(self, payable: AccountsPayable) -> None:
        paid_total = _money(payable.paid_amount)
        original = _money(payable.original_amount)
        if paid_total <= 0:
            payable.status = StatusTitulo.ABERTO
        elif paid_total < original:
            payable.status = StatusTitulo.PARCIAL
        else:
            payable.status = StatusTitulo.PAGO

    def _sync_boleto_status(self, boleto: Boleto) -> None:
        if boleto.receivable_id:
            receivable = self.db.get(AccountsReceivable, boleto.receivable_id)
            if receivable and _money(receivable.paid_amount) >= _money(receivable.original_amount):
                boleto.status = StatusBoleto.PAGO
            elif receivable and _money(receivable.paid_amount) > 0:
                boleto.status = StatusBoleto.REGISTRADO
            else:
                boleto.status = StatusBoleto.GERADO
        elif boleto.payable_id:
            payable = self.db.get(AccountsPayable, boleto.payable_id)
            if payable and _money(payable.paid_amount) >= _money(payable.original_amount):
                boleto.status = StatusBoleto.PAGO

    def create_receivable(self, tenant_id: int, payload: dict) -> AccountsReceivable:
        receivable = AccountsReceivable(tenant_id=tenant_id, **payload)
        self.db.add(receivable)
        self.db.flush()
        return receivable

    def create_payable(self, tenant_id: int, payload: dict) -> AccountsPayable:
        payable = AccountsPayable(tenant_id=tenant_id, **payload)
        self.db.add(payable)
        self.db.flush()
        return payable

    def create_boleto(self, tenant_id: int, payload: dict) -> Boleto:
        if not payload.get("receivable_id") and not payload.get("payable_id"):
            raise ValueError("Informe uma conta a receber ou a pagar para gerar o boleto")
        boleto = Boleto(tenant_id=tenant_id, **payload)
        self.db.add(boleto)
        self.db.flush()
        if boleto.receivable_id:
            receivable = self.db.get(AccountsReceivable, boleto.receivable_id)
            if receivable:
                boleto.amount = receivable.original_amount
        if boleto.payable_id:
            payable = self.db.get(AccountsPayable, boleto.payable_id)
            if payable:
                boleto.amount = payable.original_amount
        boleto.nosso_numero = self._generate_nosso_numero(tenant_id, boleto.id)
        boleto.barcode = self._build_barcode(boleto.bank_code, boleto.id, boleto.due_date, _money(boleto.amount))
        boleto.pix_qr_code = f"PIX|{boleto.barcode}|{_money(boleto.amount)}"
        return boleto

    def register_receivable_payment(self, receivable: AccountsReceivable, paid_amount: Decimal | None, notes: str | None = None) -> AccountsReceivable:
        receivable.paid_amount = _money(paid_amount or receivable.original_amount)
        receivable.notes = notes or receivable.notes
        self._update_receivable_status(receivable)
        for boleto in receivable.boletos:
            self._sync_boleto_status(boleto)
        return receivable

    def register_payable_payment(self, payable: AccountsPayable, paid_amount: Decimal | None, notes: str | None = None) -> AccountsPayable:
        payable.paid_amount = _money(paid_amount or payable.original_amount)
        payable.notes = notes or payable.notes
        self._update_payable_status(payable)
        for boleto in payable.boletos:
            self._sync_boleto_status(boleto)
        return payable

    def generate_billing_for_competence(
        self,
        tenant_id: int,
        competence: str,
        issue_date: date,
        due_date: date,
        bank_code: str = "001",
        description_prefix: str = "Faturamento",
        generate_boleto: bool = True,
    ) -> tuple[list[GeneratedBillingItem], Decimal]:
        contracts = (
            self.db.query(Contract)
            .options(selectinload(Contract.plan))
            .filter(Contract.tenant_id == tenant_id, Contract.status == StatusContrato.VIGENTE)
            .all()
        )

        generated_items: list[GeneratedBillingItem] = []
        total_amount = Decimal("0.00")

        for contract in contracts:
            readings = [
                reading
                for reading in self.db.query(Reading)
                .filter(Reading.tenant_id == tenant_id, Reading.contract_id == contract.id)
                .all()
                if reading.reference_date.isoformat()[:7] == competence
            ]
            preview = FaturamentoService().calcular_preview(contract, readings)
            amount = _money(preview["valor_total"])
            description = f"{description_prefix} {competence} - {contract.number}"
            receivable = self.create_receivable(
                tenant_id,
                {
                    "contract_id": contract.id,
                    "client_id": contract.client_id,
                    "issue_date": issue_date,
                    "due_date": due_date,
                    "competence": competence,
                    "description": description,
                    "original_amount": amount,
                    "notes": f"Gerado automaticamente para o contrato {contract.number}",
                },
            )
            boleto_id = None
            if generate_boleto:
                boleto = self.create_boleto(
                    tenant_id,
                    {
                        "receivable_id": receivable.id,
                        "bank_code": bank_code,
                        "due_date": due_date,
                        "amount": amount,
                    },
                )
                boleto_id = boleto.id
                boleto.status = StatusBoleto.REGISTRADO

            generated_items.append(
                GeneratedBillingItem(
                    contract_id=contract.id,
                    receivable_id=receivable.id,
                    boleto_id=boleto_id,
                    amount=amount,
                    description=description,
                )
            )
            total_amount += amount

        return generated_items, total_amount

    def generate_remittance(self, tenant_id: int, payload: dict, boleto_ids: list[int]) -> Remittance:
        boletos = (
            self.db.query(Boleto)
            .filter(Boleto.tenant_id == tenant_id, Boleto.id.in_(boleto_ids))
            .all()
        )
        remittance = Remittance(
            tenant_id=tenant_id,
            bank_code=payload["bank_code"],
            file_type=payload["file_type"],
            file_name=payload["file_name"],
            file_url=payload.get("file_url"),
            total_titles=len(boletos),
            total_amount=sum((_money(b.amount) for b in boletos), Decimal("0.00")),
        )
        self.db.add(remittance)
        self.db.flush()
        for boleto in boletos:
            boleto.remittance_id = remittance.id
            boleto.status = StatusBoleto.ENVIADO
            boleto.sent_at = _now()
        remittance.status = StatusRemessa.ENVIADA
        return remittance

    def import_bank_entries(
        self,
        tenant_id: int,
        entries: list[dict],
        auto_match: bool = True,
    ) -> list[BankReconciliationEntry]:
        created: list[BankReconciliationEntry] = []
        for item in entries:
            entry = BankReconciliationEntry(
                tenant_id=tenant_id,
                statement_date=item["statement_date"],
                description=item["description"],
                reference=item.get("reference"),
                amount=item["amount"],
                source=item.get("source", "extrato"),
                notes=item.get("notes"),
            )
            self.db.add(entry)
            self.db.flush()
            if auto_match:
                self._auto_match_entry(entry)
            created.append(entry)
        return created

    def _auto_match_entry(self, entry: BankReconciliationEntry) -> None:
        receivable = (
            self.db.query(AccountsReceivable)
            .filter(
                AccountsReceivable.tenant_id == entry.tenant_id,
                AccountsReceivable.status.in_([StatusTitulo.ABERTO, StatusTitulo.PARCIAL]),
                AccountsReceivable.original_amount == entry.amount,
            )
            .order_by(AccountsReceivable.due_date.asc())
            .first()
        )
        if receivable:
            self.register_receivable_payment(receivable, entry.amount, entry.notes)
            entry.receivable_id = receivable.id
            entry.status = StatusConciliacao.CASADO
            entry.matched_at = _now()
            return

        payable = (
            self.db.query(AccountsPayable)
            .filter(
                AccountsPayable.tenant_id == entry.tenant_id,
                AccountsPayable.status.in_([StatusTitulo.ABERTO, StatusTitulo.PARCIAL]),
                AccountsPayable.original_amount == entry.amount,
            )
            .order_by(AccountsPayable.due_date.asc())
            .first()
        )
        if payable:
            self.register_payable_payment(payable, entry.amount, entry.notes)
            entry.payable_id = payable.id
            entry.status = StatusConciliacao.CASADO
            entry.matched_at = _now()
