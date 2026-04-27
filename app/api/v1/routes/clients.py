from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.enums import PessoaTipo
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter()


@router.get("", response_model=list[ClientRead])
def list_clients(
    q: str | None = None,
    document: str | None = None,
    person_type: PessoaTipo | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Client]:
    query = db.query(Client).filter(Client.tenant_id == current_user.tenant_id)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Client.name.ilike(term), Client.document.ilike(term), Client.email.ilike(term)))
    if document:
        query = query.filter(Client.document.ilike(f"%{document}%"))
    if person_type:
        query = query.filter(Client.person_type == person_type)
    return query.order_by(Client.id.desc()).offset(skip).limit(limit).all()


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = db.get(Client, client_id)
    if not client or client.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente nao encontrado")
    return client


@router.post("", response_model=ClientRead)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = Client(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    client = db.get(Client, client_id)
    if not client or client.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente nao encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    client = db.get(Client, client_id)
    if not client or client.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente nao encontrado")
    db.delete(client)
    db.commit()
    return {"detail": "Cliente removido com sucesso"}
