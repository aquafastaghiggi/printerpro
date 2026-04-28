from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/executivo", response_model=DashboardOverviewResponse)
def executive_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DashboardOverviewResponse:
    return DashboardService(db).build_overview(current_user.tenant_id)
