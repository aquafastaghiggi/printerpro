from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import StatusBoleto, StatusConciliacao, StatusRemessa, StatusTitulo
from app.models.finance import AccountsPayable, AccountsReceivable, BankReconciliationEntry, Boleto, Remittance
from app.models.user import User
from app.schemas.finance import (
    AccountsPayableCreate,
    AccountsPayableRead,
    AccountsPayableUpdate,
    AccountsReceivableCreate,
    AccountsReceivableRead,
    AccountsReceivableUpdate,
    BankStatementEntryRead,
    BankStatementImportRequest,
    BillingGenerationRequest,
    BillingGenerationResponse,
    BoletoCreate,
    BoletoRead,
    BoletoUpdate,
    AgingBucketRead,
    AgingResponse,
    FinanceSummaryResponse,
    RemittanceCreate,
    RemittanceRead,
    SettlementRequest,
)
from app.services.finance import FinanceService

router = APIRouter()


def _ensure_owner(obj, tenant_id: int) -> None:
    if not obj or obj.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro nao encontrado")


def _service(db: Session) -> FinanceService:
    return FinanceService(db)


@router.get("/dashboard", response_model=FinanceSummaryResponse)
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> FinanceSummaryResponse:
    receivables = db.query(AccountsReceivable).filter(AccountsReceivable.tenant_id == current_user.tenant_id).all()
    payables = db.query(AccountsPayable).filter(AccountsPayable.tenant_id == current_user.tenant_id).all()
    boletos = db.query(Boleto).filter(Boleto.tenant_id == current_user.tenant_id).all()

    today = date.today()
    receivable_open_total = sum(
        (
            r.original_amount - r.paid_amount + r.interest_amount + r.penalty_amount - r.discount_amount
            for r in receivables
            if r.status in {StatusTitulo.ABERTO, StatusTitulo.PARCIAL}
        ),
        Decimal("0.00"),
    )
    receivable_overdue_total = sum(
        (
            r.original_amount - r.paid_amount + r.interest_amount + r.penalty_amount - r.discount_amount
            for r in receivables
            if r.status != StatusTitulo.PAGO and r.due_date < today
        ),
        Decimal("0.00"),
    )
    payable_open_total = sum(
        ((p.original_amount - p.paid_amount) for p in payables if p.status in {StatusTitulo.ABERTO, StatusTitulo.PARCIAL}),
        Decimal("0.00"),
    )
    payable_overdue_total = sum(
        ((p.original_amount - p.paid_amount) for p in payables if p.status != StatusTitulo.PAGO and p.due_date < today),
        Decimal("0.00"),
    )

    return FinanceSummaryResponse(
        receivable_open_total=Decimal(str(receivable_open_total or 0)).quantize(Decimal("0.01")),
        receivable_overdue_total=Decimal(str(receivable_overdue_total or 0)).quantize(Decimal("0.01")),
        payable_open_total=Decimal(str(payable_open_total or 0)).quantize(Decimal("0.01")),
        payable_overdue_total=Decimal(str(payable_overdue_total or 0)).quantize(Decimal("0.01")),
        boletos_open=sum(1 for item in boletos if item.status in {StatusBoleto.GERADO, StatusBoleto.ENVIADO, StatusBoleto.REGISTRADO}),
        boletos_paid=sum(1 for item in boletos if item.status == StatusBoleto.PAGO),
        receivables=len(receivables),
        payables=len(payables),
    )


