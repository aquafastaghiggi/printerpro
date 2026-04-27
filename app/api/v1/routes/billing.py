from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.contract import Contract
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate
from app.services.faturamento import FaturamentoService

router = APIRouter()


class BillingPreviewRequest(BaseModel):
    readings: list[ReadingCreate]


@router.post("/contratos/{contract_id}/preview")
def preview(contract_id: int, payload: BillingPreviewRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = (
        db.query(Contract)
        .options(selectinload(Contract.plan))
        .filter(Contract.id == contract_id, Contract.tenant_id == current_user.tenant_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")

    readings = [Reading(**item.model_dump(), tenant_id=current_user.tenant_id) for item in payload.readings]
    return FaturamentoService().calcular_preview(contract, readings)

