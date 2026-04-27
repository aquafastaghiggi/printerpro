from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDResponse(ORMModel):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