@router.get("/contas-receber", response_model=list[AccountsReceivableRead])
def list_receivables(
    q: str | None = None,
    status_filter: StatusTitulo | None = None,
    client_id: int | None = None,
    contract_id: int | None = None,
    competence: str | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AccountsReceivable]:
    query = db.query(AccountsReceivable).filter(AccountsReceivable.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(AccountsReceivable.description.ilike(term), AccountsReceivable.competence.ilike(term)))
    if status_filter is not None:
        query = query.filter(AccountsReceivable.status == status_filter)
    if client_id is not None:
        query = query.filter(AccountsReceivable.client_id == client_id)
    if contract_id is not None:
        query = query.filter(AccountsReceivable.contract_id == contract_id)
    if competence is not None:
        query = query.filter(AccountsReceivable.competence == competence)
    if due_from is not None:
        query = query.filter(AccountsReceivable.due_date >= due_from)
    if due_to is not None:
        query = query.filter(AccountsReceivable.due_date <= due_to)
    return query.order_by(AccountsReceivable.due_date.desc(), AccountsReceivable.id.desc()).offset(skip).limit(limit).all()


@router.get("/contas-receber/{receivable_id}", response_model=AccountsReceivableRead)
def get_receivable(receivable_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AccountsReceivable:
    receivable = db.get(AccountsReceivable, receivable_id)
    _ensure_owner(receivable, current_user.tenant_id)
    return receivable


@router.post("/contas-receber", response_model=AccountsReceivableRead)
def create_receivable(
    payload: AccountsReceivableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsReceivable:
    service = _service(db)
    receivable = service.create_receivable(current_user.tenant_id, payload.model_dump())
    db.commit()
    db.refresh(receivable)
    return receivable


@router.put("/contas-receber/{receivable_id}", response_model=AccountsReceivableRead)
def update_receivable(
    receivable_id: int,
    payload: AccountsReceivableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsReceivable:
    receivable = db.get(AccountsReceivable, receivable_id)
    _ensure_owner(receivable, current_user.tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(receivable, field, value)
    FinanceService(db)._update_receivable_status(receivable)
    db.commit()
    db.refresh(receivable)
    return receivable


@router.post("/contas-receber/{receivable_id}/baixa", response_model=AccountsReceivableRead)
def settle_receivable(
    receivable_id: int,
    payload: SettlementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsReceivable:
    receivable = db.get(AccountsReceivable, receivable_id)
    _ensure_owner(receivable, current_user.tenant_id)
    service = _service(db)
    service.register_receivable_payment(receivable, payload.paid_amount, payload.notes)
    db.commit()
    db.refresh(receivable)
    return receivable


@router.delete("/contas-receber/{receivable_id}")
def delete_receivable(receivable_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, str]:
    receivable = db.get(AccountsReceivable, receivable_id)
    _ensure_owner(receivable, current_user.tenant_id)
    db.delete(receivable)
    db.commit()
    return {"detail": "Conta a receber removida com sucesso"}


@router.get("/contas-pagar", response_model=list[AccountsPayableRead])
def list_payables(
    q: str | None = None,
    status_filter: StatusTitulo | None = None,
    contract_id: int | None = None,
    category: str | None = None,
    due_from: date | None = None,
    due_to: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AccountsPayable]:
    query = db.query(AccountsPayable).filter(AccountsPayable.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(AccountsPayable.description.ilike(term), AccountsPayable.supplier_name.ilike(term)))
    if status_filter is not None:
        query = query.filter(AccountsPayable.status == status_filter)
    if contract_id is not None:
        query = query.filter(AccountsPayable.contract_id == contract_id)
    if category is not None:
        query = query.filter(AccountsPayable.category == category)
    if due_from is not None:
        query = query.filter(AccountsPayable.due_date >= due_from)
    if due_to is not None:
        query = query.filter(AccountsPayable.due_date <= due_to)
    return query.order_by(AccountsPayable.due_date.desc(), AccountsPayable.id.desc()).offset(skip).limit(limit).all()


@router.get("/contas-pagar/{payable_id}", response_model=AccountsPayableRead)
def get_payable(payable_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AccountsPayable:
    payable = db.get(AccountsPayable, payable_id)
    _ensure_owner(payable, current_user.tenant_id)
    return payable


@router.post("/contas-pagar", response_model=AccountsPayableRead)
def create_payable(
    payload: AccountsPayableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsPayable:
    service = _service(db)
    payable = service.create_payable(current_user.tenant_id, payload.model_dump())
    db.commit()
    db.refresh(payable)
    return payable


@router.put("/contas-pagar/{payable_id}", response_model=AccountsPayableRead)
def update_payable(
    payable_id: int,
    payload: AccountsPayableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsPayable:
    payable = db.get(AccountsPayable, payable_id)
    _ensure_owner(payable, current_user.tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(payable, field, value)
    FinanceService(db)._update_payable_status(payable)
    db.commit()
    db.refresh(payable)
    return payable


@router.post("/contas-pagar/{payable_id}/baixa", response_model=AccountsPayableRead)
def settle_payable(
    payable_id: int,
    payload: SettlementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountsPayable:
    payable = db.get(AccountsPayable, payable_id)
    _ensure_owner(payable, current_user.tenant_id)
    service = _service(db)
    service.register_payable_payment(payable, payload.paid_amount, payload.notes)
    db.commit()
    db.refresh(payable)
    return payable


@router.delete("/contas-pagar/{payable_id}")
def delete_payable(payable_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, str]:
    payable = db.get(AccountsPayable, payable_id)
    _ensure_owner(payable, current_user.tenant_id)
    db.delete(payable)
    db.commit()
    return {"detail": "Conta a pagar removida com sucesso"}


@router.get("/boletos", response_model=list[BoletoRead])
def list_boletos(
    q: str | None = None,
    status_filter: StatusBoleto | None = None,
    bank_code: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Boleto]:
    query = db.query(Boleto).filter(Boleto.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Boleto.nosso_numero.ilike(term), Boleto.barcode.ilike(term)))
    if status_filter is not None:
        query = query.filter(Boleto.status == status_filter)
    if bank_code:
        query = query.filter(Boleto.bank_code == bank_code)
    return query.order_by(Boleto.due_date.desc(), Boleto.id.desc()).offset(skip).limit(limit).all()


@router.get("/boletos/{boleto_id}", response_model=BoletoRead)
def get_boleto(boleto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Boleto:
    boleto = db.get(Boleto, boleto_id)
    _ensure_owner(boleto, current_user.tenant_id)
    return boleto


@router.post("/boletos", response_model=BoletoRead)
def create_boleto(
    payload: BoletoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Boleto:
    service = _service(db)
    try:
        boleto = service.create_boleto(current_user.tenant_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    db.refresh(boleto)
    return boleto


@router.put("/boletos/{boleto_id}", response_model=BoletoRead)
def update_boleto(
    boleto_id: int,
    payload: BoletoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Boleto:
    boleto = db.get(Boleto, boleto_id)
    _ensure_owner(boleto, current_user.tenant_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(boleto, field, value)
    db.commit()
    db.refresh(boleto)
    return boleto


@router.post("/boletos/{boleto_id}/enviar", response_model=BoletoRead)
def send_boleto(boleto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Boleto:
    boleto = db.get(Boleto, boleto_id)
    _ensure_owner(boleto, current_user.tenant_id)
    boleto.status = StatusBoleto.ENVIADO
    db.commit()
    db.refresh(boleto)
    return boleto


@router.post("/boletos/{boleto_id}/baixar", response_model=BoletoRead)
def settle_boleto(boleto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Boleto:
    boleto = db.get(Boleto, boleto_id)
    _ensure_owner(boleto, current_user.tenant_id)
    boleto.status = StatusBoleto.PAGO
    if boleto.receivable_id:
        receivable = db.get(AccountsReceivable, boleto.receivable_id)
        if receivable:
            FinanceService(db).register_receivable_payment(receivable, boleto.amount, "Baixa via boleto")
    if boleto.payable_id:
        payable = db.get(AccountsPayable, boleto.payable_id)
        if payable:
            FinanceService(db).register_payable_payment(payable, boleto.amount, "Baixa via boleto")
    db.commit()
    db.refresh(boleto)
    return boleto


@router.delete("/boletos/{boleto_id}")
def delete_boleto(boleto_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, str]:
    boleto = db.get(Boleto, boleto_id)
    _ensure_owner(boleto, current_user.tenant_id)
    db.delete(boleto)
    db.commit()
    return {"detail": "Boleto removido com sucesso"}


@router.get("/remessas", response_model=list[RemittanceRead])
def list_remittances(
    status_filter: StatusRemessa | None = None,
    bank_code: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Remittance]:
    query = db.query(Remittance).filter(Remittance.tenant_id == current_user.tenant_id)
    if status_filter:
        query = query.filter(Remittance.status == status_filter)
    if bank_code:
        query = query.filter(Remittance.bank_code == bank_code)
    return query.order_by(Remittance.generated_at.desc(), Remittance.id.desc()).offset(skip).limit(limit).all()


@router.post("/remessas", response_model=RemittanceRead)
def create_remittance(
    payload: RemittanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Remittance:
    service = _service(db)
    remittance = service.generate_remittance(current_user.tenant_id, payload.model_dump(exclude={"boleto_ids"}), payload.boleto_ids)
    db.commit()
    db.refresh(remittance)
    return remittance


@router.post("/conciliacao/importar", response_model=list[BankStatementEntryRead])
def import_conciliation(
    payload: BankStatementImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BankReconciliationEntry]:
    service = _service(db)
    entries = service.import_bank_entries(
        current_user.tenant_id,
        [item.model_dump() for item in payload.entries],
        payload.auto_match,
    )
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return entries


@router.get("/conciliacao", response_model=list[BankStatementEntryRead])
def list_conciliation(
    status_filter: StatusConciliacao | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BankReconciliationEntry]:
    query = db.query(BankReconciliationEntry).filter(BankReconciliationEntry.tenant_id == current_user.tenant_id)
    if status_filter is not None:
        query = query.filter(BankReconciliationEntry.status == status_filter)
    return query.order_by(BankReconciliationEntry.statement_date.desc(), BankReconciliationEntry.id.desc()).offset(skip).limit(limit).all()


@router.post("/faturamento/gerar", response_model=BillingGenerationResponse)
def generate_billing(
    payload: BillingGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingGenerationResponse:
    service = _service(db)
    items, total_amount = service.generate_billing_for_competence(
        current_user.tenant_id,
        payload.competence,
        payload.issue_date,
        payload.due_date,
        payload.bank_code,
        payload.description_prefix,
        payload.generate_boleto,
    )
    db.commit()
    return BillingGenerationResponse(
        competence=payload.competence,
        total_amount=total_amount,
        items=[item.__dict__ for item in items],
    )


@router.get("/inadimplencia/aging", response_model=AgingResponse)
def aging_report(
    as_of: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgingResponse:
    as_of = as_of or date.today()
    receivables = db.query(AccountsReceivable).filter(
        AccountsReceivable.tenant_id == current_user.tenant_id,
        AccountsReceivable.status != StatusTitulo.PAGO,
    ).all()
    payables = db.query(AccountsPayable).filter(
        AccountsPayable.tenant_id == current_user.tenant_id,
        AccountsPayable.status != StatusTitulo.PAGO,
    ).all()

    buckets = [
        ("0-30", 0, 30),
        ("31-60", 31, 60),
        ("61-90", 61, 90),
        ("90+", 91, 99999),
    ]

    def build(entries):
        result: list[AgingBucketRead] = []
        for label, min_days, max_days in buckets:
            filtered = []
            for item in entries:
                days = (as_of - item.due_date).days
                if min_days <= days <= max_days:
                    filtered.append(item)
            total = sum((item.original_amount - item.paid_amount for item in filtered), Decimal("0.00"))
            result.append(AgingBucketRead(label=label, count=len(filtered), total=Decimal(str(total)).quantize(Decimal("0.01"))))
        return result

    return AgingResponse(as_of=as_of, receivable_buckets=build(receivables), payable_buckets=build(payables))
