from typing import Any

from pydantic import BaseModel, Field


class CostingSaveRequest(BaseModel):
    title: str = Field(..., min_length=1)
    customer_id: int | None = None
    payload: dict[str, Any]


class CostingListItem(BaseModel):
    id: int
    title: str
    customer_id: int | None = None
    customer_name: str | None = None
    created_at: str
    updated_at: str


class CostingDetail(CostingListItem):
    payload: dict[str, Any]
